"""
Compare RAG vs. no-retrieval (baseline) answers on the evaluation set.

Metrics
-------
Retrieval     hit@k  (was an expected source document retrieved?)  and  MRR
Key-fact recall      fraction of expected key facts present in the answer (string match, automatic)
LLM-as-judge         a *different* model scores each answer blind (it is not told which system wrote it)
                     against the reference answer: correctness 1-5, completeness 1-5, hallucination y/n
Abstention           whether the model declined / said it did not know
Cost                 latency and total tokens

Usage:  python3 evaluate.py            (all questions)
        python3 evaluate.py --limit 3  (quick run)
Outputs: results/eval_results.json and results/eval_report.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import time

from rag_core import JUDGE_MODEL, ROOT, TOP_K, LLMError, RAGPipeline, chat

RESULTS_DIR = os.path.join(ROOT, "results")
QUESTIONS = os.path.join(ROOT, "data", "eval_questions.json")

JUDGE_PROMPT = """You are a strict grader for a medical device regulatory question-answering system.
Compare the CANDIDATE answer with the REFERENCE answer (the reference is the ground truth from the
organisation's document collection; treat it as correct even if it describes a fictional company).

QUESTION: {question}

REFERENCE ANSWER: {reference}

CANDIDATE ANSWER: {candidate}

Score the candidate:
- correctness (1-5): 5 = all stated facts agree with the reference; 1 = mostly wrong or no real answer.
- completeness (1-5): 5 = covers every key point of the reference; 1 = covers none.
- hallucination (true/false): true if the candidate asserts specific facts (numbers, dates, codes, names,
  procedures) that contradict the reference or are invented. Saying "I don't know" is NOT hallucination.
- abstained (true/false): true if the candidate declines to answer or says it lacks the information.

Return only JSON: {{"correctness": int, "completeness": int, "hallucination": bool, "abstained": bool,
"rationale": "one sentence"}}"""

ABSTAIN_RE = re.compile(r"(do not (have|contain)|don't have|not (available|contain|provided)|"
                        r"no (information|publicly available)|i('m| am) not aware|unable to (find|provide)|"
                        r"not (publicly )?(documented|known)|cannot (find|provide|determine))", re.I)


def normalize(text: str) -> str:
    text = text.lower()
    for ch in "‐‑‒–—−":
        text = text.replace(ch, "-")
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace(" ", " ").replace(" ", " ").replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", text)


def key_fact_recall(answer: str, key_facts: list[list[str]]) -> tuple[float, list[bool]]:
    norm = normalize(answer)
    found = [any(normalize(alt) in norm for alt in alts) for alts in key_facts]
    return (sum(found) / len(found) if found else 0.0), found


def judge(question: str, reference: str, candidate: str) -> dict:
    prompt = JUDGE_PROMPT.format(question=question, reference=reference, candidate=candidate)
    try:
        out = chat([{"role": "user", "content": prompt}], model=JUDGE_MODEL, temperature=0.0,
                   max_tokens=2000, json_mode=True)
        data = json.loads(out["content"])
        return {"correctness": int(data.get("correctness", 0)), "completeness": int(data.get("completeness", 0)),
                "hallucination": bool(data.get("hallucination", False)),
                "abstained": bool(data.get("abstained", False)), "rationale": str(data.get("rationale", ""))}
    except (LLMError, json.JSONDecodeError, ValueError, TypeError) as exc:
        return {"correctness": None, "completeness": None, "hallucination": None, "abstained": None,
                "rationale": f"judge error: {exc}"}


def score_answer(ans, item) -> dict:
    recall, found = key_fact_recall(ans.answer, item["key_facts"])
    j = judge(item["question"], item["reference_answer"], ans.answer)
    if j["abstained"] is None:
        j["abstained"] = bool(ABSTAIN_RE.search(ans.answer))
    return {"answer": ans.answer, "latency_s": ans.latency_s,
            "total_tokens": ans.usage.get("total_tokens", 0),
            "key_fact_recall": round(recall, 3), "key_facts_found": found, "judge": j}


def summarize(rows: list[dict], system: str) -> dict:
    def avg(vals):
        vals = [v for v in vals if v is not None]
        return round(statistics.mean(vals), 3) if vals else None
    s = [r[system] for r in rows]
    return {"n": len(s),
            "key_fact_recall": avg([x["key_fact_recall"] for x in s]),
            "correctness": avg([x["judge"]["correctness"] for x in s]),
            "completeness": avg([x["judge"]["completeness"] for x in s]),
            "hallucination_rate": avg([float(x["judge"]["hallucination"]) for x in s
                                       if x["judge"]["hallucination"] is not None]),
            "abstention_rate": avg([float(x["judge"]["abstained"]) for x in s]),
            "avg_latency_s": avg([x["latency_s"] for x in s]),
            "avg_tokens": avg([x["total_tokens"] for x in s])}


def write_report(payload: dict, path: str) -> None:
    rows, summ = payload["rows"], payload["summary"]
    lines = ["# RAG vs. No-Retrieval Evaluation Report", "",
             f"*Generated {payload['timestamp']} · generator `{payload['generator_model']}` · "
             f"judge `{payload['judge_model']}` · top-k = {payload['top_k']} · "
             f"{payload['corpus']['num_documents']} documents / {payload['corpus']['num_chunks']} chunks*", "",
             "## Retrieval quality", "",
             f"- hit@{payload['top_k']}: **{payload['retrieval']['hit_at_k']:.0%}**",
             f"- MRR: **{payload['retrieval']['mrr']:.3f}**", ""]
    metrics = [("Key-fact recall", "key_fact_recall", "{:.0%}"), ("Judge correctness (1-5)", "correctness", "{:.2f}"),
               ("Judge completeness (1-5)", "completeness", "{:.2f}"),
               ("Hallucination rate", "hallucination_rate", "{:.0%}"), ("Abstention rate", "abstention_rate", "{:.0%}"),
               ("Avg latency (s)", "avg_latency_s", "{:.2f}"), ("Avg tokens / call", "avg_tokens", "{:.0f}")]
    fmt = lambda v, f: "n/a" if v is None else f.format(v)
    for scope in ["overall", "public-regulatory", "internal-company"]:
        if not summ[scope]["rag"]:
            continue
        lines += [f"## Answer quality – {scope}", "", "| Metric | With RAG | Without RAG |", "|---|---|---|"]
        for label, key, f in metrics:
            lines.append(f"| {label} | {fmt(summ[scope]['rag'][key], f)} | {fmt(summ[scope]['baseline'][key], f)} |")
        lines.append("")
    lines += ["## Per-question results", "",
              "| ID | Category | Hit | Recall RAG | Recall base | Correct RAG | Correct base | Halluc. RAG | Halluc. base |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['id']} | {r['category']} | {'✓' if r['retrieval_hit'] else '✗'} | "
                     f"{r['rag']['key_fact_recall']:.0%} | {r['baseline']['key_fact_recall']:.0%} | "
                     f"{r['rag']['judge']['correctness']} | {r['baseline']['judge']['correctness']} | "
                     f"{'yes' if r['rag']['judge']['hallucination'] else 'no'} | "
                     f"{'yes' if r['baseline']['judge']['hallucination'] else 'no'} |")
    lines += ["", "## Answers side by side", ""]
    for r in rows:
        lines += [f"### {r['id']}. {r['question']}", "", f"**Reference:** {r['reference_answer']}", "",
                  f"**Retrieved:** " + ", ".join(f"`{d}`" for d in r["retrieved_docs"]), "",
                  f"**With RAG** (recall {r['rag']['key_fact_recall']:.0%}, judge {r['rag']['judge']['correctness']}/5):",
                  "", "> " + r["rag"]["answer"].replace("\n", "\n> "), "",
                  f"**Without RAG** (recall {r['baseline']['key_fact_recall']:.0%}, judge "
                  f"{r['baseline']['judge']['correctness']}/5):", "",
                  "> " + r["baseline"]["answer"].replace("\n", "\n> "), "",
                  f"*Judge notes – RAG:* {r['rag']['judge']['rationale']}  ",
                  f"*Judge notes – baseline:* {r['baseline']['judge']['rationale']}", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def build_payload(rows: list[dict], rag_model: str, top_k: int, corpus: dict) -> dict:
    summary = {}
    for scope in ["overall", "public-regulatory", "internal-company"]:
        sub = rows if scope == "overall" else [r for r in rows if r["category"] == scope]
        summary[scope] = {"rag": summarize(sub, "rag") if sub else {},
                          "baseline": summarize(sub, "baseline") if sub else {}}
    return {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "generator_model": rag_model,
            "judge_model": JUDGE_MODEL, "top_k": top_k, "corpus": corpus,
            "retrieval": {"hit_at_k": statistics.mean(r["retrieval_hit"] for r in rows),
                          "mrr": statistics.mean(r["reciprocal_rank"] for r in rows)},
            "summary": summary, "rows": rows}


def save(payload: dict) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "eval_results.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    write_report(payload, os.path.join(RESULTS_DIR, "eval_report.md"))
    summary = payload["summary"]
    print("\n=== Summary (overall) ===")
    print(f"retrieval hit@{payload['top_k']}={payload['retrieval']['hit_at_k']:.0%}  "
          f"MRR={payload['retrieval']['mrr']:.3f}")
    for k in ["key_fact_recall", "correctness", "completeness", "hallucination_rate", "abstention_rate",
              "avg_latency_s"]:
        print(f"{k:20s} RAG={summary['overall']['rag'][k]!s:8s} baseline={summary['overall']['baseline'][k]!s}")
    print("\nWrote results/eval_results.json and results/eval_report.md")


def rejudge() -> None:
    with open(os.path.join(RESULTS_DIR, "eval_results.json"), encoding="utf-8") as fh:
        payload = json.load(fh)
    for row in payload["rows"]:
        for system in ("rag", "baseline"):
            if row[system]["judge"]["correctness"] is None:
                print(f"re-judging {row['id']} / {system}")
                j = judge(row["question"], row["reference_answer"], row[system]["answer"])
                if j["abstained"] is None:
                    j["abstained"] = bool(ABSTAIN_RE.search(row[system]["answer"]))
                row[system]["judge"] = j
    save(build_payload(payload["rows"], payload["generator_model"], payload["top_k"], payload["corpus"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--top-k", type=int, default=None)
    ap.add_argument("--rejudge", action="store_true",
                    help="re-run only failed judge calls on the saved results, then rebuild the report")
    args = ap.parse_args()
    if args.rejudge:
        return rejudge()

    # evaluation uses only the fixed built-in library so results are reproducible
    rag = RAGPipeline(top_k=args.top_k or TOP_K, include_uploads=False)
    with open(QUESTIONS, encoding="utf-8") as fh:
        items = json.load(fh)[: args.limit]

    rows = []
    for n, item in enumerate(items, 1):
        print(f"[{n}/{len(items)}] {item['id']} {item['question'][:70]}...", flush=True)
        rag_ans = rag.answer_with_rag(item["question"])
        base_ans = rag.answer_without_rag(item["question"])
        retrieved_docs = [s["doc_id"] for s in rag_ans.sources]
        ranks = [i for i, d in enumerate(retrieved_docs, 1) if d in item["source_docs"]]
        row = {"id": item["id"], "category": item["category"], "question": item["question"],
               "reference_answer": item["reference_answer"], "source_docs": item["source_docs"],
               "retrieved_docs": retrieved_docs, "retrieval_hit": bool(ranks),
               "reciprocal_rank": 1 / ranks[0] if ranks else 0.0,
               "sources": rag_ans.sources,
               "rag": score_answer(rag_ans, item), "baseline": score_answer(base_ans, item)}
        rows.append(row)
        print(f"      hit={row['retrieval_hit']}  recall rag={row['rag']['key_fact_recall']:.0%} "
              f"base={row['baseline']['key_fact_recall']:.0%}  judge rag={row['rag']['judge']['correctness']} "
              f"base={row['baseline']['judge']['correctness']}", flush=True)

    corpus = {k: v for k, v in rag.stats().items() if k != "documents"}
    save(build_payload(rows, rag.model, rag.top_k, corpus))


if __name__ == "__main__":
    main()
