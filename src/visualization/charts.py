"""
Step 10 — Chart Generation (matplotlib).

Renders revenue, profit, and debt trend charts from extracted pandas data.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from src.extraction.financial_extractor import has_extractable_data


def _apply_chart_style(ax, title: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_revenue_trend(revenue_df: pd.DataFrame) -> Figure:
    """
    Line chart of revenue over years.

    Args:
        revenue_df: DataFrame with columns year, revenue.

    Returns:
        matplotlib Figure (for st.pyplot).
    """
    df = revenue_df.dropna(subset=["revenue"]).sort_values("year")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["year"], df["revenue"], marker="o", linewidth=2, color="#2563eb")
    _apply_chart_style(ax, "Revenue Trend", "Amount (₹ crore)")
    ax.set_xticks(df["year"])
    fig.tight_layout()
    return fig


def plot_profit_trend(profit_df: pd.DataFrame) -> Figure:
    """
    Bar chart of net profit by year.

    Args:
        profit_df: DataFrame with columns year, profit.

    Returns:
        matplotlib Figure.
    """
    df = profit_df.dropna(subset=["profit"]).sort_values("year")
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#16a34a" if v >= 0 else "#dc2626" for v in df["profit"]]
    ax.bar(df["year"].astype(str), df["profit"], color=colors, edgecolor="white")
    _apply_chart_style(ax, "Profit Trend", "Amount (₹ crore)")
    fig.tight_layout()
    return fig


def plot_debt_trend(debt_df: pd.DataFrame) -> Figure:
    """
    Bar chart of total debt by year.

    Args:
        debt_df: DataFrame with columns year, debt.

    Returns:
        matplotlib Figure.
    """
    df = debt_df.dropna(subset=["debt"]).sort_values("year")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["year"].astype(str), df["debt"], color="#7c3aed", edgecolor="white")
    _apply_chart_style(ax, "Debt Trend", "Amount (₹ crore)")
    fig.tight_layout()
    return fig


def get_available_charts(
    metrics_df: pd.DataFrame,
) -> list[tuple[str, Figure]]:
    """
    Build up to 3 charts based on available data.

    Args:
        metrics_df: DataFrame with year, revenue, profit, debt columns.

    Returns:
        List of (chart_title, Figure) tuples.
    """
    charts: list[tuple[str, Figure]] = []

    if has_extractable_data(metrics_df, "revenue"):
        charts.append(("Revenue Trend", plot_revenue_trend(metrics_df)))
    if has_extractable_data(metrics_df, "profit"):
        charts.append(("Profit Trend", plot_profit_trend(metrics_df)))
    if has_extractable_data(metrics_df, "debt"):
        charts.append(("Debt Trend", plot_debt_trend(debt_df=metrics_df)))

    return charts
