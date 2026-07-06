"""
Step 1 — Upload UI.

PDF file picker and upload button. Triggers ingestion pipeline on submit.
"""

import streamlit as st

from src import config
from src.pipeline.ingest import IngestionError, run_ingestion_pipeline, save_uploaded_pdf


def render() -> None:
    """Render the PDF upload section."""
    st.header("Upload Annual Report")
    st.caption("Example: Reliance_Annual_Report_2024.pdf")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload the company's annual report or financial statement.",
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        st.write(f"**Selected:** {uploaded_file.name}")

    if st.button("Upload", type="primary", key="upload_button"):
        if uploaded_file is None:
            st.error("Please choose a PDF file first.")
        elif not config.validate_config():
            st.error("Set GROQ_API_KEY in .env before uploading.")
        else:
            try:
                with st.status("Processing report…", expanded=True) as status:
                    status.write("Saving PDF…")
                    pdf_path = save_uploaded_pdf(uploaded_file, uploaded_file.name)
                    status.write("Parsing, chunking, embedding…")
                    status.write("Extracting financial metrics…")
                    result = run_ingestion_pipeline(pdf_path)
                    status.update(label="Done!", state="complete", expanded=False)

                st.session_state.indexed = True
                st.session_state.report_id = result["report_id"]
                st.session_state.filename = result["filename"]
                st.session_state.chunk_count = result["chunk_count"]
                st.session_state.metrics_df = result["metrics_df"]
                st.session_state.metrics_report_id = result["report_id"]
                st.success(
                    f"Indexed **{result['filename']}** — "
                    f"{result['page_count']} pages, {result['chunk_count']} chunks."
                )
            except IngestionError as exc:
                st.error(str(exc))
