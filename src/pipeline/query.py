"""
Question → Answer Pipeline Orchestrator.

RAG only — embed question, search ChromaDB, generate answer with Groq.
Glossary is separate (Learn tab / src/glossary/terms.py).
"""

from src.rag.chatbot import ChatbotError, ask


def run_query_pipeline(
    question: str,
    report_id: str,
) -> dict:
    """
    Execute the RAG Q&A pipeline for one user question.

    Args:
        question: User's natural-language question.
        report_id: Identifier for the loaded report / Chroma collection.

    Returns:
        Dict with keys: answer, retrieved_chunk_count.
    """
    cleaned = (question or "").strip()
    if not cleaned:
        raise ValueError("Question cannot be empty.")

    try:
        response = ask(cleaned, report_id)
    except ChatbotError as exc:
        raise RuntimeError(str(exc)) from exc

    return {
        "answer": response.answer,
        "retrieved_chunk_count": len(response.retrieved_chunks),
    }
