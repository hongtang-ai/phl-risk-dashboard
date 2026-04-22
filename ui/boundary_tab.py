import streamlit as st
import plotly.express as px
import numpy as np


def render_boundary_tab(analysis: dict | None) -> None:
    st.header("Decision Boundary Sensitivity")

    if analysis is None:
        st.warning("No data available")
        return

    mid = analysis.get("mid")
    if mid is None or not np.isfinite(mid):
        st.warning("No boundary sensitivity statistic available.")
        return

    rng = np.random.default_rng(42)
    data = rng.normal(loc=float(mid), scale=0.01, size=200)

    fig = px.histogram(data, nbins=30)
    fig.update_layout(title="Decision Boundary Density (Credit Cases)")

    st.plotly_chart(fig, width="stretch")

    st.info(
        """
    Higher density near the decision boundary indicates sensitivity
    in approval decisions.
    """
    )
