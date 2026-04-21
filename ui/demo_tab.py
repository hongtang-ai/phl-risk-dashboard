import numpy as np
import plotly.graph_objects as go
import streamlit as st


def render_demo_tab(model, analysis):
    st.markdown("## Demo: How PHL Explains a Loan Rejection Appeal")
    st.divider()

    if analysis is None:
        st.warning("No data available")
        return

    st.subheader("Case Background")
    st.write(analysis.get("description", "No case description available."))
    st.divider()

    st.subheader("Key Risk Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Volatility (sigma)", f"{float(analysis.get('sigma', float('nan'))):.2f}")
    col2.metric("Mid-density", f"{float(analysis.get('mid', float('nan'))):.4f}")
    col3.metric("Effective Rank", f"{float(analysis.get('effective_rank', float('nan'))):.2f}")

    col4, col5 = st.columns(2)
    col4.metric("SSI", f"{float(analysis.get('ssi', float('nan'))):.3f}")
    risk_level = str(analysis.get("risk_level", "")).upper()
    risk_score = float(analysis.get("risk_score", float("nan")))
    risk_color = (
        "red" if risk_level == "HIGH" else "orange" if risk_level == "MEDIUM" else "green"
    )
    col5.markdown(
        f"Risk Score: <span style='color:{risk_color};font-weight:bold'>{risk_score:.3f} ({risk_level or 'N/A'})</span>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Mid-density reflects decision boundary uncertainty. Effective Rank measures representation capacity. "
        "Higher SSI indicates feature concentration risk."
    )
    st.divider()

    st.subheader("Spectrum Analysis")
    eigvals = np.asarray(analysis.get("eigvals", []), dtype=float)
    eigvals = eigvals[np.isfinite(eigvals)]
    eigvals = eigvals[eigvals > 0]
    if eigvals.size > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=np.log(eigvals), mode="lines+markers"))
        fig.update_layout(
            title="Covariance Spectrum (Sharpening Effect)",
            xaxis_title="Component Index",
            yaxis_title="Log Eigenvalue",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No spectrum data available.")
    st.caption(
        "Spectrum sharpening indicates internal feature concentration, increasing sensitivity near the decision boundary."
    )
    st.divider()

    st.subheader("Structural Interpretation")
    st.write(analysis.get("interpretation", "No interpretation available."))
    st.divider()

    st.subheader("Regulatory Mapping")
    st.write(analysis.get("regulatory_note", "No regulatory mapping available."))
    st.divider()

    st.subheader("Recommended Actions")
    recommendations = analysis.get("recommendations", [])
    if isinstance(recommendations, list) and recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.markdown("- Manual review is recommended for this case.")
