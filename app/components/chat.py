"""
Steps 10 & 18 — Q&A Chat UI.

Question input and RAG answer display (report questions only).
"""

import streamlit as st

from src import config
from src.rag.chatbot import ChatbotError, ask


def render() -> None:
    """Render the question-and-answer section."""
    st.header("Ask a Question")
    st.caption('Example: "What was revenue in 2024?" or "Why did profits decrease?"')

    question = st.text_input(
        "Your question",
        placeholder="Type your question here...",
        key="user_query",
    )

    if st.button("Ask", type="primary", key="ask_button"):
        if not question.strip():
            st.error("Please enter a question.")
        elif not st.session_state.get("indexed"):
            st.error("Please upload and index a report first.")
        elif not config.validate_config():
            st.error("Set GROQ_API_KEY in .env to get answers.")
        else:
            try:
                with st.spinner("Searching report and generating answer…"):
                    response = ask(
                        question.strip(),
                        st.session_state.report_id,
                    )
                st.session_state.last_question = question.strip()
                st.session_state.last_answer = response.answer
                st.session_state.last_retrieved_count = len(response.retrieved_chunks)
            except ChatbotError as exc:
                st.error(str(exc))

    st.divider()
    st.subheader("AI Answer")
    if st.session_state.get("last_answer"):
        if st.session_state.get("last_question"):
            st.markdown(f"**Q:** {st.session_state.last_question}")
        st.markdown(st.session_state.last_answer)
        count = st.session_state.get("last_retrieved_count")
        if count:
            st.caption(f"Based on {count} sections retrieved from the uploaded report.")
    else:
        st.caption("Your answer will appear here.")
