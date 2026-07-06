"""
Step 2 — Verify the retriever with sample questions.

Builds a mini fake annual report in ChromaDB, runs 4 test questions,
and prints the top retrieved chunks.

Run from project root:
    python scripts/test_retriever.py
"""

import sys
from pathlib import Path

# Allow imports from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.documents import Document

from src.ingestion.embeddings import embed_documents
from src.ingestion.vector_store import create_vector_store, delete_collection
from src.retrieval.retriever import retrieve_documents

COLLECTION = "demo_annual_report"

QUESTIONS = [
    "What was the company's revenue?",
    "How much debt does the company have?",
    "Who is the CEO?",
    "What are the risk factors?",
]


def build_demo_index() -> None:
    """Index a small fake annual report into ChromaDB."""
    delete_collection(COLLECTION)

    chunks = [
        Document(
            page_content="Revenue for FY2024 was Rs 9,00,000 crore, up 18% year on year.",
            metadata={"source": "demo_report.pdf", "chunk_index": 0},
        ),
        Document(
            page_content="Total debt stood at Rs 1,20,000 crore, reduced by 12% from the previous year.",
            metadata={"source": "demo_report.pdf", "chunk_index": 1},
        ),
        Document(
            page_content="Mr. Mukesh Ambani serves as Chairman and Managing Director of the company.",
            metadata={"source": "demo_report.pdf", "chunk_index": 2},
        ),
        Document(
            page_content="Risk factors include commodity price volatility, regulatory changes, and forex exposure.",
            metadata={"source": "demo_report.pdf", "chunk_index": 3},
        ),
        Document(
            page_content="Operating expenses increased due to higher raw material costs.",
            metadata={"source": "demo_report.pdf", "chunk_index": 4},
        ),
    ]

    embedded = embed_documents(chunks)
    create_vector_store(embedded, COLLECTION)
    print(f"Indexed {len(chunks)} demo chunks into collection '{COLLECTION}'\n")


def run_tests() -> None:
    """Ask test questions and print retrieved chunks."""
    for question in QUESTIONS:
        print("=" * 60)
        print(f"QUESTION: {question}")
        print("=" * 60)

        docs = retrieve_documents(question, COLLECTION, top_k=2)

        for i, doc in enumerate(docs, 1):
            chunk_index = doc.metadata.get("chunk_index", "?")
            print(f"\n--- Chunk {i} (index {chunk_index}) ---")
            print(doc.page_content)

        print()


if __name__ == "__main__":
    build_demo_index()
    run_tests()
