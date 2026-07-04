"""
Step 6 — ChromaDB Vector Database.

Stores (embedding, original chunk) pairs for semantic search.
Persists collections under data/chroma_db/.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import CHROMA_DIR


def create_vector_store(
    chunks: list[Document],
    collection_name: str,
) -> Chroma:
    """
    Build a new ChromaDB collection from document chunks and their embeddings.

    Args:
        chunks: LangChain Documents to index.
        collection_name: Chroma collection name (e.g. report ID from filename).

    Returns:
        Chroma vector store with persistence enabled.
    """
    # TODO: get_embedding_model() → Chroma.from_documents(
    #           documents=chunks,
    #           embedding=...,
    #           collection_name=collection_name,
    #           persist_directory=str(CHROMA_DIR),
    #       )
    pass


def save_vector_store(vector_store: Chroma, collection_name: str) -> Path:
    """
    Ensure a Chroma collection is persisted to disk.

    Chroma writes to persist_directory on creation; this flushes any pending data.

    Args:
        vector_store: Chroma instance to persist.
        collection_name: Collection identifier.

    Returns:
        Path to the Chroma persist directory.
    """
    # TODO: vector_store.persist() if needed; return CHROMA_DIR
    pass


def load_vector_store(collection_name: str) -> Chroma:
    """
    Load an existing Chroma collection from disk.

    Args:
        collection_name: Name of the saved collection.

    Returns:
        Loaded Chroma vector store ready for similarity search.
    """
    # TODO: Chroma(
    #           persist_directory=str(CHROMA_DIR),
    #           embedding_function=get_embedding_model(),
    #           collection_name=collection_name,
    #       )
    pass


def collection_exists(collection_name: str) -> bool:
    """
    Check whether a Chroma collection already exists on disk.

    Args:
        collection_name: Name of the collection to check.

    Returns:
        True if the collection is present in CHROMA_DIR.
    """
    # TODO: Check CHROMA_DIR for collection metadata / sqlite file
    pass
