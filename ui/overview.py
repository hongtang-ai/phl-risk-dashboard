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
