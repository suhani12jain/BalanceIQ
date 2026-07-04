"""
Step 1 — Upload UI.

PDF file picker and upload button. Triggers ingestion pipeline on submit.
"""

import streamlit as st


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
        else:
            # TODO: pipeline.ingest.save_uploaded_pdf → run_ingestion_pipeline
            st.info("Upload received. Ingestion pipeline not implemented yet.")
