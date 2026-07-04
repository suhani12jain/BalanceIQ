"""
Step 9 — Board & Leadership Extraction.

Extracts CEO, CFO, Chairman, and Independent Directors from the report.
"""

import pandas as pd


def extract_board_members(text: str) -> pd.DataFrame:
    """
    Parse leadership and board sections from report text.

    Args:
        text: Full cleaned report text.

    Returns:
        DataFrame with columns: role, name, designation (optional).
    """
    # TODO: Regex / section-based extraction for board tables
    pass


def extract_ceo(text: str) -> str | None:
    """
    Return the CEO / Managing Director name if found.

    Args:
        text: Report text.

    Returns:
        CEO name string, or None.
    """
    # TODO: Pattern match CEO / MD titles
    pass


def extract_cfo(text: str) -> str | None:
    """
    Return the CFO name if found.

    Args:
        text: Report text.

    Returns:
        CFO name string, or None.
    """
    # TODO: Pattern match CFO titles
    pass


def format_board_context(board_df: pd.DataFrame) -> str:
    """
    Format board info as a text block for RAG context (Step 13).

    Args:
        board_df: DataFrame from extract_board_members.

    Returns:
        Human-readable leadership summary string.
    """
    # TODO: Build context string for prompt injection
    pass
