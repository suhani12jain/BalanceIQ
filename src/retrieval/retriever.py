"""
Steps 10–12 — Question Embedding & Vector Search.

Embeds the user question, compares against stored chunk embeddings in ChromaDB,
and returns the most relevant sections.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document


def get_retriever(vector_store: Chroma, top_k: int = 4):
    """
    Create a LangChain retriever from a Chroma vector store.

    Args:
        vector_store: Loaded or newly built Chroma collection.
        top_k: Number of chunks to return per query.

    Returns:
        LangChain VectorStoreRetriever.
    """
    # TODO: vector_store.as_retriever(search_kwargs={"k": top_k})
    pass


def retrieve_relevant_chunks(
    vector_store: Chroma,
    query: str,
    top_k: int = 4,
) -> list[Document]:
    """
    Run similarity search and return top-k matching chunks.

    Example matches:
        "Why did profits decrease?" → Income Statement, MD&A, OpEx chunks.

    Args:
        vector_store: Chroma collection to search.
        query: User's natural-language question.
        top_k: Number of results to return.

    Returns:
        List of relevant Document chunks ranked by similarity.
    """
    # TODO: similarity_search or similarity_search_with_score
    pass


def format_retrieved_context(chunks: list[Document]) -> str:
    """
    Concatenate retrieved chunks into a context string for the LLM.

    Args:
        chunks: Retrieved document chunks.

    Returns:
        Formatted context block with source labels.
    """
    # TODO: Join chunk texts with separators
    pass
