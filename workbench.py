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
If you work in model risk or compliance, this probably feels very familiar.

---

Sarah is a compliance officer at a bank.  
She told me, “I deal with this kind of call almost every week.”

Last week, a customer filed a complaint:

He applied for a $9,500 used car loan, and the system rejected him automatically.

On the phone he said:  
“I gave you everything. Why was I rejected? At least tell me why.”

---

Now the pressure was on Sarah.

Under regulation,  
she cannot just say “the model decided.”

She needs something explainable, documentable, and auditable.

---

She ran the case through PHL.

Here is what stood out:

- The application sat right at the decision boundary  
- The model showed high sensitivity  
- The internal representation was compressed (low effective rank)  
- The spectrum showed strong feature concentration  

---

What the tool gave her was more than a score:

- A clear risk signal: MEDIUM risk
- A concrete action: trigger human review
- A structured explanation she could document

---

That helped her do two things immediately:

1. Respond clearly to the customer  
2. Meet internal audit and regulatory expectations  

---

Sarah later said:

“What matters is not just which feature matters.  
It's knowing when the model itself becomes unstable.  
That's what makes this usable for compliance.”

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
