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
        st.markdown("### 📘 Case Background")
        st.info(
            "Demo Case: 张伟（31岁）申请 €5000 二手车贷款，信用分 60 分。"
            "模型输出概率 q = 0.48，处于决策边界附近，被自动拒绝。"
        )

    if use_demo:
        st.markdown("### 📊 Key Risk Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volatility (σ)", "6.23")
        col2.metric("Mid-density", "0.0075")
        col3.metric("Effective Rank", "3.12")
        col4, col5 = st.columns(2)
        col4.metric("SSI", "0.42")
        col5.metric("Risk Score", "0.135 (MEDIUM)")

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
