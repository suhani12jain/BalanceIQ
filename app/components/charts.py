"""
Step 16 & 18 — Charts UI.

Displays revenue, profit, and debt trend charts from extracted metrics.
"""

import streamlit as st


def render() -> None:
    """Render the financial charts section."""
    st.header("Financial Highlights")
    st.caption("Revenue, profit, and debt trends from the uploaded report.")

    # TODO: Load metrics from data/extracted/ → visualization.charts.get_available_charts
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Revenue Trend")
        st.empty()
    with col2:
        st.subheader("Profit Trend")
        st.empty()
    with col3:
        st.subheader("Debt Trend")
        st.empty()
