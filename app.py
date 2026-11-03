"""
Web UI for the Medical Device RAG assistant (standard library only).

    python3 app.py            -> http://127.0.0.1:8501  (next free port if busy)

Endpoints
  GET    /                        single-page UI (static/index.html)
  GET    /api/stats               corpus statistics
  GET    /api/documents           list all documents (library + uploaded)
  GET    /api/documents/<id>      one document's metadata + extracted text
  DELETE /api/documents/<id>      delete an uploaded document (re-indexes)
  GET    /files/<id>              original file (PDFs open inline in the browser)
  POST   /api/upload              raw file body, header X-Filename: <url-encoded name>  (re-indexes)
  POST   /api/ask                 {"question", "top_k", "doc_ids": [..] optional} -> RAG + baseline answers
  GET    /api/eval                latest evaluation results, if present
"""
from __future__ import annotations

import json
import mimetypes
import os
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from documents import MAX_UPLOAD_BYTES, DocumentError
from rag_core import ROOT, LLMError, RAGPipeline

STATIC = os.path.join(ROOT, "static")
RESULTS = os.path.join(ROOT, "results", "eval_results.json")
PIPELINE = RAGPipeline()
POOL = ThreadPoolExecutor(max_workers=8)
CONTENT_TYPES = {"pdf": "application/pdf", "md": "text/plain; charset=utf-8", "txt": "text/plain; charset=utf-8",
                 "html": "text/plain; charset=utf-8",
                 "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}


def doc_meta(doc) -> dict:
    m = doc.meta()
    m["chunks"] = PIPELINE.chunk_count(doc.id)
    return m


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str = "application/json", extra: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _body(self, limit: int) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        if length > limit:
            raise DocumentError(f"Request too large (limit {limit // (1024 * 1024)} MB).")
        return self.rfile.read(length) if length else b""

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

    # ---------------------------------------------------------------------------- GET
    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/index.html"):
            with open(os.path.join(STATIC, "index.html"), "rb") as fh:
                return self._send(200, fh.read(), "text/html; charset=utf-8")
        if path.startswith("/static/"):
            fp = os.path.realpath(os.path.join(STATIC, path[len("/static/"):]))
            if fp.startswith(STATIC + os.sep) and os.path.isfile(fp):
                with open(fp, "rb") as fh:
                    return self._send(200, fh.read(), mimetypes.guess_type(fp)[0] or "application/octet-stream")
            return self._json(404, {"error": "not found"})
        if path == "/api/stats":
            return self._json(200, PIPELINE.stats())
        if path == "/api/documents":
            return self._json(200, {"documents": [doc_meta(d) for d in PIPELINE.store.list()]})
        if path.startswith("/api/documents/"):
            doc = PIPELINE.store.get(path.rsplit("/", 1)[1])
            if not doc:
                return self._json(404, {"error": "Document not found"})
            return self._json(200, {**doc_meta(doc), "text": doc.text})
        if path.startswith("/files/"):
            doc = PIPELINE.store.get(path.rsplit("/", 1)[1])
            if not doc or not os.path.isfile(doc.path):
                return self._json(404, {"error": "File not found"})
            with open(doc.path, "rb") as fh:
                data = fh.read()
            disp = "inline" if doc.kind in ("pdf", "md", "txt") else "attachment"
            return self._send(200, data, CONTENT_TYPES.get(doc.kind, "application/octet-stream"),
                              {"Content-Disposition": f'{disp}; filename="{doc.filename}"'})
        if path == "/api/eval":
            if not os.path.exists(RESULTS):
                return self._json(404, {"error": "No evaluation results yet. Run: python3 evaluate.py"})
            with open(RESULTS, "rb") as fh:
                return self._send(200, fh.read())
        return self._json(404, {"error": "not found"})

    # ---------------------------------------------------------------------------- POST
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/upload":
                return self._upload()
            if path == "/api/ask":
                return self._ask()
        except DocumentError as exc:
            return self._json(400, {"error": str(exc)})
        except LLMError as exc:
            return self._json(502, {"error": str(exc)})
        except Exception as exc:  # never leave the browser with a bare 500
            return self._json(500, {"error": f"Unexpected server error: {exc}"})
        return self._json(404, {"error": "not found"})

    def _upload(self):
        filename = unquote(self.headers.get("X-Filename", "")).strip()
        if not filename:
            raise DocumentError("Missing file name.")
        doc = PIPELINE.add_document(filename, self._body(MAX_UPLOAD_BYTES))
        return self._json(200, {"document": doc_meta(doc), "stats": PIPELINE.stats()})

    def _ask(self):
        try:
            body = json.loads(self._body(1024 * 1024) or b"{}")
            question = str(body.get("question", "")).strip()
            top_k = max(1, min(int(body.get("top_k", PIPELINE.top_k)), 10))
            doc_ids = [str(d) for d in (body.get("doc_ids") or []) if PIPELINE.store.get(str(d))]
        except (ValueError, TypeError, json.JSONDecodeError):
            raise DocumentError("Invalid request body.")
        if not question:
            raise DocumentError("Please enter a question.")
        rag_f = POOL.submit(PIPELINE.answer_with_rag, question, top_k, doc_ids or None)
        base_f = POOL.submit(PIPELINE.answer_without_rag, question)
        rag, base = rag_f.result(), base_f.result()
        out_rag = rag.to_dict()
        out_rag.pop("context", None)
        return self._json(200, {"question": question, "doc_ids": doc_ids, "rag": out_rag,
                                "baseline": base.to_dict()})

    # ---------------------------------------------------------------------------- DELETE
    def do_DELETE(self):
        path = unquote(urlparse(self.path).path)
        if not path.startswith("/api/documents/"):
            return self._json(404, {"error": "not found"})
        try:
            PIPELINE.delete_document(path.rsplit("/", 1)[1])
        except DocumentError as exc:
            return self._json(400, {"error": str(exc)})
        return self._json(200, {"ok": True, "stats": PIPELINE.stats()})


def _port_in_use(port: int) -> bool:
    """True if anything (on any interface) already accepts connections on this port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


class _Server(ThreadingHTTPServer):
    allow_reuse_address = False  # never share a port with another app


def main() -> None:
    port = int(os.getenv("PORT", "8501"))
    for candidate in range(port, port + 20):
        if _port_in_use(candidate):
            print(f"Port {candidate} is already used by another program, trying {candidate + 1}...")
            continue
        try:
            server = _Server(("127.0.0.1", candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    else:
        raise SystemExit(f"No free port found in {port}-{port + 19}; set PORT=<number> and retry.")
    s = PIPELINE.stats()
    print(f"Indexed {s['num_documents']} documents into {s['num_chunks']} chunks | model {s['model']}")
    print(f"Open http://127.0.0.1:{port}  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
