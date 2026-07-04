"""
Step 2 — PDF Parsing (PyMuPDF).

Converts uploaded annual report PDFs into raw text strings.
"""

from pathlib import Path


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract all text from a PDF file, page by page, into one string.

    Args:
        pdf_path: Path to the PDF file on disk.

    Returns:
        Concatenated text from all pages.
    """
    # TODO: Open PDF with fitz, iterate pages, extract text
    pass


def extract_text_by_page(pdf_path: Path) -> list[str]:
    """
    Extract text from each page separately.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of strings, one per page.
    """
    # TODO: Return per-page text list
    pass


def get_page_count(pdf_path: Path) -> int:
    """
    Return the total number of pages in the PDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Page count.
    """
    # TODO: Open PDF and return len(doc)
    pass
