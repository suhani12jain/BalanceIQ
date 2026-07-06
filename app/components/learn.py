"""
Step 11 & 18 — Learn / Glossary UI.

Explains financial terms (EBITDA, Cash Flow, ROE, etc.) on demand.
"""

import streamlit as st

from src.glossary.terms import explain_term, get_learn_topics


def render() -> None:
    """Render the financial literacy / Learn section."""
    st.header("Learn")
    st.caption("What is EBITDA? Cash Flow? ROE? Tap a term to learn.")

    topics = get_learn_topics()
    selected = st.selectbox(
        "Choose a term",
        options=[""] + topics,
        format_func=lambda x: "Select a term..." if x == "" else x,
        key="learn_term_select",
    )

    if selected:
        explanation = explain_term(selected)
        st.markdown(f"**{selected}** — {explanation}")
