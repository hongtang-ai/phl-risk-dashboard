import streamlit as st


def render_demo_tab(model, analysis):
    st.header("Loan Rejection Explanation")

    if model is None or analysis is None:
        st.warning("No data available")
        return

    sigma = analysis.get("sigma", float("nan"))
    r = analysis.get("effective_rank", float("nan"))
    ssi = analysis.get("ssi", float("nan"))
    mid = analysis.get("mid", float("nan"))

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
