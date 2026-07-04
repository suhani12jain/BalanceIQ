"""
Step 5 — Embedding Generation (OpenAI text-embedding-3-small).

Converts each text chunk and user questions into dense vectors.
"""

from langchain_openai import OpenAIEmbeddings


def get_embedding_model() -> OpenAIEmbeddings:
    """
    Create a configured OpenAIEmbeddings instance from src.config.

    Returns:
        LangChain OpenAIEmbeddings ready for embed_documents / embed_query.
    """
    # TODO: Return OpenAIEmbeddings with config values
    pass


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embedding vectors for a batch of chunk texts.

    Args:
        texts: List of chunk texts to embed.

    Returns:
        List of embedding vectors (one per input string).
    """
    # TODO: Call embedding model on batch
    pass


def embed_query(query: str) -> list[float]:
    """
    Generate a single embedding vector for a user question (Step 11).

    Args:
        query: Natural-language question from the user.

    Returns:
        Embedding vector for semantic search.
    """
    # TODO: Call embedding model on single query
    pass
