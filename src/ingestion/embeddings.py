"""
Step 5 — Embedding Generation (sentence-transformers/all-MiniLM-L6-v2).

Single responsibility: Document chunks → numerical vectors.

    [Document, Document, ...]
              │
              ▼
    HuggingFace Embeddings (local model, no API key)
              │
              ▼
    [EmbeddedDocument, EmbeddedDocument, ...]

Each vector captures the *meaning* of a chunk.
ChromaDB storage is handled in vector_store.py (Step 6).
"""

from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL_NAME

# all-MiniLM-L6-v2 outputs 384-dimensional vectors
EMBEDDING_DIMENSION: int = 384

# Reuse one model instance — loading the model is slow; embedding is fast
_embedding_model: HuggingFaceEmbeddings | None = None


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""


@dataclass
class EmbeddedDocument:
    """
    A document chunk paired with its embedding vector.

    Used as the output format for the next module (ChromaDB storage).
    """

    document: Document
    embedding: list[float]


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Initialize and return the HuggingFace embedding model (singleton).

    all-MiniLM-L6-v2 runs locally — no API key required.
    First call downloads the model (~80 MB); later calls reuse the cached instance.



    Returns:
        Configured HuggingFaceEmbeddings instance.

    Raises:
        EmbeddingError: If the model fails to load.
    """
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    try:
        # LangChain wrapper around sentence-transformers
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
        )
    except Exception as exc:
        raise EmbeddingError(
            f"Failed to load embedding model '{EMBEDDING_MODEL_NAME}': {exc}"
        ) from exc

    return _embedding_model


def extract_texts_from_documents(chunks: list[Document]) -> list[str]:
    """
    Pull page_content strings out of LangChain Document objects.

    The embedding model only accepts plain text — not Document objects directly.

    Args:
        chunks: Document list from chunker.py.

    Returns:
        List of text strings in the same order as the input chunks.

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
    embedding_model: HuggingFaceEmbeddings | None = None,
) -> list[list[float]]:
    """
    Generate embedding vectors for a batch of text strings.

    Args:
        texts: List of strings to embed.
        embedding_model: Optional pre-initialized model; created if omitted.

    Returns:
        List of embedding vectors — one per input string (384 floats each).

    Raises:
        EmbeddingError: On validation or model errors.
    """
    if not texts:
        raise EmbeddingError("Cannot embed an empty list of texts.")

    cleaned = [t.strip() for t in texts]
    if any(not t for t in cleaned):
        raise EmbeddingError("One or more texts are empty after stripping whitespace.")

    model = embedding_model or get_embedding_model()

    try:
        # embed_documents encodes all texts in one batch (efficient on CPU/GPU)
        vectors = model.embed_documents(cleaned)
    except Exception as exc:
        raise EmbeddingError(f"Failed to generate embeddings: {exc}") from exc

    if len(vectors) != len(cleaned):
        raise EmbeddingError(
            f"Expected {len(cleaned)} embeddings, got {len(vectors)}."
        )

    return vectors


def embed_documents(
    chunks: list[Document],
    embedding_model: HuggingFaceEmbeddings | None = None,
) -> list[EmbeddedDocument]:
    """
    Generate embeddings for every document chunk.

    Main entry point after chunking:
        chunks = chunker.chunk_report(clean_text, filename)
        embedded = embed_documents(chunks)

    Args:
        chunks: Document objects from chunker.py.
        embedding_model: Optional pre-initialized model.

    Returns:
        List of EmbeddedDocument — each pairs the original Document with its vector.
        Order is preserved: embedded[i] corresponds to chunks[i].

    Raises:
        EmbeddingError: On validation or model errors.
    """
    # Step 1 — extract plain text from each Document
    texts = extract_texts_from_documents(chunks)

    # Step 2 — convert texts to vectors using the local HuggingFace model
    vectors = embed_texts(texts, embedding_model=embedding_model)

    # Step 3 — pair each Document with its embedding for the next module
    return [
        EmbeddedDocument(document=chunk, embedding=vector)
        for chunk, vector in zip(chunks, vectors)
    ]


def embed_query(
    query: str,
    embedding_model: HuggingFaceEmbeddings | None = None,
) -> list[float]:
    """
    Generate a single embedding vector for a user question (used in Step 11).

    Uses embed_query (not embed_documents) because a search query is one short string.

    Args:
        query: Natural-language question (e.g. "What was the company's debt?").
        embedding_model: Optional pre-initialized model.

    Returns:
        One embedding vector (384 floats).

    Raises:
        EmbeddingError: On validation or model errors.
    """
    cleaned = (query or "").strip()
    if not cleaned:
        raise EmbeddingError("Cannot embed an empty query.")

    model = embedding_model or get_embedding_model()

    try:
        vector = model.embed_query(cleaned)
    except Exception as exc:
        raise EmbeddingError(f"Failed to embed query: {exc}") from exc

    if not vector:
        raise EmbeddingError("Embedding model returned an empty vector.")

    return vector
