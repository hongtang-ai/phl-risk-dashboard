import streamlit as st
import plotly.graph_objects as go
import numpy as np


def render_spectrum_tab(analysis: dict | None) -> None:
    st.header("Spectrum Analysis")

    if analysis is None:
        st.warning("No data available")
        return

    eigvals = np.array(analysis.get("eigvals", []), dtype=float)
    eigvals = eigvals[np.isfinite(eigvals)]
    eigvals = eigvals[eigvals > 0]
    eigvals = np.sort(eigvals)[::-1]
    if eigvals.size == 0:
        st.warning("No eigen spectrum available from analysis.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=eigvals, mode="lines+markers", name="Eigen Spectrum"))

    fig.update_layout(
        title="Representation Spectrum (Credit Rejection)",
        yaxis_type="log",
    )

    st.plotly_chart(fig, width="stretch")

    st.info(
        """
    A sharper spectrum indicates concentration of representation,
    which may lead to unstable credit decisions.
    """
    )
