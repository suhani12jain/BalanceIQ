"""
Steps 10–12 — Question Embedding & Vector Search.

Single responsibility: user question → top-k relevant Document chunks.

    User question
         │
         ▼
    embed query (same model as indexing)
         │
         ▼
    ChromaDB similarity search
         │
         ▼
    [Document, Document, Document, Document]

Does NOT: call Gemini or generate answers.
Answer generation is handled by rag_chain.py (Steps 14–15).
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import TOP_K_RETRIEVAL
from src.ingestion.embeddings import embed_query
from src.ingestion.vector_store import load_vector_store, sanitize_collection_name


class RetrievalError(Exception):
    """Raised when document retrieval fails."""


def _validate_question(question: str) -> str:
    """
    Strip and validate the user's question.

    Raises:
        RetrievalError: If the question is empty.
    """
    cleaned = (question or "").strip()
    if not cleaned:
        raise RetrievalError("Question cannot be empty.")
    return cleaned


def get_retriever(vector_store: Chroma, top_k: int = TOP_K_RETRIEVAL):
    """
    Create a LangChain retriever from a loaded Chroma vector store.

    Useful when wiring a LangChain RAG chain later.

    Args:
        vector_store: Loaded Chroma collection.
        top_k: Number of chunks to return per query (default: 4).

    Returns:
        LangChain VectorStoreRetriever.
    """
    if top_k < 1:
        raise RetrievalError("top_k must be at least 1.")

    return vector_store.as_retriever(search_kwargs={"k": top_k})


def retrieve_relevant_chunks(
    vector_store: Chroma,
    query: str,
    top_k: int = TOP_K_RETRIEVAL,
) -> list[Document]:
    """
    Embed the question and run semantic similarity search in ChromaDB.

    Steps:
        1. Validate the question text
        2. Convert question → embedding vector (all-MiniLM-L6-v2)
        3. Compare query vector against all stored chunk vectors
        4. Return the top-k most similar Document chunks

    Example:
        "Why did profits decrease?" → Income Statement, MD&A, OpEx chunks.

    Args:
        vector_store: Loaded Chroma collection from vector_store.load_vector_store().
        query: User's natural-language question.
        top_k: Number of results to return (default: 4).

    Returns:
        List of relevant Document chunks ranked by similarity (most relevant first).

    Raises:
        RetrievalError: On validation or search errors.
    """
    cleaned_query = _validate_question(query)

    if top_k < 1:
        raise RetrievalError("top_k must be at least 1.")

    try:
        # Step 2 — embed the question with the SAME model used during indexing
        query_vector = embed_query(cleaned_query)

        # Step 3 & 4 — find the top-k chunks whose vectors are closest to the query
        documents = vector_store.similarity_search_by_vector(
            embedding=query_vector,
            k=top_k,
        )
    except RetrievalError:
        raise
    except Exception as exc:
        raise RetrievalError(f"Similarity search failed: {exc}") from exc

    if not documents:
        raise RetrievalError(
            "No documents found in the vector store. "
            "Make sure the report has been indexed."
        )

    return documents


def retrieve_documents(
    question: str,
    collection_name: str,
    top_k: int = TOP_K_RETRIEVAL,
) -> list[Document]:
    """
    End-to-end retrieval: load ChromaDB → search → return top-k chunks.

    Main entry point for the Q&A pipeline:
        docs = retrieve_documents("What was the company's debt?", "Reliance_Annual_Report_2024.pdf")

    Args:
        question: User's natural-language question.
        collection_name: Report / collection name (filename or sanitized ID).
        top_k: Number of chunks to retrieve (default: 4).

    Returns:
        Top-k relevant LangChain Document objects (no answer generated).

    Raises:
        RetrievalError: If the collection is missing or search fails.
    """
    cleaned_query = _validate_question(question)
    safe_name = sanitize_collection_name(collection_name)

    try:
        # Step 1 — load the persisted ChromaDB collection from disk
        vector_store = load_vector_store(safe_name)
    except Exception as exc:
        raise RetrievalError(
            f"Could not load collection '{safe_name}'. "
            "Upload and index a report first."
        ) from exc

    return retrieve_relevant_chunks(vector_store, cleaned_query, top_k=top_k)


def format_retrieved_context(chunks: list[Document]) -> str:
    """
    Concatenate retrieved chunks into one context string.

    Helper for rag_chain.py — formats chunks but does NOT call Gemini.

    Args:
        chunks: Retrieved document chunks.

    Returns:
        Formatted context block with chunk labels.
    """
    if not chunks:
        return ""

    sections: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "unknown")
        chunk_index = chunk.metadata.get("chunk_index", "?")
        header = f"[Chunk {index} | source: {source} | index: {chunk_index}]"
        sections.append(f"{header}\n{chunk.page_content}")

    return "\n\n---\n\n".join(sections)
