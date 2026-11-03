"""
Document store: the built-in library (data/docs/) plus user uploads (data/uploads/).

Supported formats: PDF, DOCX, Markdown, plain text, HTML.
PDF text extraction uses `pypdf` if it is installed, otherwise Apple's built-in PDFKit via the small
Swift helper in tools/pdf2text.swift (compiled automatically on first use, macOS only).
"""
from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import time
import zipfile
from dataclasses import dataclass, asdict

ROOT = os.path.dirname(os.path.abspath(__file__))
LIBRARY_DIR = os.path.join(ROOT, "data", "docs")
UPLOAD_DIR = os.path.join(ROOT, "data", "uploads")
CACHE_DIR = os.path.join(UPLOAD_DIR, ".text_cache")
TOOLS_DIR = os.path.join(ROOT, "tools")

SUPPORTED = {".pdf": "pdf", ".docx": "docx", ".md": "md", ".markdown": "md", ".txt": "txt",
             ".html": "html", ".htm": "html"}
MAX_UPLOAD_BYTES = 30 * 1024 * 1024
PAGE_BREAK = "\f"


class DocumentError(ValueError):
    pass


@dataclass
class Document:
    id: str              # stable id (file stem)
    filename: str
    title: str
    kind: str            # pdf | docx | md | txt | html
    source: str          # "library" or "uploaded"
    category: str        # FDA | EU MDR | Standards | Internal | Uploaded
    path: str
    size_bytes: int
    pages: int           # PDF pages (0 for other formats)
    added: float
    text: str = ""       # extracted text (PDF pages separated by \f)

    def meta(self) -> dict:
        d = asdict(self)
        d.pop("text"); d.pop("path")
        d["chars"] = len(self.text)
        return d


# ------------------------------------------------------------------------------------------
# Text extraction
# ------------------------------------------------------------------------------------------
def _pdf_text(path: str) -> str:
    try:  # preferred, cross-platform
        from pypdf import PdfReader  # type: ignore
        return PAGE_BREAK.join((p.extract_text() or "") for p in PdfReader(path).pages)
    except ImportError:
        pass
    binary = os.path.join(TOOLS_DIR, "pdf2text")
    source = os.path.join(TOOLS_DIR, "pdf2text.swift")
    if not os.path.exists(binary):
        if not shutil.which("swiftc"):
            raise DocumentError("PDF support needs `pip install pypdf` (or macOS with Swift).")
        subprocess.run(["swiftc", "-O", source, "-o", binary], check=True, capture_output=True, timeout=300)
    out = subprocess.run([binary, path], capture_output=True, timeout=120)
    if out.returncode != 0:
        raise DocumentError("Could not read this PDF (it may be encrypted or damaged).")
    return out.stdout.decode("utf-8", errors="replace").rstrip("\n")


def _docx_text(path: str) -> str:
    try:
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
    except (zipfile.BadZipFile, KeyError) as exc:
        raise DocumentError("Not a valid .docx file.") from exc
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    # keep heading paragraphs recognisable as markdown headings
    xml = re.sub(r"<w:p[ >](?:(?!</w:p>).)*?<w:pStyle w:val=\"(?:Heading|heading)\s?1\"",
                 lambda m: "\n# " + m.group(0), xml, flags=re.S)
    xml = re.sub(r"<w:p[ >](?:(?!</w:p>).)*?<w:pStyle w:val=\"(?:Heading|heading)\s?[2-3]\"",
                 lambda m: "\n## " + m.group(0), xml, flags=re.S)
    xml = xml.replace("</w:p>", "\n")
    text = html.unescape(re.sub(r"<[^>]+>", "", xml))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _html_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", raw)
    raw = re.sub(r"(?i)<h1[^>]*>", "\n# ", raw)
    raw = re.sub(r"(?i)<h[23][^>]*>", "\n## ", raw)
    raw = re.sub(r"(?i)</(p|div|li|h\d|tr|br)\s*>|<br\s*/?>", "\n", raw)
    return re.sub(r"\n{3,}", "\n\n", html.unescape(re.sub(r"<[^>]+>", "", raw))).strip()


def extract_text(path: str, kind: str) -> str:
    if kind == "pdf":
        return _pdf_text(path)
    if kind == "docx":
        return _docx_text(path)
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    return _html_text(raw) if kind == "html" else raw


# ------------------------------------------------------------------------------------------
# Metadata helpers
# ------------------------------------------------------------------------------------------
def _guess_title(text: str, kind: str, filename: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, flags=re.M)
    if m:
        return m.group(1).strip()
    if kind in ("pdf", "docx", "txt", "html"):
        for line in text.splitlines():
            line = line.strip()
            if 8 <= len(line) <= 120 and re.search(r"[A-Za-z]{3}", line):
                return line
    stem = os.path.splitext(filename)[0]
    return re.sub(r"[_\-]+", " ", re.sub(r"^\d+_", "", stem)).strip().title()


def _category(doc_id: str, title: str, source: str) -> str:
    t = f"{doc_id} {title}".lower()
    if "veridian" in t:
        return "Internal"
    if source == "uploaded":
        return "Uploaded"
    if "eu " in t or "2017/745" in t or "eu_mdr" in t:
        return "EU MDR"
    if re.search(r"\b(iso|iec)\b|iso\d|iec\d", t):
        return "Standards"
    return "FDA"


def safe_filename(name: str) -> str:
    name = os.path.basename(name.replace("\\", "/")).strip()
    stem, ext = os.path.splitext(name)
    stem = re.sub(r"[^A-Za-z0-9._ -]+", "", stem).strip(" .")[:80] or "document"
    stem = re.sub(r"\s+", "_", stem)
    return stem + ext.lower()


# ------------------------------------------------------------------------------------------
# Store
# ------------------------------------------------------------------------------------------
class DocumentStore:
    def __init__(self, include_uploads: bool = True):
        self.include_uploads = include_uploads
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        self.docs: dict[str, Document] = {}
        self.reload()

    def reload(self) -> None:
        self.docs = {}
        dirs = [(LIBRARY_DIR, "library")] + ([(UPLOAD_DIR, "uploaded")] if self.include_uploads else [])
        for folder, source in dirs:
            for name in sorted(os.listdir(folder)):
                path = os.path.join(folder, name)
                kind = SUPPORTED.get(os.path.splitext(name)[1].lower())
                if not kind or not os.path.isfile(path) or name.startswith("."):
                    continue
                try:
                    self._load(path, kind, source)
                except DocumentError as exc:
                    print(f"[documents] skipped {name}: {exc}")

    def _load(self, path: str, kind: str, source: str) -> Document:
        filename = os.path.basename(path)
        doc_id = os.path.splitext(filename)[0]
        if doc_id in self.docs:                       # e.g. same stem, different extension
            doc_id = f"{doc_id}-{kind}"
        text = self._cached_text(path, kind) if source == "uploaded" else extract_text(path, kind)
        title = _guess_title(text, kind, filename)
        st = os.stat(path)
        doc = Document(doc_id, filename, title, kind, source, _category(doc_id, title, source), path,
                       st.st_size, text.count(PAGE_BREAK) + 1 if kind == "pdf" else 0, st.st_mtime, text)
        self.docs[doc_id] = doc
        return doc

    def _cached_text(self, path: str, kind: str) -> str:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache = os.path.join(CACHE_DIR, os.path.basename(path) + ".txt")
        if os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(path):
            with open(cache, encoding="utf-8") as fh:
                return fh.read()
        text = extract_text(path, kind)
        with open(cache, "w", encoding="utf-8") as fh:
            fh.write(text)
        return text

    # -- public API -------------------------------------------------------------------------
    def list(self) -> list[Document]:
        return sorted(self.docs.values(), key=lambda d: (d.source != "uploaded", -d.added if d.source == "uploaded" else 0, d.id))

    def get(self, doc_id: str) -> Document | None:
        return self.docs.get(doc_id)

    def add_upload(self, filename: str, data: bytes) -> Document:
        if not data:
            raise DocumentError("The file is empty.")
        if len(data) > MAX_UPLOAD_BYTES:
            raise DocumentError(f"File is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")
        name = safe_filename(filename)
        kind = SUPPORTED.get(os.path.splitext(name)[1])
        if not kind:
            raise DocumentError("Unsupported file type. Use PDF, DOCX, TXT, MD or HTML.")
        if kind == "pdf" and not data.startswith(b"%PDF"):
            raise DocumentError("This does not look like a valid PDF file.")
        stem, ext = os.path.splitext(name)
        n, final = 1, name
        while os.path.exists(os.path.join(UPLOAD_DIR, final)) or os.path.splitext(final)[0] in self.docs:
            n += 1
            final = f"{stem}-{n}{ext}"
        path = os.path.join(UPLOAD_DIR, final)
        with open(path, "wb") as fh:
            fh.write(data)
        try:
            doc = self._load(path, kind, "uploaded")
        except Exception:
            os.remove(path)
            raise
        if len(re.sub(r"\s", "", doc.text)) < 20:
            self.delete(doc.id)
            raise DocumentError("No readable text found. Scanned/image-only PDFs need OCR first.")
        doc.added = time.time()
        return doc

    def delete(self, doc_id: str) -> None:
        doc = self.docs.get(doc_id)
        if not doc:
            raise DocumentError("Document not found.")
        if doc.source != "uploaded":
            raise DocumentError("Built-in library documents cannot be deleted.")
        for p in (doc.path, os.path.join(CACHE_DIR, doc.filename + ".txt")):
            if os.path.exists(p):
                os.remove(p)
        del self.docs[doc_id]
