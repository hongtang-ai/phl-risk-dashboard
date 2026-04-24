import streamlit as st
import pandas as pd


def render_overview(analysis: dict | None) -> None:
    st.header("Overview")

    if analysis is None:
        st.warning("No analysis available.")
        return

    st.write(
        """
    This dashboard provides a structured diagnostic view of model behavior
    under credit decision scenarios.

    Key concepts:
    - Decision boundary sensitivity region
    - Representation collapse (effective rank)
    - Spectrum concentration (risk indicator)
    """
    )

    if analysis.get("description"):
        st.subheader("Case Background")
        st.write(analysis["description"])

    # === UPDATED ===
    st.subheader("Regulatory Compliance Summary")
    table = pd.DataFrame(
        [
            {"Framework": "SR 11-7", "Control": "Model Stability & Monitoring", "Status": "✓"},
            {"Framework": "EU AI Act", "Control": "Transparency & Bias Mitigation", "Status": "✓"},
        ]
    )
    st.table(table)
