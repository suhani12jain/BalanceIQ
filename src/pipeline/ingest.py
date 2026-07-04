"""
Upload → Ingest Pipeline Orchestrator.

Runs Steps 2–9 in sequence when a user uploads a PDF:
  2. Parse PDF → text
  3. Clean text
  4. Chunk text
  5. Generate embeddings
  6. Store in ChromaDB
  7. Extract financial metrics → pandas
  8. Fetch external news (optional)
  9. Extract board information
"""

from pathlib import Path


def save_uploaded_pdf(uploaded_file, filename: str) -> Path:
    """
    Save Streamlit UploadedFile to data/uploads/ (Step 1).

    Args:
        uploaded_file: Streamlit file uploader object.
        filename: Target filename (e.g. Reliance_Annual_Report_2024.pdf).

    Returns:
        Path to saved PDF.
    """
    # TODO: Write bytes to UPLOADS_DIR / filename
    pass


def run_ingestion_pipeline(pdf_path: Path) -> dict:
    """
    Execute the full ingestion pipeline for one uploaded report.

    Args:
        pdf_path: Path to saved PDF.

    Returns:
        Dict with keys: report_id, chunk_count, metrics_df, board_df, news_items.
    """
    # TODO: Chain ingestion → extraction → external modules
    pass


def get_report_id(filename: str) -> str:
    """
    Derive a stable report ID from the uploaded filename.

    Args:
        filename: Original PDF filename.

    Returns:
        Sanitized identifier for Chroma collection and extracted data files.
    """
    # TODO: Strip extension, lowercase, replace spaces
    pass
