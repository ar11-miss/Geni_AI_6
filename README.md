# MedDevice RAG: Retrieval-Augmented QA for the Medical Device Domain

A Retrieval-Augmented Generation (RAG) application that answers questions about medical device
regulation, standards and manufacturer quality documents. It **compares every answer against the same
LLM without retrieval**. The LLM is served by **Groq** (`openai/gpt-oss-120b` by default).

```
question ──► BM25 retriever ──► top-k passages ──► LLM (with context, must cite [n]) ──► RAG answer
        └──────────────────────────────────────► LLM (no context)                   ──► baseline answer
```

## Document collection (`data/docs/`, 15 documents, 82 chunks)

| Type | Documents |
|---|---|
| Public regulatory knowledge (paraphrased summaries) | FDA classification, 510(k), PMA & De Novo, QMSR / ISO 13485 & design controls, ISO 14971, IEC 62304, EU MDR 2017/745, MDR reporting & recalls (21 CFR 803/806), UDI, cybersecurity (§524B), ISO 10993-1, human factors (IEC 62366 / FDA) |
| Internal company documents (**fictional** "Veridian MedTech") | InfusePro 300 infusion pump IFU, SOP-QA-014 complaint handling, Field Safety Notice FSN-2026-07 |

The fictional internal documents stand in for a manufacturer's private knowledge base. The LLM cannot
have seen them during training, which is where RAG matters most. To use your own collection, drop more
`.md` / `.txt` files into `data/docs/`; they are indexed automatically at start-up.

The regulatory summaries are written for demonstration and are not a substitute for the official texts.

## How it works

| Stage | Implementation (`rag_core.py`) |
|---|---|
| Chunking | Heading-aware: splits on `##` sections, then into chunks of up to 900 characters on sentence boundaries with 150-character overlap. Each chunk keeps its document title and section. |
| Indexing | BM25 (k1 = 1.5, b = 0.75) in pure numpy, with a domain tokenizer that keeps identifiers like `E-401`, `SOP-QA-014`, `510(k)`, `IEC 62304` and applies light stemming |
| Retrieval | Hierarchical BM25: `0.65 × chunk score + 0.35 × parent-document score`, plus query-time acronym expansion (MDR, CAPA, UDI, SBOM, KVO…) |
| Generation (RAG) | Numbered passages go in the prompt; the model must answer only from them, cite `[n]`, and say so when the context is insufficient |
| Generation (baseline) | Same model, same system persona and temperature, no context |
| LLM client | Groq OpenAI-compatible REST API with retry/back-off for rate limits (429) |

## Evaluation (`evaluate.py`)

16 questions (`data/eval_questions.json`): 11 public-regulatory and 5 internal-company. Each has a
reference answer, required key facts and the expected source document.

- **Retrieval:** hit@k and MRR against the expected source document
- **Key-fact recall:** automatic string matching of required facts (numbers, dates, codes) in the answer
- **LLM-as-judge:** a *different* model (`qwen/qwen3.8-27b`) grades each answer blind against the reference:
  correctness 1–5, completeness 1–5, hallucination yes/no, abstained yes/no
- **Cost:** latency and tokens per call

Outputs: `results/eval_report.md` (readable report with all answers side by side) and
`results/eval_results.json` (shown in the web UI's **Evaluation** tab).

## Run it

Requires Python 3.9+ with `numpy` and `requests` (`pip install -r requirements.txt`). `pypdf` is optional.
No other dependencies are needed.

```bash
cp .env.example .env            # then put your Groq key in .env (already done here)

python3 app.py                  # web UI → http://127.0.0.1:8501 (next free port if busy)
python3 ask.py "What does error E-401 mean on the InfusePro 300?"   # CLI comparison
python3 evaluate.py             # full evaluation (about 64 API calls, a few minutes on the free tier)
python3 rag_core.py             # retrieval smoke test, no API calls
```

Optional settings in `.env`: `GROQ_MODEL`, `GROQ_JUDGE_MODEL`, `RAG_TOP_K`, `PORT` (default 8501).

## Web app

- **Ask Assistant:** ask a question across all documents, or pick one document under "Search in". The
  RAG answer and the no-retrieval answer appear side by side. Citations such as `[1]` jump to the
  retrieved evidence, and **Open** shows the passage highlighted inside its document.
- **Document Library:** every document, with type, category, pages, passages and size. Filter by
  category, search titles, view documents in a side panel (PDFs show the original or the extracted
  text), click **Ask** to question one document, or delete your uploads.
- **Upload:** drag and drop PDF, DOCX, TXT, Markdown or HTML files (up to 30 MB). They are indexed
  immediately. Uploaded files are stored in `data/uploads/`. Try `samples/Aeris_V9_Quick_Guide_FICTIONAL.pdf`.
- **Evaluation:** the benchmark dashboard.
- Direct links: `#library`, `#eval`, `#doc=<id>`, `#ask=<question>`.

PDF text extraction uses `pypdf` if it is installed. Otherwise it uses macOS's built-in PDFKit via
`tools/pdf2text.swift`, which is compiled automatically on first use. Scanned image-only PDFs need OCR first.

## Project layout

```
rag_core.py              chunking, BM25 retriever, Groq client, RAG and baseline answering
documents.py             document store: library + uploads, PDF/DOCX/HTML text extraction
app.py                   web server (standard library) + JSON API (ask, upload, documents, files)
static/index.html        UI: assistant, document library + viewer, evaluation dashboard
ask.py                   CLI
evaluate.py              RAG vs. no-RAG benchmark → results/ (built-in library only, for reproducibility)
data/docs/               built-in document collection
data/uploads/            your uploaded documents
data/eval_questions.json evaluation set
tools/pdf2text.swift     PDFKit text extractor (macOS fallback when pypdf is not installed)
```

## Limitations and possible extensions

- BM25 is lexical, so heavily paraphrased or jargon-only questions can miss. Adding dense embeddings
  (hybrid retrieval) and a cross-encoder re-ranker would improve recall.
- Key-fact recall is string-based and can under-count correct paraphrases. The LLM judge compensates,
  but it is itself a model with its own errors.
- The 16-question set is small. Treat the numbers as indicative rather than statistically conclusive.
