"""
Step 16 — Chart Generation (matplotlib).

Renders revenue, profit, and debt trend charts from extracted pandas data.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_revenue_trend(revenue_df: pd.DataFrame) -> Figure:
    """
    Line chart of revenue over years.

    Args:
        revenue_df: DataFrame with columns year, revenue.

    Returns:
        matplotlib Figure (for st.pyplot).
    """
    # TODO: Create line plot
    pass


def plot_profit_trend(profit_df: pd.DataFrame) -> Figure:
    """
    Bar chart of net profit by year.

    Args:
        profit_df: DataFrame with columns year, profit.

    Returns:
        matplotlib Figure.
    """
    # TODO: Create bar chart
    pass


def plot_debt_trend(debt_df: pd.DataFrame) -> Figure:
    """
    Bar chart of total debt by year.

    Args:
        debt_df: DataFrame with columns year, debt.

    Returns:
        matplotlib Figure.
    """
    # TODO: Create bar chart
    pass


def get_available_charts(
    revenue_df: pd.DataFrame,
    profit_df: pd.DataFrame,
    debt_df: pd.DataFrame,
) -> list[tuple[str, Figure]]:
    """
    Build up to 3 charts based on available data.

    Returns:
        List of (chart_title, Figure) tuples.
    """
    # TODO: Conditionally call plot functions
    pass
