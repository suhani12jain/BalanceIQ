"""
RAG Chatbot — retrieve context + generate answer with Groq.

This module is RAG only. Glossary / Learn is a separate feature (Learn tab).

Flow:
    question → embed → ChromaDB search → top-k chunks → Groq → answer
"""

from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import GROQ_API_KEY, GROQ_MODEL, TOP_K_RETRIEVAL, validate_config
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


def initialize_llm() -> ChatGroq:
    """
    Create and return the Groq chat client.

    Low temperature keeps answers factual and grounded in context.

    Returns:
        Configured ChatGroq instance.

    Raises:
        ChatbotError: If GROQ_API_KEY is missing.
    """
    if not validate_config():
        raise ChatbotError(
            "GROQ_API_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )

    return ChatGroq(
        model=GROQ_MODEL,
        temperature=0.2,
        api_key=GROQ_API_KEY,
    )


def _get_system_prompt() -> str:
    """System instructions — answer only from provided context."""
    return """You are BalanceIQ, a financial assistant that explains annual reports in simple language.

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
        Prompt string sent to the LLM as the human message.
    """
    return f"""Use the following excerpts from the annual report to answer the question.

--- REPORT CONTEXT ---
{context}
--- END CONTEXT ---

Question: {question}

Answer in simple language based only on the context above:"""


def _invoke_llm(llm: ChatGroq, context: str, question: str) -> str:
    """
    Send the system prompt + built user prompt to Groq and return the reply.

    Args:
        llm: Groq client from initialize_llm().
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
        raise ChatbotError(f"Groq failed to generate an answer: {exc}") from exc

    answer = (response.content or "").strip()
    if not answer:
        raise ChatbotError("Groq returned an empty response.")

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
        4. Initialize Groq (initialize_llm) and invoke

    Args:
        question: User's natural-language question.
        collection_name: ChromaDB collection / report name.
        top_k: Number of chunks to retrieve (default: 4).

    Returns:
        Plain-language answer string.

    Raises:
        ChatbotError: On validation, retrieval, or generation errors.
    """
    response = ask(question, collection_name, top_k=top_k)
    return response.answer


def ask(
    question: str,
    collection_name: str,
    top_k: int = TOP_K_RETRIEVAL,
) -> ChatbotResponse:
    """
    RAG pipeline: retrieve relevant PDF chunks, then ask Groq.

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
