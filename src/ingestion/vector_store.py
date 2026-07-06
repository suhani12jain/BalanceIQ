"""
Step 6 — ChromaDB Vector Database.

Single responsibility: persist (chunk + embedding) pairs to disk.

    [EmbeddedDocument, EmbeddedDocument, ...]
              │
              ▼
         ChromaDB (local)
              │
              ▼
    data/chroma_db/

Data survives app restarts via persist_directory.
Does NOT: retrieve chunks, call Gemini, or answer questions.
"""

import re
from pathlib import Path

import chromadb
from langchain_chroma import Chroma

from src.config import CHROMA_DIR
from src.ingestion.embeddings import EmbeddedDocument, get_embedding_model


class VectorStoreError(Exception):
    """Raised when ChromaDB operations fail."""


def _ensure_chroma_dir() -> None:
    """Create the Chroma persist directory if it does not exist."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_collection_name(name: str) -> str:
    """
    Convert a filename or report ID into a valid Chroma collection name.

    Chroma allows letters, digits, underscores, and hyphens (3–63 chars).

    Args:
        name: Raw name (e.g. "Reliance_Annual_Report_2024.pdf").

    Returns:
        Sanitized collection name (e.g. "reliance_annual_report_2024").
    """
    # Drop file extension and lowercase
    stem = Path(name).stem.lower()
    # Replace invalid characters with underscores
    clean = re.sub(r"[^a-z0-9_-]", "_", stem)
    clean = re.sub(r"_+", "_", clean).strip("_")

    if len(clean) < 3:
        clean = f"report_{clean}"

    return clean[:63]


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
    Remove a Chroma collection (e.g. before re-indexing the same report).

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


def _validate_embedded_documents(embedded_docs: list[EmbeddedDocument]) -> None:
    """Ensure embedded documents are valid before storing."""
    if not embedded_docs:
        raise VectorStoreError("Cannot create vector store from empty embedded_docs.")

    for index, item in enumerate(embedded_docs):
        if not item.document.page_content.strip():
            raise VectorStoreError(f"Embedded document at index {index} has empty text.")
        if not item.embedding:
            raise VectorStoreError(f"Embedded document at index {index} has no embedding vector.")


def create_vector_store(
    embedded_docs: list[EmbeddedDocument],
    collection_name: str,
    *,
    overwrite: bool = True,
) -> Chroma:
    """
    Build a new ChromaDB collection from pre-computed embeddings.

    Stores three things per chunk:
        - text      (page_content)
        - metadata  (source, chunk_index, etc.)
        - embedding (384-dim vector from all-MiniLM-L6-v2)

    Args:
        embedded_docs: Output from embeddings.embed_documents().
        collection_name: Unique name for this report.
        overwrite: If True, delete an existing collection with the same name first.

    Returns:
        Chroma vector store persisted under data/chroma_db/.

    Raises:
        VectorStoreError: If input is invalid or storage fails.
    """
    if not collection_name or not collection_name.strip():
        raise VectorStoreError("collection_name cannot be empty.")

    collection_name = sanitize_collection_name(collection_name)
    _validate_embedded_documents(embedded_docs)
    _ensure_chroma_dir()

    # Replace existing index when the same report is uploaded again
    if overwrite and collection_exists(collection_name):
        delete_collection(collection_name)

    embedding_model = get_embedding_model()

    try:
        # Step 1 — open (or create) a persistent Chroma collection
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_model,
            persist_directory=str(CHROMA_DIR),
        )

        # Step 2 — unpack texts, metadata, and pre-computed embeddings
        texts = [item.document.page_content for item in embedded_docs]
        metadatas = [item.document.metadata for item in embedded_docs]
        embeddings = [item.embedding for item in embedded_docs]

        # Step 3 — write all chunks + vectors to ChromaDB in one batch
        vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    except VectorStoreError:
        raise
    except Exception as exc:
        raise VectorStoreError(f"Failed to create Chroma collection: {exc}") from exc

    return vector_store


def save_vector_store(vector_store: Chroma, collection_name: str) -> Path:
    """
    Confirm the Chroma collection is persisted to disk.

    LangChain-Chroma writes to persist_directory automatically on add_texts.
    This function verifies the collection exists and returns the storage path.

    Args:
        vector_store: Chroma instance returned by create_vector_store().
        collection_name: Collection identifier used during creation.

    Returns:
        Path to data/chroma_db/.

    Raises:
        VectorStoreError: If the collection is not found after saving.
    """
    _ensure_chroma_dir()
    collection_name = sanitize_collection_name(collection_name)

    if not collection_exists(collection_name):
        raise VectorStoreError(
            f"Collection '{collection_name}' was not found after save."
        )

    # Touch the store to ensure persistence is flushed (no-op on modern Chroma)
    _ = vector_store

    return CHROMA_DIR


def load_vector_store(collection_name: str) -> Chroma:
    """
    Load an existing Chroma collection from disk.

    Uses the same embedding model so future query vectors are compatible
    with stored chunk vectors (needed by retriever.py later).

    Args:
        collection_name: Name of the saved collection.

    Returns:
        Loaded Chroma vector store.

    Raises:
        VectorStoreError: If the collection does not exist.
    """
    collection_name = sanitize_collection_name(collection_name)

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
        raise VectorStoreError(
            f"Failed to load collection '{collection_name}': {exc}"
        ) from exc

    return vector_store


def get_collection_count(collection_name: str) -> int:
    """
    Return how many chunks are stored in a collection.

    Useful for verifying indexing after upload.

    Args:
        collection_name: Name of the collection.

    Returns:
        Number of stored documents.

    Raises:
        VectorStoreError: If the collection does not exist.
    """
    collection_name = sanitize_collection_name(collection_name)
    vector_store = load_vector_store(collection_name)

    try:
        collection = vector_store._collection
        return collection.count()
    except Exception as exc:
        raise VectorStoreError(
            f"Failed to count documents in '{collection_name}': {exc}"
        ) from exc
