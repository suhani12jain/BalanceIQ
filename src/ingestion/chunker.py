"""
Step 4 — Document Chunking (LangChain RecursiveCharacterTextSplitter).

Single responsibility: clean text → list of Document chunks.

    clean_text (from preprocessor)
              │
              ▼
           Chunker
              │
              ▼
    [Document, Document, ...]

Does NOT: generate embeddings, store in ChromaDB, or call GPT.
Those belong to embeddings.py and vector_store.py (Steps 5–6).
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """
    Split clean report text into overlapping chunks.

    Uses RecursiveCharacterTextSplitter, which tries to break on
    paragraphs → sentences → words so chunks stay readable.

    Typical settings:
        chunk_size    = 1000 characters
        chunk_overlap = 200 characters (preserves context at boundaries)

    Args:
        text: Preprocessed text from preprocessor.clean_text().
        chunk_size: Target maximum size of each chunk in characters.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of LangChain Document objects with page_content set.
    """
    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        # Prefer splitting on natural boundaries (paragraphs, then sentences)
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.create_documents([text])


def add_chunk_metadata(
    chunks: list[Document],
    source_filename: str,
) -> list[Document]:
    """
    Attach source filename and chunk index to each Document's metadata.

    Metadata helps trace answers back to the original report during retrieval.

    Args:
        chunks: List of document chunks from split_into_chunks().
        source_filename: Original PDF filename (e.g. Reliance_Annual_Report_2024.pdf).

    Returns:
        Same chunks with metadata enriched in-place.
    """
    for index, chunk in enumerate(chunks):
        chunk.metadata["source"] = source_filename
        chunk.metadata["chunk_index"] = index
        chunk.metadata["total_chunks"] = len(chunks)

    return chunks


def chunk_report(
    clean_text: str,
    source_filename: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """
    Convenience function: split text and attach metadata in one call.

    Args:
        clean_text: Output from preprocessor.clean_text().
        source_filename: Original PDF filename.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between chunks.

    Returns:
        List of Document chunks ready for embedding (Step 5).
    """
    chunks = split_into_chunks(clean_text, chunk_size, chunk_overlap)
    return add_chunk_metadata(chunks, source_filename)
