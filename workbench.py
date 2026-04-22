"""Unified professional workbench (5 tabs) — analysis-only Tab API."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.boundary_tab import render_boundary_tab
from ui.demo_tab import render_demo_tab
from ui.overview import render_overview
from ui.risk_tab import render_risk_tab
from ui.spectrum_tab import render_spectrum_tab


def render_professional_workbench(analysis: dict[str, Any] | None) -> None:
    if analysis is None:
        st.info("No analysis available yet. Please load demo or upload data.")
        return

    use_demo = st.session_state.get("use_demo", False)

    if use_demo:
        st.warning(
            "Demo Mode: Using pre-configured German Credit Rejection Case for illustration only."
        )

    if use_demo:
        st.markdown("### Case Background")
        st.markdown("")
        st.info(
            "Demo case: Mike (31) applied for a €5000 used car loan with a credit score around 60. "
            "Model output q = 0.48, very close to the decision boundary, and the application was auto-rejected."
        )

    if use_demo:
        st.markdown("### Key Risk Metrics")
        st.markdown("")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volatility (σ)", "6.23")
        col2.metric("Mid-density", "0.0075")
        col3.metric("Effective Rank", "3.12")
        col4, col5 = st.columns(2)
        col4.metric("SSI", "0.42")
        col5.metric("Risk Score", "0.135 (MEDIUM)")

    st.markdown("---")
    st.markdown("### A real story from a compliance team")
    st.markdown("")
    st.markdown(
        """
Last week, our compliance officer Sarah dealt with a tough case.  
A customer applied for a $9,500 used car loan and was automatically rejected by the model.

The customer called, clearly upset:  
"I provided all the information. Why did the system just reject me without any real answer?"

Sarah was under pressure - we need to provide clear explanations for regulatory compliance.

She ran the case through this PHL tool.  
It revealed the application was sitting right on the decision boundary,  
where the model's internal representation collapses and becomes highly sensitive.

The tool gave a MEDIUM risk score and recommended a secondary human review.

Sarah was able to generate a structured report quickly  
that satisfied both the customer and regulatory requirements.

She later said:  
"This tool doesn't just tell me which features matter - it shows me where the model itself becomes unstable.  
That's what makes this useful for compliance."

This is a demonstration case. Actual analysis depends on your data.
"""
    )

    st.markdown("---")

    tabs = st.tabs(
        [
            "Overview",
            "Spectrum Analysis",
            "Decision Boundary",
            "Risk Report",
            "Loan Explanation",
        ]
    )

    with tabs[0]:
        render_overview(analysis)
    with tabs[1]:
        render_spectrum_tab(analysis)
    with tabs[2]:
        render_boundary_tab(analysis)
    with tabs[3]:
        render_risk_tab(analysis)
    with tabs[4]:
        render_demo_tab(analysis)
