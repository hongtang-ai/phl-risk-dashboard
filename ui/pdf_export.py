from fpdf import FPDF
import datetime
import io
import plotly.graph_objects as go


def generate_pdf_report(analysis_results: dict):
    """
    Final PHL Credit Risk Report (MRM / EU AI Act aligned)

    Structure:
    1. Header
    2. Executive Summary (Regulatory aligned)
    3. Key Metrics (with Business Implication)
    4. Spectrum Analysis + Caption
    5. Structural Interpretation
    6. Limitations
    7. Recommended Actions (banking context)
    8. Footer
    """
    # ===== 时间 =====
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M")
    readable_time = now.strftime("%Y-%m-%d %H:%M")
    filename = f"phl_risk_report_{timestamp}.pdf"

    # ===== 数据 =====
    sigma = float(analysis_results.get("sigma", 0) or 0)
    mid = float(analysis_results.get("mid", 0) or 0)
    r = float(analysis_results.get("effective_rank", 0) or 0)
    ssi = float(analysis_results.get("ssi", 0) or 0)
    risk = float(analysis_results.get("risk_score", 0) or 0)
    eigvals = analysis_results.get("eigvals", [])

    # ===== Risk Level =====
    if risk > 0.15:
        risk_level = "HIGH"
        risk_color = (255, 0, 0)
    elif risk > 0.08:
        risk_level = "MEDIUM"
        risk_color = (255, 140, 0)
    else:
        risk_level = "LOW"
        risk_color = (0, 128, 0)

    # ===== 图 =====
    img_bytes = None
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=eigvals, mode="lines+markers"))
        fig.update_layout(title="Covariance Spectrum Sharpening", yaxis_type="log")
        img_bytes = fig.to_image(format="png")
    except Exception:
        img_bytes = None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ===== Header =====
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "PHL Credit Risk Structure Diagnosis Report", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Generated at: {readable_time}", ln=True)
    pdf.cell(0, 6, "PHL Version: v1.0 (POC)", ln=True)
    pdf.ln(6)
    pdf.cell(0, 0, "", ln=True)
    pdf.ln(4)

    # ===== Executive Summary（关键升级）=====
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Executive Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        7,
        "This report supports Adverse Action Explanation and EU AI Act high-risk AI system compliance "
        "technical documentation for credit decision systems.\n\n",
    )

    # Risk Level 高亮块
    pdf.ln(2)
    pdf.set_text_color(*risk_color)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 9, f"[{risk_level} RISK]", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        7,
        "The model shows potential instability in credit decision consistency, "
        "particularly in high-sensitivity zones near the decision boundary, where small changes "
        "in applicant information may lead to inconsistent or unfair outcomes.",
    )
    pdf.ln(3)
    pdf.multi_cell(
        0,
        7,
        "The rejection or risk assessment in this case is primarily driven by structural sensitivity "
        "rather than clear separation in applicant features.",
    )
    pdf.ln(6)
    pdf.cell(0, 0, "", ln=True)
    pdf.ln(4)

    # ===== Key Metrics =====
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Key Metrics", ln=True)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(55, 8, "Metric", 1)
    pdf.cell(35, 8, "Value", 1)
    pdf.cell(90, 8, "Business Implication", 1, ln=True)

    pdf.set_font("Arial", "", 10)
    rows = [
        ("Volatility (sigma)", f"{sigma:.4f}", "Output variability in risk scoring"),
        ("Mid-density", f"{mid:.4f}", "Decision boundary uncertainty density"),
        ("Effective Rank", f"{r:.2f}", "Model representational capacity"),
        ("SSI", f"{ssi:.4f}", "Internal feature concentration level"),
        ("Risk Score", f"{risk:.4f}", "Overall structural instability risk"),
    ]
    for metric, value, desc in rows:
        pdf.cell(55, 8, metric, 1)
        pdf.cell(35, 8, value, 1)
        pdf.cell(100, 8, desc, 1, ln=True)
    pdf.ln(6)
    pdf.cell(0, 0, "", ln=True)
    pdf.ln(4)

    # ===== Spectrum =====
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Covariance Spectrum Analysis", ln=True)

    if img_bytes:
        try:
            pdf.image(io.BytesIO(img_bytes), x=20, w=170)
        except Exception:
            pdf.cell(0, 6, "Spectrum image unavailable", ln=True)
    else:
        pdf.cell(0, 6, "Spectrum image unavailable", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(
        0,
        5,
        "Figure: Spectrum decay reflects internal feature concentration. "
        "Sharper decay indicates increased reliance on a limited set of internal representations, "
        "which may increase decision sensitivity.",
    )
    pdf.ln(6)
    pdf.cell(0, 0, "", ln=True)
    pdf.ln(4)

    # ===== Structural =====
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Structural Interpretation", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        7,
        "The model shows internal feature concentration and reduced representational capacity. "
        "This results in a high-sensitivity zone near the decision boundary, where small changes in "
        "applicant information may significantly alter approval outcomes.",
    )
    pdf.ln(6)
    pdf.cell(0, 0, "", ln=True)
    pdf.ln(4)

    # ===== Limitations =====
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Limitations", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        "This analysis is based on an experimental structural diagnostic framework and "
        "should not be used as the sole basis for automated decision-making. "
        "It must be combined with traditional credit risk models and human review processes.",
    )
    pdf.ln(6)
    pdf.cell(0, 0, "", ln=True)
    pdf.ln(4)

    # ===== Actions =====
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Recommended Actions", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        "- For applications with predicted probability near 0.5, trigger secondary human review process\n"
        "- Avoid fully automated decisions in high-sensitivity regions\n"
        "- Integrate structural risk score into model governance workflow\n"
        "- Implement human oversight for critical decision paths\n"
        "- Monitor model structure post-deployment for drift and instability\n"
        "- For high-risk or borderline cases, decisions should not rely solely on automated model outputs.",
    )
    pdf.ln(5)

    # ===== 页脚 =====
    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(
        0,
        6,
        f"Generated at {readable_time} | PHL v1.0 | Developed by Independent Researcher",
        align="C",
    )

    # ===== 输出 =====
    raw = pdf.output(dest="S")
    if isinstance(raw, str):
        pdf_bytes = raw.encode("latin1")
    else:
        pdf_bytes = bytes(raw)
    return filename, pdf_bytes
