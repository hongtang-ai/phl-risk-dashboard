import streamlit as st


def render_overview(model, analysis):
    st.header("Overview")

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

    if analysis is not None and analysis.get("description"):
        st.subheader("Case Background")
        st.write(analysis["description"])

    if analysis is not None:
        return

    if model is None:
        st.warning("Please upload a model to begin analysis, or load the demo case from the sidebar.")
