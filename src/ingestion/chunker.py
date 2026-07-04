"""
Step 4 — Document Chunking (LangChain RecursiveCharacterTextSplitter).

Splits the full report into ~500–1000 token chunks for embedding.
"""

from langchain_core.documents import Document


def split_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """
    Split a long document into LangChain Document chunks.

    Args:
        text: Preprocessed full-document text.
        chunk_size: Target size of each chunk in characters.
        chunk_overlap: Overlap between adjacent chunks.

    Returns:
        List of LangChain Document objects.
    """
    # TODO: RecursiveCharacterTextSplitter → return chunks
    pass


def add_chunk_metadata(
    chunks: list[Document],
    source_filename: str,
) -> list[Document]:
    """
    Attach source filename and chunk index to each Document's metadata.

    Args:
        chunks: List of document chunks.
        source_filename: Original PDF filename.

    Returns:
        Chunks with enriched metadata.
    """
    # TODO: Set metadata fields on each chunk
    pass
