"""
Step 8 & 18 — Related News UI.

Shows latest news, earnings, and market updates fetched externally.
"""

import streamlit as st


def render() -> None:
    """Render the related news section."""
    st.header("Related News")
    st.caption("Latest headlines beyond the annual report.")

    # TODO: Load from data/cache/ or external.news_fetcher
    st.empty()
