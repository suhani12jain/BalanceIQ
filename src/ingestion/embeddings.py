"""
Step 5 — Embedding Generation (Google text-embedding-004).

Single responsibility: text / Document chunks → numerical vectors.

    [Document, Document, ...]
              │
              ▼
         Embeddings (Google API)
              │
              ▼
    [[0.45, 0.91, ...], [0.12, 0.33, ...], ...]

Chat answers use gemini-2.5-flash (rag_chain.py).
Embeddings use a separate Google embedding model — not the chat model.
"""

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import GEMINI_EMBEDDING_MODEL, GOOGLE_API_KEY

# models/text-embedding-004 outputs 768-dimensional vectors
EMBEDDING_DIMENSION: int = 768


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""


def _validate_api_key() -> None:
    """
    Ensure GOOGLE_API_KEY is set before calling the Google Gemini API.

    Raises:
        EmbeddingError: If the key is missing or still a placeholder.
    """
    if not GOOGLE_API_KEY or not GOOGLE_API_KEY.strip():
        raise EmbeddingError(
            "GOOGLE_API_KEY is not set. Add it to your .env file "
            "(see .env.example)."
        )

    if GOOGLE_API_KEY.strip() == "your_google_api_key_here":
        raise EmbeddingError(
            "GOOGLE_API_KEY is still the placeholder value. "
            "Get a key at https://aistudio.google.com/apikey"
        )


def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Initialize and return the Google embedding model via LangChain.

    Uses models/text-embedding-004 by default (optimized for semantic search).
    LangChain wraps the Google API so we can call embed_documents / embed_query
    without writing raw HTTP requests.

    Returns:
        Configured GoogleGenerativeAIEmbeddings instance.

    Raises:
        EmbeddingError: If the API key is missing or invalid.
    """
    _validate_api_key()

    return GoogleGenerativeAIEmbeddings(
        model=GEMINI_EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )


def extract_texts_from_documents(chunks: list[Document]) -> list[str]:
    """
    Pull page_content strings out of LangChain Document objects.

    Args:
        chunks: Document list from chunker.py.

    Returns:
        List of text strings, one per document (same order as input).

    Raises:
        EmbeddingError: If chunks is empty or any chunk has no text.
    """
    if not chunks:
        raise EmbeddingError("Cannot embed an empty list of documents.")

    texts: list[str] = []
    for index, chunk in enumerate(chunks):
        text = (chunk.page_content or "").strip()
        if not text:
            raise EmbeddingError(
                f"Document at index {index} has empty page_content."
            )
        texts.append(text)

    return texts


def embed_texts(
    texts: list[str],
    embedding_model: GoogleGenerativeAIEmbeddings | None = None,
) -> list[list[float]]:
    """
    Generate embedding vectors for a batch of text strings.

    Args:
        texts: List of strings to embed (e.g. chunk texts).
        embedding_model: Optional pre-initialized model; created if omitted.

    Returns:
        List of embedding vectors — one float list per input string.

    Raises:
        EmbeddingError: On validation failure or Google API errors.
    """
    if not texts:
        raise EmbeddingError("Cannot embed an empty list of texts.")

    cleaned = [t.strip() for t in texts]
    if any(not t for t in cleaned):
        raise EmbeddingError("One or more texts are empty after stripping whitespace.")

    model = embedding_model or get_embedding_model()

    try:
        vectors = model.embed_documents(cleaned)
    except Exception as exc:
        raise _wrap_api_error(exc, context="document embedding") from exc

    if len(vectors) != len(cleaned):
        raise EmbeddingError(
            f"Expected {len(cleaned)} embeddings, got {len(vectors)}."
        )

    return vectors


def embed_documents(
    chunks: list[Document],
    embedding_model: GoogleGenerativeAIEmbeddings | None = None,
) -> list[list[float]]:
    """
    Generate embeddings for a list of LangChain Document chunks.

    Main entry point after chunking:
        chunks = chunker.chunk_report(clean_text, filename)
        vectors = embed_documents(chunks)

    Args:
        chunks: Document objects from chunker.py.
        embedding_model: Optional pre-initialized model.

    Returns:
        Embedding vectors aligned with input order (vectors[i] ↔ chunks[i]).

    Raises:
        EmbeddingError: On validation failure or Google API errors.
    """
    texts = extract_texts_from_documents(chunks)
    return embed_texts(texts, embedding_model=embedding_model)


def embed_query(
    query: str,
    embedding_model: GoogleGenerativeAIEmbeddings | None = None,
) -> list[float]:
    """
    Generate a single embedding vector for a user question (Step 11).

    Args:
        query: Natural-language question.
        embedding_model: Optional pre-initialized model.

    Returns:
        One embedding vector (list of floats).

    Raises:
        EmbeddingError: On validation failure or Google API errors.
    """
    cleaned = (query or "").strip()
    if not cleaned:
        raise EmbeddingError("Cannot embed an empty query.")

    model = embedding_model or get_embedding_model()

    try:
        vector = model.embed_query(cleaned)
    except Exception as exc:
        raise _wrap_api_error(exc, context="query embedding") from exc

    if not vector:
        raise EmbeddingError("Google API returned an empty embedding vector.")

    return vector


def _wrap_api_error(exc: Exception, context: str) -> EmbeddingError:
    """Convert Google API exceptions into clear EmbeddingError messages."""
    message = str(exc).lower()

    if "api key" in message or "api_key" in message or "permission" in message:
        return EmbeddingError(
            f"Google API authentication failed during {context}. "
            "Check your GOOGLE_API_KEY."
        )
    if "quota" in message or "rate" in message or "429" in message:
        return EmbeddingError(
            f"Google API rate limit exceeded during {context}. "
            "Wait and retry."
        )
    if "connect" in message or "network" in message or "timeout" in message:
        return EmbeddingError(
            f"Could not connect to Google API during {context}. "
            "Check your internet connection."
        )

    return EmbeddingError(f"Error during {context}: {exc}")
