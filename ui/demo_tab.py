import streamlit as st


def render_demo_tab(model, analysis):
    st.header("Loan Rejection Explanation")

    if analysis is None:
        st.warning("No data available")
        return

    if analysis.get("case_name"):
        st.caption(analysis["case_name"])

    if analysis.get("description"):
        st.subheader("Case Background")
        st.write(analysis["description"])

    sigma = analysis.get("sigma", float("nan"))
    r = analysis.get("effective_rank", float("nan"))
    ssi = analysis.get("ssi", float("nan"))
    mid = analysis.get("mid", float("nan"))
    risk = analysis.get("risk_score", float("nan"))
    risk_level = analysis.get("risk_level")

    st.subheader("Key Risk Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Volatility (sigma)", f"{float(sigma):.2f}")
    col2.metric("Mid-density", f"{float(mid):.4f}")
    col3.metric("Effective Rank", f"{float(r):.2f}")

    col4, col5 = st.columns(2)
    col4.metric("SSI", f"{float(ssi):.3f}")
    risk_label = f"{float(risk):.3f}" + (f" ({risk_level})" if risk_level else "")
    col5.metric("Risk Score", risk_label)

    if analysis.get("interpretation"):
        st.subheader("Structural Interpretation")
        st.write(analysis["interpretation"])

    if analysis.get("regulatory_note"):
        st.subheader("Regulatory Mapping")
        st.write(analysis["regulatory_note"])

    recs = analysis.get("recommendations")
    if isinstance(recs, list) and recs:
        st.subheader("Recommended Actions")
        for rec in recs:
            st.write(f"- {rec}")

    if not (analysis.get("interpretation") or analysis.get("regulatory_note") or recs):
        st.markdown(
            f"""
        ### Explanation Summary

        This loan rejection is associated with structural properties of the model:

        - Logit volatility remains elevated (sigma = {float(sigma):.2f})
        - Effective representation rank reduced to {float(r):.2f}
        - Spectrum concentration increased (SSI = {float(ssi):.3f})
        - Elevated boundary density (mid = {float(mid):.4f})

        ### Interpretation

        The model exhibits a high sensitivity region near the decision boundary,
        likely due to representation collapse in deeper layers.

        ### Recommendation
        Manual review is recommended for:
        - Review credit history
        - Re-evaluate loan amount
        - Account balance
        """
        )
