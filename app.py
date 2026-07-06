"""
BalanceIQ — Streamlit RAG Application.

Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Project root on Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config  # noqa: E402
from src.extraction.financial_extractor import load_metrics_from_disk  # noqa: E402
from src.glossary.terms import explain_term, get_learn_topics  # noqa: E402
from src.ingestion.embeddings import get_embedding_model  # noqa: E402
from src.pipeline.ingest import IngestionError, run_ingestion_pipeline, save_uploaded_pdf  # noqa: E402
from src.rag.chatbot import ChatbotError, ask  # noqa: E402
from src.visualization.charts import get_available_charts  # noqa: E402


@st.cache_resource
def _preload_embedding_model():
    """Load the embedding model once at startup (saves ~30s on first PDF upload)."""
    return get_embedding_model()


st.set_page_config(
    page_title="BalanceIQ — Financial Report Q&A",
    page_icon="📊",
    layout="wide",
)


def _init_session_state() -> None:
    """Initialize Streamlit session variables."""
    defaults = {
        "indexed": False,
        "report_id": None,
        "filename": None,
        "chunk_count": 0,
        "metrics_df": None,
        "metrics_report_id": None,
        "last_answer": None,
        "last_question": None,
        "last_retrieved_count": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _get_metrics_df() -> pd.DataFrame | None:
    """Load metrics for the currently indexed report only."""
    report_id = st.session_state.get("report_id")
    if not report_id:
        return None

    cached_id = st.session_state.get("metrics_report_id")
    cached_df = st.session_state.get("metrics_df")
    if cached_id == report_id and cached_df is not None and not cached_df.empty:
        return cached_df

    metrics_df = load_metrics_from_disk(report_id)
    st.session_state.metrics_df = metrics_df
    st.session_state.metrics_report_id = report_id
    return metrics_df if not metrics_df.empty else None


def _render_sidebar() -> None:
    """Sidebar — app info and status."""
    with st.sidebar:
        st.title("BalanceIQ")
        st.caption("Financial report analysis for everyone")
        st.divider()

        st.markdown("**How to use**")
        st.markdown(
            "1. **Metrics** — upload & extract data\n"
            "2. **Q&A** — ask about the report\n"
            "3. **Charts** — view trends\n"
            "4. **Learn** — glossary of terms"
        )

        st.divider()
        if config.validate_config():
            st.success("Groq API key loaded")
        else:
            st.warning("Set `GROQ_API_KEY` in `.env`")

        if st.session_state.indexed:
            st.divider()
            st.markdown("**Indexed report**")
            st.write(st.session_state.filename)
            st.caption(f"{st.session_state.chunk_count} chunks stored")


def _render_metrics_table(metrics_df: pd.DataFrame) -> None:
    """Show extracted metrics as a formatted table."""
    display_df = metrics_df.copy()
    for col in ("revenue", "profit", "debt", "assets"):
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda v: f"₹{v:,.0f} cr" if pd.notna(v) else "—"
            )
    st.dataframe(display_df, width="stretch", hide_index=True)


def _render_upload_and_metrics_tab() -> None:
    """Tab 1 — PDF upload and extracted financial metrics."""
    st.header("📋 Metrics & Data Extraction")
    st.markdown(
        "Upload an annual report PDF. BalanceIQ will index it for Q&A and "
        "**extract Revenue, Profit, Debt, and Assets** using regex parsing."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Company annual report or financial statement",
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        st.write(f"**Selected:** {uploaded_file.name}")
        if (
            st.session_state.indexed
            and st.session_state.filename
            and uploaded_file.name != st.session_state.filename
        ):
            st.warning(
                f"You selected a new file. Click **Process & Index** to replace "
                f"**{st.session_state.filename}** and refresh charts."
            )

    if st.button("Process & Index", type="primary", key="process_button"):
        if uploaded_file is None:
            st.error("Please select a PDF file first.")
            return

        if not config.validate_config():
            st.error("Set your `GROQ_API_KEY` in `.env` before indexing.")
            return

        try:
            status = st.status("Processing your report…", expanded=True)
            status.write("Saving PDF…")
            pdf_path = save_uploaded_pdf(uploaded_file, uploaded_file.name)

            status.write("Parsing & cleaning text…")
            status.write("Chunking document…")
            status.write("Generating embeddings (this step takes the longest)…")
            status.write("Extracting financial metrics…")
            result = run_ingestion_pipeline(pdf_path)
            status.update(label="Indexing complete!", state="complete", expanded=False)

            st.session_state.indexed = True
            st.session_state.report_id = result["report_id"]
            st.session_state.filename = result["filename"]
            st.session_state.chunk_count = result["chunk_count"]
            st.session_state.metrics_df = result["metrics_df"]
            st.session_state.metrics_report_id = result["report_id"]
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

    st.divider()
    st.subheader("Extracted Financial Data")

    if not st.session_state.indexed:
        st.info("Upload and process a report above to see extracted metrics.")
        return

    metrics_df = _get_metrics_df()
    if metrics_df is None or metrics_df.empty:
        st.warning(
            "No financial metrics could be extracted from this report. "
            "The PDF text may not contain recognizable table formats."
        )
        return

    st.caption(f"Source: **{st.session_state.filename}**")
    _render_metrics_table(metrics_df)

    cols = st.columns(4)
    for col, metric_col in zip(cols, ("revenue", "profit", "debt", "assets")):
        label = metric_col.capitalize()
        if metric_col not in metrics_df.columns or metrics_df[metric_col].notna().sum() == 0:
            col.metric(label, "—")
            continue
        latest = metrics_df.dropna(subset=[metric_col]).sort_values("year").iloc[-1]
        year = int(latest["year"])
        value = latest[metric_col]
        col.metric(label, f"₹{value:,.0f} cr", delta=f"FY {year}", delta_color="off")


def _render_qa_tab() -> None:
    """Tab 2 — Question & answer over the indexed report."""
    st.header("💬 Q&A — Ask About the Report")
    st.markdown(
        "Ask anything about the **uploaded annual report**. "
        "Answers come from the PDF via search + Groq — not from general definitions."
    )

    if not st.session_state.indexed:
        st.info("Go to **Metrics & Data** and upload a report first.")
        return

    question = st.text_area(
        "Your question",
        placeholder='e.g. "What was the company\'s revenue in 2024?"',
        height=120,
        key="qa_question",
    )

    if st.button("Get Answer", type="primary", key="qa_button"):
        if not question.strip():
            st.error("Please enter a question.")
            return

        if not config.validate_config():
            st.error("Set your `GROQ_API_KEY` in `.env` to get answers.")
            return

        try:
            with st.spinner("Searching report and generating answer…"):
                response = ask(
                    question=question.strip(),
                    collection_name=st.session_state.report_id,
                )

            st.session_state.last_question = question.strip()
            st.session_state.last_answer = response.answer
            st.session_state.last_retrieved_count = len(response.retrieved_chunks)

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

        # Show that RAG ran (chunks retrieved from the indexed PDF)
        last_chunks = st.session_state.get("last_retrieved_count")
        if last_chunks is not None and last_chunks > 0:
            st.caption(
                f"Answer generated from **{last_chunks} relevant sections** "
                f"of the uploaded report (RAG pipeline)."
            )


def _render_charts_tab() -> None:
    """Tab 3 — Revenue, profit, and debt trend charts."""
    st.header("📈 Charts & Plots")
    st.markdown(
        "Visual trends for **Revenue**, **Profit**, and **Debt** "
        "extracted from your report."
    )

    if not st.session_state.indexed:
        st.info("Go to **Metrics & Data** and upload a report first.")
        return

    st.info(f"Showing charts for: **{st.session_state.filename}**")

    metrics_df = _get_metrics_df()
    if metrics_df is None or metrics_df.empty:
        st.warning("No metrics available to chart. Try re-uploading the report.")
        return

    charts = get_available_charts(metrics_df)
    if not charts:
        st.warning(
            "Metrics were found but none of Revenue, Profit, or Debt "
            "had usable values. Check the **Metrics & Data** tab."
        )
        _render_metrics_table(metrics_df)
        return

    if len(charts) == 1:
        title, fig = charts[0]
        st.subheader(title)
        st.pyplot(fig, width="stretch")
    elif len(charts) == 2:
        col1, col2 = st.columns(2)
        for col, (title, fig) in zip((col1, col2), charts):
            with col:
                st.subheader(title)
                st.pyplot(fig, width="stretch")
    else:
        col1, col2, col3 = st.columns(3)
        for col, (title, fig) in zip((col1, col2, col3), charts):
            with col:
                st.subheader(title)
                st.pyplot(fig, width="stretch")


def _render_learn_tab() -> None:
    """Tab 4 — Financial literacy glossary."""
    st.header("📚 Learn — Financial Terms")
    st.markdown(
        "New to finance? Pick a term below for a **beginner-friendly explanation**. "
        "No report upload needed."
    )

    topics = get_learn_topics()

    col_select, col_info = st.columns([1, 2])
    with col_select:
        selected = st.selectbox(
            "Choose a term",
            options=topics,
            index=0,
            key="learn_term_select",
        )

    with col_info:
        if selected:
            explanation = explain_term(selected)
            st.markdown(f"### {selected}")
            st.markdown(explanation)

    st.divider()
    st.subheader("All terms at a glance")
    for term in topics:
        with st.expander(f"**{term}**"):
            st.markdown(explain_term(term))

    st.caption("For term definitions (EBITDA, ROE, etc.), use the **Learn** tab.")


def main() -> None:
    """App entry point."""
    _preload_embedding_model()
    _init_session_state()
    _render_sidebar()

    st.title("📊 BalanceIQ")
    st.caption("Understand annual reports — no finance degree required.")

    tab_metrics, tab_qa, tab_charts, tab_learn = st.tabs([
        "📋 Metrics & Data",
        "💬 Q&A",
        "📈 Charts",
        "📚 Learn",
    ])

    with tab_metrics:
        _render_upload_and_metrics_tab()

    with tab_qa:
        _render_qa_tab()

    with tab_charts:
        _render_charts_tab()

    with tab_learn:
        _render_learn_tab()


if __name__ == "__main__":
    main()
