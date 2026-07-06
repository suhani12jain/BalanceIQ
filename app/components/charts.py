"""
Step 10 & 18 — Charts UI.

Displays revenue, profit, and debt trend charts from extracted metrics.
"""

import streamlit as st

from src.extraction.financial_extractor import load_metrics_from_disk
from src.visualization.charts import get_available_charts


def render() -> None:
    """Render the financial charts section."""
    st.header("Financial Highlights")
    st.caption("Revenue, profit, and debt trends from the uploaded report.")

    report_id = st.session_state.get("report_id")
    if not report_id:
        st.info("Upload and index an annual report to generate charts.")
        return

    filename = st.session_state.get("filename", report_id)
    st.info(f"Showing charts for: **{filename}**")

    metrics_df = st.session_state.get("metrics_df")
    if st.session_state.get("metrics_report_id") != report_id or metrics_df is None:
        metrics_df = load_metrics_from_disk(report_id)
        st.session_state.metrics_df = metrics_df
        st.session_state.metrics_report_id = report_id
        st.info("Upload and index an annual report to generate charts.")
        return

    charts = get_available_charts(metrics_df)
    if not charts:
        st.warning(
            "Metrics were extracted but there is not enough multi-year data "
            "to plot trends (need ≥ 2 data points per metric)."
        )
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        return

    cols = st.columns(min(len(charts), 3))
    for col, (title, fig) in zip(cols, charts):
        with col:
            st.subheader(title)
            st.pyplot(fig, use_container_width=True)
