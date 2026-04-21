import streamlit as st


def render_overview(model):
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

    if model is None:
        st.warning("Please upload a model to begin analysis.")
