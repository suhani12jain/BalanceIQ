"""
Step 9 — Financial Metrics Extraction.

Pulls Revenue, Profit, Debt, and Assets into pandas DataFrames using regex.
Runs once at upload time — not on every question.
"""

import re
from pathlib import Path

import pandas as pd

from src.config import EXTRACTED_DIR

# Metric labels commonly found in annual reports (case-insensitive).
METRIC_PATTERNS: dict[str, list[str]] = {
    "revenue": [
        r"total\s+revenue",
        r"net\s+sales",
        r"revenue\s+from\s+operations",
        r"\bturnover\b",
        r"\brevenue\b",
        r"\bsales\b",
    ],
    "profit": [
        r"net\s+profit(?:\s+after\s+tax)?",
        r"profit\s+after\s+tax",
        r"\bpat\b",
        r"net\s+income",
        r"profit\s+for\s+the\s+(?:year|period)",
        r"\bearnings\b",
    ],
    "debt": [
        r"total\s+debt",
        r"total\s+borrowings",
        r"long[\-\s]?term\s+borrowings",
        r"short[\-\s]?term\s+borrowings",
        r"\bdebt\b",
        r"\bborrowings\b",
    ],
    "assets": [
        r"total\s+assets",
        r"\bassets\b",
    ],
}

YEAR_PATTERN = re.compile(
    r"(?:FY\s*)?(20\d{2})(?:[-/](?:\d{2}|20\d{2}))?",
    re.IGNORECASE,
)

# Numbers with optional commas/decimals and common Indian/global units.
VALUE_PATTERN = re.compile(
    r"(?:₹|rs\.?\s*)?"
    r"([\d,]+(?:\.\d+)?)\s*"
    r"(crore|cr\.?|million|mn\.?|billion|bn\.?|lakh|lakhs)?",
    re.IGNORECASE,
)

UNIT_MULTIPLIERS = {
    "crore": 1.0,
    "cr": 1.0,
    "cr.": 1.0,
    "lakh": 0.01,
    "lakhs": 0.01,
    "million": 0.1,
    "mn": 0.1,
    "mn.": 0.1,
    "billion": 100.0,
    "bn": 100.0,
    "bn.": 100.0,
}


def _parse_number(raw: str, unit: str | None = None) -> float | None:
    """Convert a matched numeric string (and optional unit) to crore-equivalent float."""
    try:
        value = float(raw.replace(",", ""))
    except ValueError:
        return None

    if value <= 0:
        return None

    multiplier = UNIT_MULTIPLIERS.get((unit or "").lower().strip("."), 1.0)
    return value * multiplier


def _extract_year(text: str) -> int | None:
    """Return the ending calendar year from FY2023, 2023-24, or plain 2024."""
    match = YEAR_PATTERN.search(text)
    if not match:
        return None
    year = int(match.group(1))
    if 1990 <= year <= 2035:
        return year
    return None


def _line_matches_metric(line: str, metric_key: str) -> bool:
    """True if the line mentions the given metric label."""
    lowered = line.lower()
    for pattern in METRIC_PATTERNS[metric_key]:
        if re.search(pattern, lowered):
            return True
    return False


def _years_from_line(line: str) -> list[int]:
    """Extract all plausible years from a line."""
    years: list[int] = []
    for match in YEAR_PATTERN.finditer(line):
        year = int(match.group(1))
        if 1990 <= year <= 2035:
            years.append(year)
    return years


def _strip_years_from_line(line: str) -> str:
    """Remove FY/year tokens so year numbers are not parsed as metric values."""
    cleaned = YEAR_PATTERN.sub(" ", line)
    cleaned = re.sub(r"\bFY\s*\b", " ", cleaned, flags=re.IGNORECASE)
    return cleaned


def _values_from_line(
    line: str,
    metric_key: str | None = None,
    known_years: set[int] | None = None,
) -> list[float]:
    """Extract monetary values from a line, optionally stripping the metric label first."""
    cleaned = line
    if metric_key:
        for pattern in METRIC_PATTERNS[metric_key]:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = _strip_years_from_line(cleaned)
    years_on_line = set(_years_from_line(line))
    if known_years:
        years_on_line |= known_years

    values: list[float] = []
    for match in VALUE_PATTERN.finditer(cleaned):
        raw = match.group(1)
        unit = match.group(2)
        parsed = _parse_number(raw, unit)
        if parsed is None:
            continue
        if not _is_plausible_metric_value(parsed, unit, years_on_line):
            continue
        values.append(parsed)
    return values


def _is_plausible_metric_value(
    value: float,
    unit: str | None,
    known_years: set[int],
) -> bool:
    """Reject values that are almost certainly calendar years, not amounts."""
    if unit:
        return True

    int_value = int(value)
    if value == int_value and int_value in known_years:
        return False

    # Bare 4-digit numbers in year range are usually dates, not rupee amounts.
    if value == int_value and 1990 <= int_value <= 2035:
        return False

    return True


def _years_from_context(lines: list[str], index: int, lookback: int = 8) -> list[int]:
    """Collect years from the current line and preceding lines (table header row)."""
    years: list[int] = []
    start = max(0, index - lookback)
    for line in lines[start : index + 1]:
        years.extend(_years_from_line(line))
    # Preserve order but drop duplicates
    seen: set[int] = set()
    ordered: list[int] = []
    for year in years:
        if year not in seen:
            seen.add(year)
            ordered.append(year)
    return ordered


def _pair_years_values(years: list[int], values: list[float]) -> list[tuple[int, float]]:
    """Align year and value lists from a table row or inline sentence."""
    if not years or not values:
        return []

    if len(years) == len(values):
        return list(zip(years, values))
    if len(years) == 1:
        return [(years[0], values[0])]
    if len(values) < len(years):
        return list(zip(years[-len(values) :], values))
    return list(zip(years, values[-len(years) :]))


def _collect_metric_rows(text: str, metric_key: str) -> list[dict]:
    """
    Scan line-by-line for a metric keyword paired with year(s) and value(s).

    Handles table-style rows (years on the header line, values on the next)
    and inline prose (e.g. "Revenue was ₹50,000 crore in FY2024").
    """
    rows: list[dict] = []
    seen: set[tuple[int, str]] = set()
    lines = text.splitlines()

    for index, line in enumerate(lines):
        if not _line_matches_metric(line, metric_key):
            continue

        years = _years_from_context(lines, index)
        year_set = set(years)
        values = _values_from_line(line, metric_key=metric_key, known_years=year_set)
        if not values:
            continue

        for year, value in _pair_years_values(years, values):
            if not _is_plausible_metric_value(value, unit=None, known_years=year_set | {year}):
                continue
            key = (year, metric_key)
            if key in seen:
                continue
            seen.add(key)
            rows.append({"year": year, metric_key: value})

    return rows


def extract_financial_metrics(text: str) -> pd.DataFrame:
    """
    Scan document text for common financial line items and values.

    Args:
        text: Full cleaned report text.

    Returns:
        DataFrame with columns: year, revenue, profit, debt, assets.
    """
    if not text or not text.strip():
        return _empty_metrics_df()

    frames: list[pd.DataFrame] = []
    for metric in ("revenue", "profit", "debt", "assets"):
        rows = _collect_metric_rows(text, metric)
        if rows:
            frames.append(pd.DataFrame(rows))

    if not frames:
        return _empty_metrics_df()

    combined = frames[0]
    for frame in frames[1:]:
        combined = combined.merge(frame, on="year", how="outer")

    combined = combined.sort_values("year").reset_index(drop=True)
    for col in ("revenue", "profit", "debt", "assets"):
        if col not in combined.columns:
            combined[col] = pd.NA

    combined = _sanitize_metrics_df(combined)
    return combined[["year", "revenue", "profit", "debt", "assets"]]


def _sanitize_metrics_df(df: pd.DataFrame) -> pd.DataFrame:
    """Drop values that equal the row year or look like mis-parsed dates."""
    cleaned = df.copy()
    for col in ("revenue", "profit", "debt", "assets"):
        if col not in cleaned.columns:
            continue
        for idx, row in cleaned.iterrows():
            val = row[col]
            if pd.isna(val):
                continue
            year = row["year"]
            if val == year or (1990 <= val <= 2035 and val == int(val)):
                cleaned.at[idx, col] = pd.NA
    return cleaned


def _empty_metrics_df() -> pd.DataFrame:
    return pd.DataFrame(columns=["year", "revenue", "profit", "debt", "assets"])


def extract_revenue_series(text: str) -> pd.DataFrame:
    """Extract multi-year revenue figures."""
    metrics = extract_financial_metrics(text)
    if metrics.empty or metrics["revenue"].isna().all():
        return pd.DataFrame(columns=["year", "revenue"])
    out = metrics[["year", "revenue"]].dropna(subset=["revenue"])
    return out.reset_index(drop=True)


def extract_profit_series(text: str) -> pd.DataFrame:
    """Extract net profit / PAT figures across years."""
    metrics = extract_financial_metrics(text)
    if metrics.empty or metrics["profit"].isna().all():
        return pd.DataFrame(columns=["year", "profit"])
    out = metrics[["year", "profit"]].dropna(subset=["profit"])
    return out.reset_index(drop=True)


def extract_debt_series(text: str) -> pd.DataFrame:
    """Extract total debt / borrowings across years."""
    metrics = extract_financial_metrics(text)
    if metrics.empty or metrics["debt"].isna().all():
        return pd.DataFrame(columns=["year", "debt"])
    out = metrics[["year", "debt"]].dropna(subset=["debt"])
    return out.reset_index(drop=True)


def save_metrics_to_disk(df: pd.DataFrame, report_id: str) -> Path:
    """
    Persist extracted metrics as CSV under data/extracted/.

    Args:
        df: Financial metrics DataFrame.
        report_id: Identifier derived from uploaded filename.

    Returns:
        Path to the saved CSV file.
    """
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    path = EXTRACTED_DIR / f"{report_id}_metrics.csv"
    df.to_csv(path, index=False)
    return path


def load_metrics_from_disk(report_id: str) -> pd.DataFrame:
    """Load previously extracted metrics for a report, or an empty DataFrame."""
    path = EXTRACTED_DIR / f"{report_id}_metrics.csv"
    if not path.exists():
        return _empty_metrics_df()
    return pd.read_csv(path)


def has_extractable_data(df: pd.DataFrame, column: str) -> bool:
    """
    Check whether a metric column has enough data to render a chart (≥ 1 point).

    Args:
        df: Financial metrics DataFrame.
        column: Metric column name (revenue, profit, debt).

    Returns:
        True if charting is possible for that column.
    """
    if df is None or df.empty or column not in df.columns:
        return False
    return df[column].notna().sum() >= 1
