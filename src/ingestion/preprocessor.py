"""
Step 3 — Text Cleaning (Preprocessor).

Single responsibility: raw PDF text → clean text string.

    One Huge String (from pdf_parser)
              │
              ▼
         Text Processor
              │
              ▼
         Clean Text String

Removes: page numbers, repeated headers/footers, extra spaces, blank lines.
Does NOT: split into chunks, embed, or call GPT.
Chunking is handled by chunker.py (Step 4).
"""

import re
import unicodedata
from collections import Counter


def remove_page_numbers(text: str) -> str:
    """
    Remove standalone page number lines (e.g. "Page 124", "Page 2", "124").

    Args:
        text: Document text.

    Returns:
        Text with page-number lines removed.
    """
    # "Page 15", "page 3", "PAGE 124"
    text = re.sub(r"^\s*Page\s+\d+\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)

    # Standalone numbers on their own line (typical footer page numbers)
    text = re.sub(r"^\s*\d{1,4}\s*$", "", text, flags=re.MULTILINE)

    # Separator lines made only of dashes or underscores
    text = re.sub(r"^\s*[-_]{3,}\s*$", "", text, flags=re.MULTILINE)

    return text


def remove_repeated_headers(text: str, min_occurrences: int = 3) -> str:
    """
    Detect and strip lines that repeat across pages (headers/footers).

    Annual reports repeat lines like "Reliance Annual Report" or "Confidential"
    on almost every page — this removes them.

    Args:
        text: Full document text.
        min_occurrences: Minimum repeats before a line is treated as noise.

    Returns:
        Text with repeated headers/footers removed.
    """
    lines = text.split("\n")

    # Count how often each non-empty stripped line appears
    stripped = [line.strip() for line in lines if line.strip()]
    line_counts = Counter(stripped)

    # Flag short-ish lines that repeat often (typical header/footer pattern)
    repeated_lines = {
        line
        for line, count in line_counts.items()
        if count >= min_occurrences and 3 <= len(line) <= 120
    }

    cleaned_lines = [
        line for line in lines if line.strip() not in repeated_lines
    ]

    return "\n".join(cleaned_lines)


def _normalize_line_endings(text: str) -> str:
    """Convert Windows/Mac line endings to Unix \\n."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _collapse_blank_lines(text: str) -> str:
    """Replace 3+ consecutive blank lines with a single blank line."""
    return re.sub(r"\n{3,}", "\n\n", text)


def _collapse_extra_spaces(text: str) -> str:
    """Collapse multiple spaces/tabs within a line to a single space."""
    lines = []
    for line in text.split("\n"):
        # Preserve empty lines; only collapse spaces inside non-empty lines
        if line.strip():
            lines.append(re.sub(r"[ \t]+", " ", line.strip()))
        else:
            lines.append("")
    return "\n".join(lines)


def normalize_financial_notation(text: str) -> str:
    """
    Standardize currency symbols and common Indian financial notation.

    Examples:
        Rs. 500 Cr  →  ₹500 Cr
        9,00,000 Crore  →  kept readable with consistent spacing

    Args:
        text: Cleaned document text.

    Returns:
        Text with normalized financial notation.
    """
    # Normalize unicode (e.g. combine stray combining characters)
    text = unicodedata.normalize("NFKC", text)

    # Common rupee spellings → ₹
    text = re.sub(r"\bRs\.?\s*", "₹", text)
    text = re.sub(r"\bINR\s*", "₹", text)

    # Normalize crore / lakh abbreviations
    text = re.sub(r"\bCrores?\b", "Cr", text, flags=re.IGNORECASE)
    text = re.sub(r"\bLakhs?\b", "L", text, flags=re.IGNORECASE)

    # Ensure a space between ₹ and the number
    text = re.sub(r"₹\s*(\d)", r"₹\1", text)

    return text


def clean_text(raw_text: str) -> str:
    """
    Apply the full cleaning pipeline to raw PDF text.

    Pipeline:
        1. Normalize line endings
        2. Remove page numbers and separator lines
        3. Remove repeated headers/footers
        4. Collapse extra blank lines
        5. Collapse extra spaces within lines
        6. Normalize financial notation (₹, Cr, L)
        7. Strip leading/trailing whitespace

    Args:
        raw_text: Unprocessed text from pdf_parser.extract_text_from_pdf().

    Returns:
        Cleaned text string, ready for chunker.py.
    """
    if not raw_text or not raw_text.strip():
        return ""

    text = raw_text

    # Step 1 — unify line endings
    text = _normalize_line_endings(text)

    # Step 2 — remove page numbers and dash separators
    text = remove_page_numbers(text)

    # Step 3 — strip repeated header/footer lines
    text = remove_repeated_headers(text)

    # Step 4 — remove excessive blank lines
    text = _collapse_blank_lines(text)

    # Step 5 — remove extra spaces within each line
    text = _collapse_extra_spaces(text)

    # Step 6 — normalize ₹, Cr, L notation
    text = normalize_financial_notation(text)

    # Step 7 — final trim
    return text.strip()
