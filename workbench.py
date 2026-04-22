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
        st.info(
            "Demo Case: 张伟（31岁）申请 €5000 二手车贷款，信用分 60 分。"
            "模型输出概率 q = 0.48，处于决策边界附近，被自动拒绝。"
        )

    if use_demo:
        st.markdown("### Key Risk Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volatility (σ)", "6.23")
        col2.metric("Mid-density", "0.0075")
        col3.metric("Effective Rank", "3.12")
        col4, col5 = st.columns(2)
        col4.metric("SSI", "0.42")
        col5.metric("Risk Score", "0.135 (MEDIUM)")

    st.markdown("---")
    st.markdown("### Bank Compliance Use Case")
    st.markdown(
        """
If you work in model risk or compliance, this probably feels familiar.

---

“This is exactly the kind of case Sarah deals with.”

Last week, a customer filed a complaint:

He applied for a $9,500 used car loan.  
The system rejected him automatically.

On the phone, he was clearly upset:  
“I gave you everything.  
Why was I rejected? At least tell me why.”

---

Sarah, a compliance officer, now had to answer.

And under regulation,  
she cannot just say “the model decided.”

She needs something explainable.

---

She ran the case through PHL.

Here is what stood out:

- The application sits right at the decision boundary  
- The model shows high sensitivity  
- Internal representation is compressed (low effective rank)  
- Spectrum indicates strong feature concentration  

---

What the tool provided:

- A clear risk signal: MEDIUM risk
- A concrete action: trigger human review
- A structured explanation she could document

---

This helped her do two things:

1. Respond clearly to the customer  
2. Satisfy internal and regulatory expectations  

---

She later said:

“What matters is not just which feature matters.  
It's knowing when the model itself becomes unstable.  
That's what makes this usable.”

---

This is a demo scenario. Actual analysis depends on your data.
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
