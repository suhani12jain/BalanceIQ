"""
Step 7 — Financial Metrics Extraction.

Pulls Revenue, Profit, Debt, Assets, EPS, ROE, Cash Flow into pandas DataFrames.
Runs once at upload time — not on every question.
"""

import pandas as pd


def extract_financial_metrics(text: str) -> pd.DataFrame:
    """
    Scan document text for common financial line items and values.

    Args:
        text: Full cleaned report text.

    Returns:
        DataFrame with columns: year, revenue, profit, debt, assets, eps, roe, cash_flow.
    """
    # TODO: Regex / pattern matching for financial tables and prose
    pass


def extract_revenue_series(text: str) -> pd.DataFrame:
    """
    Extract multi-year revenue figures.

    Returns:
        DataFrame with columns: year, revenue.
    """
    # TODO: Parse year-over-year revenue mentions
    pass


def extract_profit_series(text: str) -> pd.DataFrame:
    """
    Extract net profit / PAT figures across years.

    Returns:
        DataFrame with columns: year, profit.
    """
    # TODO: Parse profit figures
    pass


def extract_debt_series(text: str) -> pd.DataFrame:
    """
    Extract total debt / borrowings across years.

    Returns:
        DataFrame with columns: year, debt.
    """
    # TODO: Parse debt figures
    pass


def save_metrics_to_disk(df: pd.DataFrame, report_id: str) -> None:
    """
    Persist extracted metrics as CSV under data/extracted/.

    Args:
        df: Financial metrics DataFrame.
        report_id: Identifier derived from uploaded filename.
    """
    # TODO: df.to_csv(EXTRACTED_DIR / f"{report_id}_metrics.csv")
    pass


def has_extractable_data(df: pd.DataFrame) -> bool:
    """
    Check whether enough data exists to render charts (≥ 2 data points).

    Args:
        df: Financial metrics DataFrame.

    Returns:
        True if charting is possible.
    """
    # TODO: Validate non-empty DataFrame with sufficient rows
    pass
