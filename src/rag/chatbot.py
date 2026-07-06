"""
RAG Chatbot — retrieve context + generate answer with Gemini 2.5 Flash.

Orchestration lives in small, focused functions:
    initialize_llm()   → Gemini client
    build_prompt()       → context + question string
    generate_answer()    → retrieve → prompt → invoke → answer
"""

from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import GEMINI_CHAT_MODEL, GOOGLE_API_KEY, TOP_K_RETRIEVAL, validate_config
from src.retrieval.retriever import (
    RetrievalError,
    format_retrieved_context,
    retrieve_documents,
)


class ChatbotError(Exception):
    """Raised when the RAG chatbot fails."""


@dataclass
class ChatbotResponse:
    """Answer plus the source chunks used to produce it."""

    answer: str
    retrieved_chunks: list[Document]


def initialize_llm() -> ChatGoogleGenerativeAI:
    """
    Create and return the Gemini 2.5 Flash client.

    Low temperature keeps answers factual and grounded in context.

    Returns:
        Configured ChatGoogleGenerativeAI instance.

    Raises:
        ChatbotError: If GOOGLE_API_KEY is missing.
    """
    if not validate_config():
        raise ChatbotError(
            "GOOGLE_API_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )

    return ChatGoogleGenerativeAI(
        model=GEMINI_CHAT_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
    )


def _get_system_prompt() -> str:
    """System instructions — answer only from provided context."""
    return """You are FinSum, a financial assistant that explains annual reports in simple language.

Rules:
1. Answer ONLY using the context provided below. Do not use outside knowledge.
2. If the context does not contain enough information, say: "I could not find that information in the uploaded report."
3. Explain financial terms in plain English when they appear.
4. Keep answers clear, short, and accurate — suitable for someone with no finance background.
5. Do not invent numbers, names, or facts that are not in the context."""


def build_prompt(context: str, question: str) -> str:
    """
    Construct the user prompt string from retrieved context and the question.

    Args:
        context: Formatted report excerpts from the retriever.
        question: User's natural-language question.

    Returns:
        Prompt string sent to Gemini as the human message.
    """
    return f"""Use the following excerpts from the annual report to answer the question.

--- REPORT CONTEXT ---
{context}
--- END CONTEXT ---

Question: {question}

Answer in simple language based only on the context above:"""


def _invoke_llm(llm: ChatGoogleGenerativeAI, context: str, question: str) -> str:
    """
    Send the system prompt + built user prompt to Gemini and return the reply.

    Args:
        llm: Gemini client from initialize_llm().
        context: Retrieved report context.
        question: User's question.

    Returns:
        Generated answer text.

    Raises:
        ChatbotError: On API or empty-response errors.
    """
    try:
        response = llm.invoke([
            SystemMessage(content=_get_system_prompt()),
            HumanMessage(content=build_prompt(context, question)),
        ])
    except Exception as exc:
        raise ChatbotError(f"Gemini failed to generate an answer: {exc}") from exc

    answer = (response.content or "").strip()
    if not answer:
        raise ChatbotError("Gemini returned an empty response.")

    return answer


def generate_answer(
    question: str,
    collection_name: str,
    top_k: int = TOP_K_RETRIEVAL,
) -> str:
    """
    Orchestrate the full RAG answer flow and return the final answer.

    Steps:
        1. Retrieve top-k relevant chunks from ChromaDB
        2. Format chunks into a context string
        3. Build the prompt (build_prompt)
        4. Initialize Gemini (initialize_llm) and invoke

    Args:
        question: User's natural-language question.
        collection_name: ChromaDB collection / report name.
        top_k: Number of chunks to retrieve (default: 4).

    Returns:
        Plain-language answer string.

    Raises:
        ChatbotError: On validation, retrieval, or generation errors.
    """
    cleaned = (question or "").strip()
    if not cleaned:
        raise ChatbotError("Question cannot be empty.")

    # Step 1 — semantic search over ChromaDB
    try:
        chunks = retrieve_documents(cleaned, collection_name, top_k=top_k)
    except RetrievalError as exc:
        raise ChatbotError(str(exc)) from exc

    # Step 2 — join retrieved chunks into one context block
    context = format_retrieved_context(chunks)

    # Step 3 & 4 — prompt + Gemini
    llm = initialize_llm()
    return _invoke_llm(llm, context, cleaned)


def ask(
    question: str,
    collection_name: str,
    top_k: int = TOP_K_RETRIEVAL,
) -> ChatbotResponse:
    """
    Like generate_answer(), but also returns the retrieved source chunks.

    Args:
        question: User's question.
        collection_name: ChromaDB collection name.
        top_k: Number of chunks to retrieve.

    Returns:
        ChatbotResponse with answer and retrieved_chunks.
    """
    cleaned = (question or "").strip()
    if not cleaned:
        raise ChatbotError("Question cannot be empty.")

    try:
        chunks = retrieve_documents(cleaned, collection_name, top_k=top_k)
    except RetrievalError as exc:
        raise ChatbotError(str(exc)) from exc

    context = format_retrieved_context(chunks)
    llm = initialize_llm()
    answer = _invoke_llm(llm, context, cleaned)

    return ChatbotResponse(answer=answer, retrieved_chunks=chunks)
