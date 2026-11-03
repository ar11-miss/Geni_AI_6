"""
Core RAG engine for the Medical Device Regulatory & Quality assistant.

Pipeline
--------
1. Load documents (PDF, DOCX, MD, TXT, HTML) from data/docs/ and data/uploads/
2. Split them into overlapping, heading-aware chunks
3. Index chunks with BM25 (pure numpy, no external search engine)
4. For a question: retrieve top-k chunks -> build a grounded prompt -> call the LLM (Groq)
5. Baseline: call the same LLM with the same question but WITHOUT retrieved context

Only numpy + requests + the standard library are required.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from collections import Counter
from dataclasses import dataclass, field, asdict

import numpy as np
import requests

from documents import PAGE_BREAK, Document, DocumentStore

ROOT = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------
def load_env(path: str = os.path.join(ROOT, ".env")) -> None:
    """Minimal .env loader (KEY=VALUE lines). Existing env vars take precedence."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEN_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
JUDGE_MODEL = os.getenv("GROQ_JUDGE_MODEL", "qwen/qwen3.8-27b")
TOP_K = int(os.getenv("RAG_TOP_K", "5"))


# --------------------------------------------------------------------------------------
# Documents & chunking
# --------------------------------------------------------------------------------------
@dataclass
class Chunk:
    id: int
    doc_id: str          # file name without extension
    doc_title: str       # H1 of the document
    section: str         # nearest H2 heading
    text: str            # chunk body

    def header(self) -> str:
        return f"{self.doc_title} > {self.section}"


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    """Split text on sentence boundaries into pieces <= max_chars with sentence overlap."""
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?;])\s+|\n(?=- |\d+\. )", text)
    pieces, current = [], ""
    for sent in sentences:
        if current and len(current) + len(sent) + 1 > max_chars:
            pieces.append(current.strip())
            # carry trailing context into the next piece
            tail = current[-overlap:]
            tail = tail[tail.find(" ") + 1:] if " " in tail else tail
            current = tail + " " + sent
        else:
            current = f"{current} {sent}" if current else sent
    if current.strip():
        pieces.append(current.strip())
    return pieces


def chunk_document(doc: Document, start_id: int = 0, max_chars: int = 900, overlap: int = 150) -> list[Chunk]:
    """Heading-aware chunking for Markdown-like text; page-aware chunking for PDFs."""
    text = doc.text
    if doc.kind == "pdf":
        sections = [(f"Page {i}", page) for i, page in enumerate(text.split(PAGE_BREAK), 1)]
    elif re.search(r"^##\s+", text, flags=re.M):
        parts = re.split(r"^##\s+(.+)$", text, flags=re.M)
        sections = [("Introduction", parts[0])] + list(zip(parts[1::2], parts[2::2]))
    else:
        sections = [("", text)]
    chunks: list[Chunk] = []
    for heading, body in sections:
        body = re.sub(r"^#\s+.+$", "", body, flags=re.M)      # drop H1
        body = re.sub(r"^>\s?", "", body, flags=re.M)          # unquote notes
        if doc.kind == "pdf":                                  # re-join hard-wrapped PDF lines
            body = re.sub(r"-\n(?=[a-z])", "", body)
            body = re.sub(r"(?<!\n)\n(?!\n|\s*[-•\d]+[.)]?\s)", " ", body)
        body = body.strip()
        if len(body) < 40:
            continue
        pieces = _split_long(body, max_chars, overlap)
        for n, piece in enumerate(pieces, 1):
            section = heading.strip() or (f"Part {n}" if len(pieces) > 1 else "Full text")
            chunks.append(Chunk(start_id + len(chunks), doc.id, doc.title, section, piece))
    return chunks


def load_chunks(store: DocumentStore) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in store.list():
        chunks.extend(chunk_document(doc, len(chunks)))
    return chunks


# --------------------------------------------------------------------------------------
# BM25 retriever
# --------------------------------------------------------------------------------------
_STOP = set("""a an and are as at be been but by can could do does for from has have how if in into is it
its may must not of on or such that the their then there these this those to under was were what when where
which who whom why will with within would should shall you your i me my we our they them than also any all
each other more most some about after before between both during per""".split())


def _stem(tok: str) -> str:
    """Tiny, *consistent* suffix stripper (cause/causes/caused -> caus, days/day -> day)."""
    if len(tok) <= 3 or not tok.isalpha():
        return tok
    for suf, rep in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")):
        if tok.endswith(suf) and not tok.endswith("ss") and len(tok) - len(suf) >= 3:
            tok = tok[: len(tok) - len(suf)] + rep
            break
    if tok.endswith("e") and len(tok) > 4:
        tok = tok[:-1]
    return tok


# Domain acronyms expanded at query time so "MDR" also matches "Medical Device Reporting", etc.
ACRONYMS = {
    "mdr": "medical device reporting regulation", "510k": "premarket notification",
    "pma": "premarket approval", "capa": "corrective preventive action",
    "udi": "unique device identification identifier", "fsn": "field safety notice",
    "sbom": "software bill materials", "ifu": "instructions use", "qms": "quality management system",
    "qmsr": "quality management system regulation", "soup": "software unknown provenance",
    "psur": "periodic safety update report", "pmcf": "post-market clinical follow-up",
    "kvo": "keep vein open", "vtbi": "volume infused", "fsca": "field safety corrective action",
    "samd": "software medical device", "hf": "human factors usability", "dhf": "design history file",
}


def tokenize(text: str, expand: bool = False) -> list[str]:
    """Lowercase tokens; keep hyphenated identifiers (e.g. 'e-101', 'sop-qa-014') AND their parts."""
    text = text.lower().replace("510(k)", "510k").replace("µl", "ul")
    out: list[str] = []
    for tok in re.findall(r"[a-z0-9]+(?:[-.][a-z0-9]+)*", text):
        tok = tok.strip(".")
        if expand and tok in ACRONYMS:
            out.extend(_stem(t) for t in ACRONYMS[tok].split())
        if "-" in tok or "." in tok:
            out.append(tok)
            out.extend(_stem(p) for p in re.split(r"[-.]", tok) if p and p not in _STOP)
        elif tok not in _STOP:
            out.append(_stem(tok))
    return out


def _bm25_weights(token_lists: list[list[str]], vocab: dict[str, int], k1: float, b: float) -> np.ndarray:
    """Return an (n_docs x vocab) matrix of BM25 term weights; a query score is a sum of columns."""
    tf = np.zeros((len(token_lists), len(vocab)), dtype=np.float32)
    for row, toks in enumerate(token_lists):
        for tok, cnt in Counter(toks).items():
            tf[row, vocab[tok]] = cnt
    doc_len = tf.sum(axis=1)
    avgdl = doc_len.mean() if len(doc_len) else 1.0
    df = (tf > 0).sum(axis=0)
    n = len(token_lists)
    idf = np.log(1 + (n - df + 0.5) / (df + 0.5)).astype(np.float32)
    denom = tf + k1 * (1 - b + b * (doc_len[:, None] / avgdl))
    return (tf * (k1 + 1)) / np.where(denom == 0, 1, denom) * idf[None, :]


class BM25Index:
    """Hierarchical BM25: final score = (1-alpha) * chunk score + alpha * parent-document score.

    The document-level term blends in evidence from the whole source document, which stops short,
    loosely related chunks from other documents outranking the right passage.
    """

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75, alpha: float = 0.35):
        self.chunks, self.alpha = chunks, alpha
        # index title + section + body so headings help matching
        chunk_tokens = [tokenize(f"{c.doc_title} {c.section} {c.section} {c.text}") for c in chunks]
        self.doc_ids = sorted({c.doc_id for c in chunks})
        doc_tokens = [[t for c, toks in zip(chunks, chunk_tokens) if c.doc_id == d for t in toks]
                      for d in self.doc_ids]
        self.vocab = {t: i for i, t in enumerate(sorted({t for toks in chunk_tokens for t in toks}))}
        self.chunk_w = _bm25_weights(chunk_tokens, self.vocab, k1, b)
        self.doc_w = _bm25_weights(doc_tokens, self.vocab, k1, b)
        doc_row = {d: i for i, d in enumerate(self.doc_ids)}
        self.chunk_doc = np.array([doc_row[c.doc_id] for c in chunks])

    def search(self, query: str, k: int = TOP_K, doc_ids: set[str] | None = None) -> list[tuple[Chunk, float]]:
        q_ids = [self.vocab[t] for t in set(tokenize(query, expand=True)) if t in self.vocab]
        if not q_ids or not self.chunks:
            return []
        chunk_s = self.chunk_w[:, q_ids].sum(axis=1)
        doc_s = self.doc_w[:, q_ids].sum(axis=1)
        if doc_ids:  # restrict retrieval to the selected documents
            keep = np.array([c.doc_id in doc_ids for c in self.chunks])
            chunk_s = np.where(keep, chunk_s, 0)
            doc_s = np.where(np.isin(np.arange(len(self.doc_ids)), self.chunk_doc[keep]), doc_s, 0)
        if chunk_s.max() <= 0:
            return []
        scores = (1 - self.alpha) * chunk_s / chunk_s.max() + \
            self.alpha * (doc_s / max(doc_s.max(), 1e-9))[self.chunk_doc]
        order = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in order if chunk_s[i] > 0]


# --------------------------------------------------------------------------------------
# Groq LLM client (OpenAI-compatible endpoint)
# --------------------------------------------------------------------------------------
class LLMError(RuntimeError):
    pass


def chat(messages: list[dict], model: str = GEN_MODEL, temperature: float = 0.2,
         max_tokens: int = 2048, json_mode: bool = False, retries: int = 6) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise LLMError("GROQ_API_KEY is not set (put it in .env or the environment).")
    payload = {"model": model, "messages": messages, "temperature": temperature,
               "max_completion_tokens": max_tokens}
    if model.startswith("openai/gpt-oss"):
        payload["reasoning_effort"] = "low"
        payload["include_reasoning"] = False
    if model.startswith("qwen/"):
        payload["reasoning_format"] = "hidden"
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    delay = 2.0
    for attempt in range(retries):
        t0 = time.time()
        try:
            resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=120)
        except requests.RequestException as exc:
            if attempt == retries - 1:
                raise LLMError(f"Network error: {exc}") from exc
            time.sleep(delay); delay *= 2
            continue
        if resp.status_code == 200:
            data = resp.json()
            content = (data["choices"][0]["message"].get("content") or "").strip()
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()
            content = re.sub(r"\u3010(\d+)(?:[^\u3011]*)\u3011", r"[\1]", content)  # 【1†L2】 -> [1]
            return {"content": content, "usage": data.get("usage", {}),
                    "latency_s": round(time.time() - t0, 2), "model": model}
        if resp.status_code in (429, 500, 502, 503) and attempt < retries - 1:
            wait = resp.headers.get("retry-after")
            time.sleep(float(wait) + 0.5 if wait and wait.replace(".", "").isdigit() else delay)
            delay = min(delay * 2, 60)
            continue
        raise LLMError(f"Groq API error {resp.status_code}: {resp.text[:400]}")
    raise LLMError("Groq API: retries exhausted")


# --------------------------------------------------------------------------------------
# Prompts & answer generation
# --------------------------------------------------------------------------------------
SYSTEM_BASE = ("You are an expert assistant for the medical device industry, covering FDA and EU regulations, "
               "international standards (ISO 13485, ISO 14971, IEC 62304, ISO 10993, IEC 62366) and "
               "manufacturer quality procedures. Answer precisely and concisely (under 200 words), "
               "with specific numbers, timelines and clause references where relevant.")

SYSTEM_RAG = SYSTEM_BASE + (
    "\n\nAnswer ONLY using the numbered context passages provided. Cite the passages that support each "
    "statement using square brackets, e.g. [1] or [2][3]. If the context does not contain the information "
    "needed, say clearly that the provided documents do not contain the answer instead of guessing.")

SYSTEM_BASELINE = SYSTEM_BASE + (
    "\n\nAnswer from your own knowledge. If you do not know or are unsure, say so.")


def format_context(hits: list[tuple[Chunk, float]]) -> str:
    return "\n\n".join(f"[{i}] (Source: {c.header()})\n{c.text}" for i, (c, _) in enumerate(hits, 1))


@dataclass
class Answer:
    mode: str
    question: str
    answer: str
    latency_s: float
    model: str
    usage: dict = field(default_factory=dict)
    sources: list[dict] = field(default_factory=list)
    context: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class RAGPipeline:
    """Document store + BM25 index + Groq generation. Thread-safe re-indexing on upload/delete."""

    def __init__(self, top_k: int = TOP_K, model: str = GEN_MODEL, include_uploads: bool = True):
        self.store = DocumentStore(include_uploads=include_uploads)
        self.top_k = top_k
        self.model = model
        self._lock = threading.RLock()
        self._build()

    def _build(self) -> None:
        chunks = load_chunks(self.store)
        index = BM25Index(chunks)
        self.chunks, self.index = chunks, index   # swap together so readers never see a mix

    def add_document(self, filename: str, data: bytes) -> Document:
        with self._lock:
            doc = self.store.add_upload(filename, data)
            self._build()
            return doc

    def delete_document(self, doc_id: str) -> None:
        with self._lock:
            self.store.delete(doc_id)
            self._build()

    def chunk_count(self, doc_id: str) -> int:
        return sum(1 for c in self.chunks if c.doc_id == doc_id)

    def retrieve(self, question: str, k: int | None = None,
                 doc_ids: list[str] | None = None) -> list[tuple[Chunk, float]]:
        return self.index.search(question, k or self.top_k, set(doc_ids) if doc_ids else None)

    def answer_with_rag(self, question: str, k: int | None = None,
                        doc_ids: list[str] | None = None) -> Answer:
        hits = self.retrieve(question, k, doc_ids)
        context = format_context(hits)
        if not hits:
            context = "(no relevant passages were found)"
        messages = [{"role": "system", "content": SYSTEM_RAG},
                    {"role": "user", "content": f"Context passages:\n{context}\n\nQuestion: {question}"}]
        out = chat(messages, model=self.model)
        sources = []
        for i, (c, s) in enumerate(hits, 1):
            doc = self.store.get(c.doc_id)
            sources.append({"rank": i, "doc_id": c.doc_id, "title": c.doc_title, "section": c.section,
                            "kind": doc.kind if doc else "", "category": doc.category if doc else "",
                            "score": round(s, 3), "text": c.text})
        return Answer("rag", question, out["content"], out["latency_s"], out["model"], out["usage"],
                      sources, context)

    def answer_without_rag(self, question: str) -> Answer:
        messages = [{"role": "system", "content": SYSTEM_BASELINE},
                    {"role": "user", "content": question}]
        out = chat(messages, model=self.model)
        return Answer("baseline", question, out["content"], out["latency_s"], out["model"], out["usage"])

    def stats(self) -> dict:
        docs = self.store.list()
        return {"num_documents": len(docs), "num_chunks": len(self.chunks),
                "num_uploaded": sum(d.source == "uploaded" for d in docs),
                "vocab_size": len(self.index.vocab), "model": self.model, "top_k": self.top_k,
                "documents": [{"doc_id": d.id, "title": d.title, "chunks": self.chunk_count(d.id)}
                              for d in docs]}


if __name__ == "__main__":  # quick retrieval smoke test, no LLM call
    rag = RAGPipeline()
    print(json.dumps({k: v for k, v in rag.stats().items() if k != "documents"}, indent=2))
    for q in ["What does error E-401 mean on the InfusePro 300?",
              "How long does a manufacturer have to submit a 30-day MDR?",
              "What are the IEC 62304 software safety classes?"]:
        print("\nQ:", q)
        for c, s in rag.retrieve(q, 3):
            print(f"   {s:6.2f}  {c.header()}")
