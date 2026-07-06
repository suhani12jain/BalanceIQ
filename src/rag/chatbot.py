"""
RAG Chatbot — retrieve context + generate answer with Gemini 2.5 Flash.

Single responsibility: user question → retrieved chunks → Gemini answer.

    User question
         │
         ▼
    retriever (top 4 chunks)
         │
         ▼
    build prompt (context + question)
         │
         ▼
    Gemini 2.5 Flash
         │
         ▼
    Plain-language answer

Does NOT: handle Streamlit UI or file uploads.
"""

from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import GOOGLE_API_KEY, TOP_K_RETRIEVAL, validate_config
from src.rag.llm import get_chat_model
from src.retrieval.retriever import (
    RetrievalError,
    format_retrieved_context,
    retrieve_documents,
)


class ChatbotError(Exception):
    """Raised when the RAG chatbot fails."""


@dataclass
class ChatbotResponse:
    """Full chatbot output — answer plus the chunks used to generate it."""

    answer: str
    retrieved_chunks: list[Document]


def _validate_api_key() -> None:
    """Ensure GOOGLE_API_KEY is configured for Gemini."""
    if not validate_config():
        raise ChatbotError(
            "GOOGLE_API_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )


def get_system_prompt() -> str:
    """
    System instructions for Gemini.

    Tells the model to act as a layman-friendly financial analyst and
  to stay grounded in the retrieved report context only.
    """
    return """You are FinSum, a financial assistant that explains annual reports in simple language.

Rules:
1. Answer ONLY using the context provided below. Do not use outside knowledge.
2. If the context does not contain enough information, say: "I could not find that information in the uploaded report."
3. Explain financial terms in plain English when they appear.
4. Keep answers clear, short, and accurate — suitable for someone with no finance background.
5. Do not invent numbers, names, or facts that are not in the context."""


def build_prompt(context: str, question: str) -> str:
    """
    Build the user message sent to Gemini.

    Combines retrieved report excerpts with the user's question.

    Args:
        context: Formatted text from retriever.format_retrieved_context().
        question: User's natural-language question.

    Returns:
        Complete user prompt string.
    """
    return f"""Use the following excerpts from the annual report to answer the question.

--- REPORT CONTEXT ---
{context}
--- END CONTEXT ---

Question: {question}

Answer in simple language based only on the context above:"""


def generate_answer(context: str, question: str) -> str:
    """
    Call Gemini 2.5 Flash with the built prompt and return the answer.

    Args:
        context: Retrieved report context.
        question: User's question.

    Returns:
        Generated answer string.

    Raises:
        ChatbotError: On API or model errors.
    """
    _validate_api_key()

    try:
        llm = get_chat_model()
        messages = [
            SystemMessage(content=get_system_prompt()),
            HumanMessage(content=build_prompt(context, question)),
        ]
        response = llm.invoke(messages)
    except ChatbotError:
        raise
    except Exception as exc:
        raise ChatbotError(f"Gemini failed to generate an answer: {exc}") from exc

    answer = (response.content or "").strip()
    if not answer:
        raise ChatbotError("Gemini returned an empty response.")

    return answer


def ask(
    question: str,
    collection_name: str,
    top_k: int = TOP_K_RETRIEVAL,
) -> ChatbotResponse:
    """
    End-to-end RAG chatbot: retrieve → prompt → Gemini → answer.

    Main entry point:
        result = ask("What was the company's revenue?", "demo_annual_report")
        print(result.answer)

    Args:
        question: User's natural-language question.
        collection_name: ChromaDB collection / report name.
        top_k: Number of chunks to retrieve (default: 4).

    Returns:
        ChatbotResponse with answer and the retrieved source chunks.

    Raises:
        ChatbotError: On retrieval or generation errors.
    """
    cleaned = (question or "").strip()
    if not cleaned:
        raise ChatbotError("Question cannot be empty.")

    # Step 1 — retrieve top-k relevant chunks from ChromaDB
    try:
        chunks = retrieve_documents(cleaned, collection_name, top_k=top_k)
    except RetrievalError as exc:
        raise ChatbotError(str(exc)) from exc

    # Step 2 — format chunks into a single context block
    context = format_retrieved_context(chunks)

    # Step 3 — send context + question to Gemini and get the answer
    answer = generate_answer(context, cleaned)

    return ChatbotResponse(answer=answer, retrieved_chunks=chunks)


def ask_simple(question: str, collection_name: str) -> str:
    """
    Convenience wrapper that returns only the answer string.

    Args:
        question: User's question.
        collection_name: ChromaDB collection name.

    Returns:
        Generated answer.
    """
    return ask(question, collection_name).answer
