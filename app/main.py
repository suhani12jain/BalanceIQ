"""
FinSum — Streamlit frontend (Step 18).

Entry point for the Financial Statement Analysis app.
Run with: streamlit run app/main.py
"""

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config  # noqa: E402
from app.components import upload, chat, charts, news, learn  # noqa: E402


st.set_page_config(
    page_title="FinSum — Financial Statement Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_sidebar() -> None:
    """Sidebar with app info and pipeline status."""
    with st.sidebar:
        st.title("FinSum")
        st.caption("Financial Statement Analysis for Laymen")
        st.divider()

        st.subheader("Pipeline")
        st.markdown(
            """
            1. **Upload** PDF
            2. **Parse & index** (ChromaDB)
            3. **Ask** questions
            4. **View** answer + charts + news
            """
        )

        st.divider()
        st.subheader("Status")
        if config.OPENAI_API_KEY:
            st.success("API key loaded")
        else:
            st.warning("Set OPENAI_API_KEY in .env")


def main() -> None:
    """Main app — Step 18 final output layout."""
    render_sidebar()

    st.title("📊 FinSum")
    st.markdown("**Understand annual reports — no finance degree required.**")

    tab_upload, tab_chat, tab_charts, tab_news, tab_learn = st.tabs(
        ["Upload", "Q&A", "Charts", "News", "Learn"]
    )

    with tab_upload:
        upload.render()

    with tab_chat:
        chat.render()

    with tab_charts:
        charts.render()

    with tab_news:
        news.render()

    with tab_learn:
        learn.render()


if __name__ == "__main__":
    main()
