"""
Step 8 — External Data Fetching.

Scrapes or fetches latest information beyond the annual report:
  - Yahoo Finance, MoneyControl, Economic Times, NSE, BSE (planned)

Collects: latest earnings, CEO changes, acquisitions, share price, quarterly results.
"""

from pathlib import Path


def fetch_latest_news(company_name: str, ticker: str | None = None) -> list[dict]:
    """
    Fetch recent news headlines and summaries for the company.

    Args:
        company_name: Company name (e.g. "Reliance Industries").
        ticker: Optional stock ticker (e.g. "RELIANCE.NS").

    Returns:
        List of dicts with keys: title, source, date, summary.
    """
    # TODO: Scrape/API call to news sources
    pass


def fetch_share_price(ticker: str) -> dict | None:
    """
    Fetch latest share price and daily change.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Dict with price, change_pct, currency — or None if unavailable.
    """
    # TODO: Fetch from Yahoo Finance or NSE
    pass


def fetch_quarterly_results(company_name: str) -> list[dict]:
    """
    Fetch recent quarterly earnings summaries.

    Args:
        company_name: Company name.

    Returns:
        List of quarterly result dicts.
    """
    # TODO: Scrape quarterly results
    pass


def format_news_context(news_items: list[dict]) -> str:
    """
    Format news items as a text block for RAG context (Step 13).

    Args:
        news_items: List from fetch_latest_news.

    Returns:
        Human-readable news summary string.
    """
    # TODO: Join headlines and summaries
    pass


def cache_external_data(company_name: str, data: dict) -> Path:
    """
    Save fetched external data to data/cache/ to avoid repeated requests.

    Args:
        company_name: Company identifier.
        data: Dict of fetched news, price, quarterly data.

    Returns:
        Path to cached JSON file.
    """
    # TODO: Write JSON to CACHE_DIR
    pass


def load_cached_external_data(company_name: str) -> dict | None:
    """
    Load previously cached external data if available.

    Args:
        company_name: Company identifier.

    Returns:
        Cached data dict, or None.
    """
    # TODO: Read JSON from CACHE_DIR
    pass
