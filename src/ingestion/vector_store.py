"""
Step 6 — ChromaDB Vector Database.

Single responsibility: store (embedding + chunk) pairs for semantic search.

    [Document, Document, ...]
              │
              ▼
    embed + store in ChromaDB
              │
              ▼
    data/chroma_db/<collection_name>/

Does NOT: answer questions or call the chat model.
Retrieval is handled by retriever.py (Steps 10–12).
"""

from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import CHROMA_DIR
from src.ingestion.embeddings import get_embedding_model


class VectorStoreError(Exception):
    """Raised when ChromaDB operations fail."""


def _ensure_chroma_dir() -> None:
    """Create the Chroma persist directory if it does not exist."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)


def create_vector_store(
    chunks: list[Document],
    collection_name: str,
) -> Chroma:
    """
    Build a new ChromaDB collection from document chunks.

    Chroma calls the embedding model internally — each chunk is embedded
    and stored as (vector, text, metadata) in one step.

    Args:
        chunks: LangChain Documents from chunker.py.
        collection_name: Unique name for this report (e.g. reliance_annual_report_2024).

    Returns:
        Chroma vector store with persistence enabled.

    Raises:
        VectorStoreError: If chunks are empty or storage fails.
    """
    if not chunks:
        raise VectorStoreError("Cannot create vector store from empty chunks.")

    if not collection_name or not collection_name.strip():
        raise VectorStoreError("collection_name cannot be empty.")

    _ensure_chroma_dir()
    embedding_model = get_embedding_model()

    try:
        # from_documents: embed each chunk → store in ChromaDB
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            collection_name=collection_name,
            persist_directory=str(CHROMA_DIR),
        )
    except Exception as exc:
        raise VectorStoreError(f"Failed to create Chroma collection: {exc}") from exc

    return vector_store


def save_vector_store(vector_store: Chroma, collection_name: str) -> Path:
    """
    Confirm a Chroma collection is persisted to disk.

    Modern Chroma + LangChain writes to persist_directory on creation.
    This function ensures the directory exists and returns its path.

    Args:
        vector_store: Chroma instance (already persisted on create).
        collection_name: Collection identifier (for validation).

    Returns:
        Path to data/chroma_db/.
    """
    _ensure_chroma_dir()

    if not collection_exists(collection_name):
        raise VectorStoreError(
            f"Collection '{collection_name}' was not found after save."
        )

    return CHROMA_DIR


def load_vector_store(collection_name: str) -> Chroma:
    """
    Load an existing Chroma collection from disk.

    Uses the same embedding model so query vectors are comparable
    to stored chunk vectors.

    Args:
        collection_name: Name of the saved collection.

    Returns:
        Loaded Chroma vector store ready for similarity search.

    Raises:
        VectorStoreError: If the collection does not exist.
    """
    if not collection_exists(collection_name):
        raise VectorStoreError(
            f"Collection '{collection_name}' not found in {CHROMA_DIR}. "
            "Upload and index a report first."
        )

    _ensure_chroma_dir()
    embedding_model = get_embedding_model()

    try:
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_model,
            persist_directory=str(CHROMA_DIR),
        )
    except Exception as exc:
        raise VectorStoreError(f"Failed to load collection '{collection_name}': {exc}") from exc

    return vector_store


def collection_exists(collection_name: str) -> bool:
    """
    Check whether a Chroma collection already exists on disk.

    Args:
        collection_name: Name of the collection to check.

    Returns:
        True if the collection is present in CHROMA_DIR.
    """
    if not CHROMA_DIR.exists():
        return False

    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        existing = {col.name for col in client.list_collections()}
        return collection_name in existing
    except Exception:
        return False


def delete_collection(collection_name: str) -> None:
    """
    Remove a Chroma collection (e.g. when re-uploading the same report).

    Args:
        collection_name: Name of the collection to delete.

    Raises:
        VectorStoreError: If deletion fails.
    """
    if not collection_exists(collection_name):
        return

    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        client.delete_collection(name=collection_name)
    except Exception as exc:
        raise VectorStoreError(
            f"Failed to delete collection '{collection_name}': {exc}"
        ) from exc
