"""Command-line comparison:  python3 ask.py "What does error E-401 mean on the InfusePro 300?" """
import sys
import textwrap

from rag_core import RAGPipeline


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or input("Question: ").strip()
    rag = RAGPipeline()
    with_rag = rag.answer_with_rag(question)
    without = rag.answer_without_rag(question)
    bar = "=" * 90
    print(f"\n{bar}\nQUESTION: {question}\n{bar}")
    print("\nRETRIEVED PASSAGES:")
    for s in with_rag.sources:
        print(f"  [{s['rank']}] {s['score']:.2f}  {s['title']} > {s['section']}")
    print(f"\n--- WITH RAG ({with_rag.latency_s}s) ---\n{with_rag.answer}")
    print(f"\n--- WITHOUT RAG ({without.latency_s}s) ---\n{without.answer}\n")


if __name__ == "__main__":
    main()
