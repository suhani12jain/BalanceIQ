"""
Steps 14–15 — Prompt Building & Gemini Answer Generation.

Builds the final prompt (system + context + question) and calls gemini-2.5-flash.
Answers only from provided context to reduce hallucination.
"""


def get_system_prompt() -> str:
    """
    Return the system prompt for Gemini.

    Instructs the model to:
        - Act as a financial analyst for laymen
        - Use only provided context
        - Explain jargon simply
        - Admit when information is missing

    Returns:
        System prompt string.
    """
    # TODO: Return multi-line system prompt
    pass


def build_prompt(context: str, question: str) -> str:
    """
    Assemble the final user prompt with context and question (Step 14).

    Args:
        context: Full context from context_builder.
        question: User's question.

    Returns:
        Formatted prompt string.
    """
    # TODO: Template with Context + Question sections
    pass


def build_rag_chain(retriever):
    """
    Assemble a LangChain RAG chain (retriever + LLM).

    Args:
        retriever: LangChain retriever backed by ChromaDB.

    Returns:
        Runnable chain.
    """
    # TODO: ChatGoogleGenerativeAI (gemini-2.5-flash) + prompt template + retriever chain
    pass


def answer_question(context: str, question: str) -> str:
    """
    Generate a plain-language answer using context and Gemini (Step 15).

    Args:
        context: Merged context from context_builder.
        question: User's question.

    Returns:
        AI answer string.
    """
    # TODO: Invoke LLM with system prompt + build_prompt output
    pass
