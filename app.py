"""
BalanceIQ — Streamlit RAG Application.

Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Project root on Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config  # noqa: E402
from src.ingestion.embeddings import get_embedding_model  # noqa: E402
from src.pipeline.ingest import IngestionError, run_ingestion_pipeline, save_uploaded_pdf  # noqa: E402
from src.rag.chatbot import ChatbotError, ask  # noqa: E402


@st.cache_resource
def _preload_embedding_model():
    """Load the embedding model once at startup (saves ~30s on first PDF upload)."""
    return get_embedding_model()


# --- Page setup ---
st.set_page_config(
    page_title="BalanceIQ — Financial Report Q&A",
    page_icon="📊",
    layout="centered",
)


def _init_session_state() -> None:
    """Initialize Streamlit session variables."""
    defaults = {
        "indexed": False,
        "report_id": None,
        "filename": None,
        "chunk_count": 0,
        "last_answer": None,
        "last_question": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _render_sidebar() -> None:
    """Sidebar — app info and status."""
    with st.sidebar:
        st.title("BalanceIQ")
        st.caption("RAG demo for annual report Q&A")
        st.divider()

        st.markdown("**Pipeline**")
        st.markdown("1. Upload PDF\n2. Index in ChromaDB\n3. Ask questions")

        st.divider()
        if config.validate_config():
            st.success("Gemini API key loaded")
        else:
            st.warning("Set `GOOGLE_API_KEY` in `.env`")

        if st.session_state.indexed:
            st.divider()
            st.markdown("**Indexed report**")
            st.write(st.session_state.filename)
            st.caption(f"{st.session_state.chunk_count} chunks stored")


def _render_upload_section() -> None:
    """PDF upload and ingestion."""
    st.subheader("1. Upload Annual Report")
    st.caption("Upload a company annual report PDF to index it for Q&A.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        st.write(f"Selected: **{uploaded_file.name}**")

    if st.button("Process & Index", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.error("Please select a PDF file first.")
            return

        if not config.validate_config():
            st.error("Set your `GOOGLE_API_KEY` in `.env` before indexing.")
            return

        try:
            status = st.status("Processing your report…", expanded=True)
            status.write("Saving PDF…")
            pdf_path = save_uploaded_pdf(uploaded_file, uploaded_file.name)

            status.write("Parsing & cleaning text…")
            status.write("Chunking document…")
            status.write("Generating embeddings (this step takes the longest)…")
            result = run_ingestion_pipeline(pdf_path)
            status.update(label="Indexing complete!", state="complete", expanded=False)

            st.session_state.indexed = True
            st.session_state.report_id = result["report_id"]
            st.session_state.filename = result["filename"]
            st.session_state.chunk_count = result["chunk_count"]
            st.session_state.last_answer = None
            st.session_state.last_question = None

            st.success(
                f"Indexed **{result['filename']}** — "
                f"{result['page_count']} pages, {result['chunk_count']} chunks."
            )

        except IngestionError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Unexpected error during indexing: {exc}")


def _render_chat_section() -> None:
    """Question input and chatbot answer."""
    st.subheader("2. Ask a Question")

    if not st.session_state.indexed:
        st.info("Upload and index a report above before asking questions.")
        return

    question = st.text_area(
        "Your question",
        placeholder='e.g. "What was the company\'s revenue?" or "Who is the CEO?"',
        height=100,
        label_visibility="collapsed",
    )

    if st.button("Get Answer", type="primary", use_container_width=True):
        if not question.strip():
            st.error("Please enter a question.")
            return

        if not config.validate_config():
            st.error("Set your `GOOGLE_API_KEY` in `.env` to get answers.")
            return

        try:
            with st.spinner("Searching report and generating answer…"):
                response = ask(
                    question=question.strip(),
                    collection_name=st.session_state.report_id,
                )

            st.session_state.last_question = question.strip()
            st.session_state.last_answer = response.answer

        except ChatbotError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")

    if st.session_state.last_answer:
        st.divider()
        st.subheader("Answer")
        if st.session_state.last_question:
            st.markdown(f"**Q:** {st.session_state.last_question}")
        st.markdown(st.session_state.last_answer)


def main() -> None:
    """App entry point."""
    _preload_embedding_model()  # warm up model before first upload
    _init_session_state()
    _render_sidebar()

    st.title("📊 BalanceIQ")
    st.markdown("Upload an annual report and ask questions in plain English.")

    _render_upload_section()
    st.divider()
    _render_chat_section()


if __name__ == "__main__":
    main()
