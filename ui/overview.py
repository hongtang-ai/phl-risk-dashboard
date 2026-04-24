import streamlit as st


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

    st.subheader("Regulatory Compliance Summary")
    st.markdown(
        "- **SR 11-7 (lightweight alignment)**: Model monitoring includes decision-boundary diagnostics, "
        "sensitivity checks, and audit logging hooks.\n"
        "- **EU AI Act (lightweight alignment)**: Dashboard surfaces explainability, bias snapshot, "
        "and drift indicators for transparency and oversight."
    )
