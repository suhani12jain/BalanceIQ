"""
Step 13 — Collect Additional Context.

Merges retrieved chunks with latest news, financial ratios, and board info
into one context block for the GPT prompt.
"""

import pandas as pd
from langchain_core.documents import Document


def build_full_context(
    retrieved_chunks: list[Document],
    financial_df: pd.DataFrame | None = None,
    board_context: str = "",
    news_context: str = "",
) -> str:
    """
    Combine all context sources into a single string for the prompt.

    Args:
        retrieved_chunks: Top-k chunks from vector search (Step 12).
        financial_df: Extracted metrics DataFrame (Step 7).
        board_context: Formatted leadership info (Step 9).
        news_context: Formatted latest news (Step 8).

    Returns:
        Full context string passed to GPT.
    """
    # TODO: Merge sections with clear headers
    pass


def format_financial_ratios(df: pd.DataFrame) -> str:
    """
    Convert financial metrics DataFrame into a readable text summary.

    Args:
        df: Metrics from financial_extractor.

    Returns:
        Text block with revenue, profit, debt, ROE, etc.
    """
    # TODO: df.to_string or custom formatting
    pass
