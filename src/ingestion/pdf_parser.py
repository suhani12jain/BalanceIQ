"""
Step 2 — PDF Parsing (PyMuPDF / fitz).

Single responsibility: PDF file → plain text string.

    Reliance_Annual_Report_2024.pdf
              │
              ▼
         PDF Parser
              │
              ▼
         Plain Text

Does NOT: clean text, chunk, embed, store vectors, or call GPT.
Those belong to later modules (preprocessor, chunker, etc.).
"""

from pathlib import Path

import fitz  # PyMuPDF — opens and reads .pdf files


def _open_pdf(pdf_path: Path) -> fitz.Document:
    """
    Step 3 — Open the PDF with PyMuPDF.

    Validates the path, then opens the file like Word opens a .docx.

    Args:
        pdf_path: Path to the saved PDF on disk.

    Returns:
        Open PyMuPDF Document (caller must close it).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the path is invalid or the file cannot be opened.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Not a file: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {pdf_path.name}")

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise ValueError(f"Could not open PDF '{pdf_path.name}': {exc}") from exc

    if doc.page_count == 0:
        doc.close()
        raise ValueError(f"PDF has no pages: {pdf_path.name}")

    return doc


def get_page_count(pdf_path: Path) -> int:
    """
    Step 4 — Count the pages (e.g. Total Pages = 287).

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Total number of pages in the document.
    """
    doc = _open_pdf(pdf_path)
    try:
        return doc.page_count
    finally:
        doc.close()


def extract_text_by_page(pdf_path: Path) -> list[str]:
    """
    Step 5 — Read each page and extract text.

    Loops Page 1 → Page N. Each page becomes one string.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of page texts, e.g. ["Revenue increased...", "Operating expenses..."]
    """
    doc = _open_pdf(pdf_path)
    pages: list[str] = []

    try:
        for page_number in range(doc.page_count):
            page = doc[page_number]
            # get_text("text") returns plain text from the page layout
            page_text = page.get_text("text") or ""
            pages.append(page_text)
    finally:
        doc.close()

    return pages


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Steps 6 & 7 — Combine all pages into one string and return it.

    Example output:
        Revenue : ₹500 Cr

        Net Profit : ₹120 Cr

        Debt : ₹50 Cr

    Args:
        pdf_path: Path to the PDF file on disk.

    Returns:
        Full report text as a single string (raw, not cleaned).
    """
    pages = extract_text_by_page(pdf_path)

    # Double newline keeps page boundaries for the preprocessor (Step 3)
    return "\n\n".join(pages)
