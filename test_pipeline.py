"""
test_pipeline.py — Run the full BalanceIQ RAG backend without Streamlit.

Usage:
    python test_pipeline.py data/uploads/infosys-ar-25.pdf
    python test_pipeline.py data/uploads/infosys-ar-25.pdf -q "What was the revenue?"

Pipeline:
    Load PDF → Parse → Preprocess → Chunk → Embed → ChromaDB
    → Retrieve chunks → Gemini answer
"""

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import TOP_K_RETRIEVAL, validate_config
from src.ingestion.chunker import chunk_report
from src.ingestion.embeddings import embed_documents, get_embedding_model
from src.ingestion.pdf_parser import extract_text_by_page
from src.ingestion.preprocessor import clean_text
from src.ingestion.vector_store import (
    create_vector_store,
    save_vector_store,
    sanitize_collection_name,
)
from src.rag.chatbot import ChatbotError, ask
from src.retrieval.retriever import retrieve_documents


DEFAULT_QUESTION = "What was the company's revenue?"


def _step(label: str) -> float:
    """Print a pipeline step label and return start time."""
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print("=" * 60)
    return time.perf_counter()


def _done(start: float, detail: str = "") -> None:
    """Print elapsed time for a step."""
    elapsed = time.perf_counter() - start
    suffix = f" — {detail}" if detail else ""
    print(f"  ✓ Done in {elapsed:.1f}s{suffix}")


def run_pipeline(pdf_path: Path, question: str) -> None:
    """Execute the full ingest + query pipeline and print results."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    filename = pdf_path.name
    collection_name = sanitize_collection_name(filename)

    # --- INGESTION ---
    t = _step("1. Load & Parse PDF")
    pages = extract_text_by_page(pdf_path)
    raw_text = "\n\n".join(pages)
    _done(t, f"{len(pages)} pages, {len(raw_text):,} characters")

    t = _step("2. Preprocess (clean text)")
    cleaned_text = clean_text(raw_text)
    _done(t, f"{len(cleaned_text):,} characters after cleaning")

    t = _step("3. Chunk document")
    chunks = chunk_report(cleaned_text, filename)
    _done(t, f"{len(chunks)} chunks")

    t = _step("4. Generate embeddings")
    model = get_embedding_model()
    embedded = embed_documents(chunks, embedding_model=model)
    _done(t, f"{len(embedded)} vectors (dim={len(embedded[0].embedding)})")

    t = _step("5. Store in ChromaDB")
    store = create_vector_store(embedded, collection_name)
    save_vector_store(store, collection_name)
    _done(t, f"collection='{collection_name}'")

    # --- RETRIEVAL + ANSWER ---
    t = _step(f"6. Retrieve top-{TOP_K_RETRIEVAL} chunks")
    print(f"  Question: {question}")
    retrieved = retrieve_documents(question, collection_name, top_k=TOP_K_RETRIEVAL)
    _done(t, f"{len(retrieved)} chunks retrieved")

    print(f"\n{'─' * 60}")
    print("  RETRIEVED CHUNKS")
    print("─" * 60)
    for i, doc in enumerate(retrieved, 1):
        idx = doc.metadata.get("chunk_index", "?")
        print(f"\n[Chunk {i} | index {idx}]")
        preview = doc.page_content[:400]
        print(preview + ("..." if len(doc.page_content) > 400 else ""))

    if not validate_config():
        print("\n⚠ GOOGLE_API_KEY not set — skipping Gemini answer.")
        return

    t = _step("7. Generate Gemini answer")
    try:
        response = ask(question, collection_name, top_k=TOP_K_RETRIEVAL)
    except ChatbotError as exc:
        print(f"  ✗ Chatbot error: {exc}")
        return
    _done(t)

    print(f"\n{'─' * 60}")
    print("  GEMINI ANSWER")
    print("─" * 60)
    print(f"\nQ: {question}\n")
    print(response.answer)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the BalanceIQ RAG pipeline without Streamlit."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        default="data/uploads/infosys-ar-25.pdf",
        help="Path to the annual report PDF (default: data/uploads/infosys-ar-25.pdf)",
    )
    parser.add_argument(
        "-q", "--question",
        default=DEFAULT_QUESTION,
        help=f"Sample question to ask (default: '{DEFAULT_QUESTION}')",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = PROJECT_ROOT / pdf_path

    print("BalanceIQ — Full Pipeline Test")
    print(f"PDF: {pdf_path}")

    try:
        run_pipeline(pdf_path, args.question)
        print(f"\n{'=' * 60}")
        print("  Pipeline completed successfully.")
        print("=" * 60)
    except Exception as exc:
        print(f"\n✗ Pipeline failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
