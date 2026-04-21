import streamlit as st

from analyzer import load_demo_case


def render_demo_tab() -> None:
    st.markdown("## 🧪 Demo: Loan Rejection Explanation")

    if st.button("Load German Credit Rejection Demo Case"):
        st.session_state["demo_data"] = load_demo_case()
        st.success("Demo case loaded")

    data = st.session_state.get("demo_data")
    if data is None and st.session_state.get("use_demo") and st.session_state.get("analysis") is not None:
        data = st.session_state["analysis"]

    if data is None:
        st.info("Click the button above to load a demo case.")
        return

    st.markdown("---")

    st.markdown("### ⚠️ Demo Mode: German Credit Rejection Analysis")

    st.markdown("### Case Background")

    q = float(data.get("q", 0.48))
    st.write(
        "Applicant applied for a €5000 used car loan. "
        f"The model produced approval probability q={q:.2f}, "
        "placing the case near the decision boundary. The application was rejected."
    )

    st.markdown("---")

    st.markdown("### Key Risk Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Volatility (σ)", f"{float(data['sigma']):.2f}")
    col2.metric("Mid-density", f"{float(data['mid']):.4f}")
    col3.metric("Effective Rank", f"{float(data['effective_rank']):.2f}")

    col4, col5 = st.columns(2)

    col4.metric("SSI", f"{float(data['ssi']):.2f}")

    risk_level = str(data.get("risk_level", "")).upper()
    risk_color = "orange" if risk_level == "MEDIUM" else "green"
    if risk_level == "HIGH":
        risk_color = "red"
    col5.markdown(
        f"<h3 style='color:{risk_color}'>Risk Score: {float(data['risk_score']):.3f} ({risk_level})</h3>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### Spectrum Analysis")

    spectrum_fig = data.get("spectrum_fig")
    if spectrum_fig is not None:
        st.plotly_chart(spectrum_fig, use_container_width=True)
    else:
        st.info("No spectrum figure in this demo payload.")

    st.caption(
        "Spectrum sharpening indicates internal feature concentration, "
        "which increases decision sensitivity near the approval boundary."
    )

    st.markdown("---")

    st.markdown("### Structural Interpretation")

    st.write(
        "The model shows reduced representational capacity, resulting in high sensitivity near the decision boundary. "
        "Small changes in applicant features may significantly alter approval outcomes, reducing decision consistency."
    )

    st.markdown("---")

    st.markdown("### Regulatory Mapping")

    st.write(
        "This analysis supports Adverse Action Explanation and aligns with SR 11-7 model risk management expectations, "
        "as well as EU AI Act requirements for high-risk credit decision systems."
    )

    st.markdown("---")

    st.markdown("### Recommended Actions")

    st.markdown(
        """
- Trigger secondary human review for borderline applications (q ≈ 0.5)
- Re-assess key applicant attributes (credit history, loan amount, employment stability)
- Avoid fully automated decisions in high-sensitivity regions
- Integrate structural risk metrics into governance workflows
"""
    )
