"""
Question → Answer Pipeline Orchestrator.

Runs Steps 10–17 when a user asks a question:
  10. Receive question
  11. Embed question
  12. Vector search → retrieve chunks
  13. Build full context (chunks + news + ratios + board)
  14–15. Build prompt → GPT answer
  16. (Charts served separately from stored metrics)
  17. Append glossary explanations if relevant
"""


def run_query_pipeline(
    question: str,
    report_id: str,
) -> dict:
    """
    Execute the full Q&A pipeline for one user question.

    Args:
        question: User's natural-language question.
        report_id: Identifier for the loaded report / Chroma collection.

    Returns:
        Dict with keys: answer, glossary_notes, retrieved_chunk_count.
    """
    # TODO: Chain retrieval → context_builder → rag_chain → glossary
    pass
