"""
Upload → Ingest Pipeline Orchestrator.

Runs Steps 2–6 and Step 9 when a user uploads a PDF:
  2. Parse PDF → text
  3. Clean text
  4. Chunk text
  5. Generate embeddings
  6. Store in ChromaDB
  9. Extract financial metrics → pandas CSV
"""

from pathlib import Path

from src.config import UPLOADS_DIR
from src.extraction.financial_extractor import extract_financial_metrics, save_metrics_to_disk
from src.ingestion.chunker import chunk_report
from src.ingestion.embeddings import embed_documents, get_embedding_model
from src.ingestion.pdf_parser import extract_text_by_page
from src.ingestion.preprocessor import clean_text
from src.ingestion.vector_store import (
    create_vector_store,
    sanitize_collection_name,
    save_vector_store,
)


class IngestionError(Exception):
    """Raised when the ingestion pipeline fails."""


def save_uploaded_pdf(uploaded_file, filename: str) -> Path:
    """
    Save a Streamlit UploadedFile to data/uploads/.

    Args:
        uploaded_file: Streamlit file uploader object.
        filename: Target filename (e.g. Reliance_Annual_Report_2024.pdf).

    Returns:
        Path to the saved PDF.
    """
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = UPLOADS_DIR / filename

    try:
        pdf_path.write_bytes(uploaded_file.getbuffer())
    except Exception as exc:
        raise IngestionError(f"Failed to save PDF: {exc}") from exc

    return pdf_path


def get_report_id(filename: str) -> str:
    """
    Derive a stable Chroma collection name from the uploaded filename.

    Args:
        filename: Original PDF filename.

    Returns:
        Sanitized collection identifier.
    """
    return sanitize_collection_name(filename)


def run_ingestion_pipeline(pdf_path: Path) -> dict:
    """
    Execute the full ingestion pipeline for one uploaded report.

    Args:
        pdf_path: Path to the saved PDF on disk.

    Returns:
        Dict with report_id, filename, page_count, chunk_count.

    Raises:
        IngestionError: If any step fails.
    """
    if not pdf_path.exists():
        raise IngestionError(f"PDF not found: {pdf_path}")

    filename = pdf_path.name
    collection_name = get_report_id(filename)

    try:
        # Step 2 — PDF → raw text (single pass — no double file read)
        pages = extract_text_by_page(pdf_path)
        page_count = len(pages)
        raw_text = "\n\n".join(pages)

        # Step 3 — clean text
        cleaned_text = clean_text(raw_text)
        if not cleaned_text.strip():
            raise IngestionError("No text could be extracted from this PDF.")

        # Step 4 — split into chunks
        chunks = chunk_report(cleaned_text, filename)
        if not chunks:
            raise IngestionError("Document produced no chunks after processing.")

        # Step 5 — generate embeddings (reuse pre-loaded model if available)
        model = get_embedding_model()
        embedded_docs = embed_documents(chunks, embedding_model=model)

        # Step 6 — store in ChromaDB
        vector_store = create_vector_store(embedded_docs, collection_name)
        save_vector_store(vector_store, collection_name)

        # Step 9 — extract financial metrics (regex) → pandas CSV
        metrics_df = extract_financial_metrics(cleaned_text)
        save_metrics_to_disk(metrics_df, collection_name)

    except IngestionError:
        raise
    except Exception as exc:
        raise IngestionError(f"Ingestion failed: {exc}") from exc

    return {
        "report_id": collection_name,
        "filename": filename,
        "page_count": page_count,
        "chunk_count": len(chunks),
        "metrics_df": metrics_df,
    }
