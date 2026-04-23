import streamlit as st
import plotly.graph_objects as go
import numpy as np


def render_spectrum_tab(analysis: dict | None) -> None:
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

    st.markdown(
        """
<div class="phl-spectrum-panel">
  <div class="phl-spectrum-panel-head">Spectrum Analysis</div>
  <p class="phl-spectrum-panel-desc">
    Eigenvalue decay describes how energy is distributed across latent directions for boundary-adjacent
    rejections. A <strong style="color:#e2e8f0;">sharper, steeper</strong> spectrum often signals
    <strong style="color:#00e5cc;">concentrated representations</strong> and higher sensitivity to small
    perturbations near the decision surface.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=eigvals, mode="lines+markers", name="Eigen Spectrum"))

    fig.update_layout(
        title="Representation Spectrum (Credit Rejection)",
        yaxis_type="log",
        paper_bgcolor="rgba(10,12,18,0.4)",
        plot_bgcolor="rgba(8,10,14,0.5)",
        font=dict(color="#cbd5e1", family="Inter, system-ui, sans-serif"),
        title_font=dict(size=15, color="#f1f5f9"),
    )

    st.markdown('<div class="glass p-6 mb-6">', unsafe_allow_html=True)
    st.plotly_chart(fig, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
<div class="phl-spectrum-foot">
  <p style="margin:0.75rem 0 0;font-size:0.88rem;line-height:1.55;color:#94a3b8 !important;">
    <strong style="color:#a78bfa;">Reading the curve:</strong> flatter early decay can indicate more dispersed
    directions (often more stable under perturbation); a sharp knee followed by a long tail suggests a few
    dominant directions driving the rejection score — a common trigger for secondary review in MRM workflows.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
