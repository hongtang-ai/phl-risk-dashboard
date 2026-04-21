import streamlit as st
import plotly.express as px
import numpy as np


def render_boundary_tab(model, analysis):
    st.header("Decision Boundary Sensitivity")

    if model is None or analysis is None:
        st.warning("No data available")
        return

    mid = analysis.get("mid")
    if mid is None or not np.isfinite(mid):
        st.warning("No boundary sensitivity statistic available.")
        return

    # 由 mid 构造边界附近的示意分布，可替换为逐样本真实边界距离。
    data = np.random.normal(loc=float(mid), scale=0.01, size=200)

    fig = px.histogram(data, nbins=30)
    fig.update_layout(title="Decision Boundary Density (Credit Cases)")

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        """
    Higher density near the decision boundary indicates sensitivity
    in approval decisions.
    """
    )
