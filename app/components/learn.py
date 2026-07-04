"""
Step 17 & 18 — Learn / Glossary UI.

Explains financial terms (EBITDA, Cash Flow, ROE, etc.) on demand.
"""

import streamlit as st

from src.glossary.terms import get_learn_topics, explain_term


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
        if explanation:
            st.markdown(f"**{selected}** — {explanation}")
        else:
            # TODO: explain_term returns static lookup once implemented
            st.info(f"Explanation for '{selected}' will appear here.")
