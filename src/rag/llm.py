"""
Chat LLM helper for RAG (Google Gemini).

gemini-2.5-flash is used for generating answers — not for embeddings.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import GEMINI_CHAT_MODEL, GOOGLE_API_KEY


def get_chat_model() -> ChatGoogleGenerativeAI:
    """
    Initialize Gemini chat model for RAG answer generation (Step 15).

    Returns:
        Configured ChatGoogleGenerativeAI instance (gemini-2.5-flash by default).
    """
    return ChatGoogleGenerativeAI(
        model=GEMINI_CHAT_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,  # low temperature → factual, less creative hallucination
    )
