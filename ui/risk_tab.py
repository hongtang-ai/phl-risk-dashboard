import streamlit as st

from ui.pdf_export import generate_pdf_report


def render_risk_tab(model, analysis):
    st.header("Risk Report")

    if model is None or analysis is None:
        st.warning("No data available")
        return

    sigma = analysis.get("sigma")
    r = analysis.get("effective_rank")
    ssi = analysis.get("ssi")
    risk = analysis.get("risk_score")

    if any(v is None for v in (sigma, r, ssi, risk)):
        st.warning("Incomplete risk metrics in analysis output.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Volatility (σ)", f"{float(sigma):.2f}")
    col2.metric("Effective Rank", f"{float(r):.2f}")
    col3.metric("Concentration (SSI)", f"{float(ssi):.3f}")
    col4.metric("Risk Score", f"{float(risk):.3f}")

    if float(risk) > 0.15:
        st.warning("High structural risk detected")
    else:
        st.success("Risk level acceptable")

    try:
        filename, pdf_bytes = generate_pdf_report(analysis)
        st.caption(f"本次导出文件：`{filename}`")
        st.download_button(
            label="📄 生成并下载 PDF 报告",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
        )
    except Exception as exc:
        st.info(f"PDF export unavailable: {exc}")
