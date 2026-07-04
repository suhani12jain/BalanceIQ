"""
Steps 10 & 18 — Q&A Chat UI.

Question input, AI answer display, and related context.
"""

import streamlit as st


def render() -> None:
    """Render the question-and-answer section."""
    st.header("Ask a Question")
    st.caption('Example: "Why did profits decrease?" or "Should I invest?"')

    question = st.text_input(
        "Your question",
        placeholder="Type your question here...",
        key="user_query",
    )

    if st.button("Ask", type="primary", key="ask_button"):
        if not question.strip():
            st.error("Please enter a question.")
        else:
            # TODO: pipeline.query.run_query_pipeline
            st.info("RAG pipeline not implemented yet.")

    st.divider()
    st.subheader("AI Answer")
    # TODO: Display answer from st.session_state after pipeline runs
    st.empty()
