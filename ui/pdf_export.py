from fpdf import FPDF
import datetime
import io
import plotly.graph_objects as go


def generate_pdf_report(analysis_results: dict):
    """Generate a finance-ready compliance-oriented PHL report."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M")
    readable_time = now.strftime("%Y-%m-%d %H:%M")
    filename = f"phl_risk_report_{timestamp}.pdf"

    sigma = float(analysis_results.get("sigma", 0) or 0)
    mid = float(analysis_results.get("mid", 0) or 0)
    r = float(analysis_results.get("effective_rank", 0) or 0)
    ssi = float(analysis_results.get("ssi", 0) or 0)
    risk = float(analysis_results.get("risk_score", 0) or 0)
    eigvals = analysis_results.get("eigvals", [])

    if risk > 0.15:
        risk_level = "HIGH"
    elif risk > 0.08:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    img_bytes = None
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=eigvals, mode="lines+markers"))
        fig.update_layout(title="Covariance Spectrum Sharpening", yaxis_type="log")
        img_bytes = fig.to_image(format="png")
    except Exception:
        img_bytes = None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(left=18, top=18, right=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "PHL Credit Risk Structure Diagnosis Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated at: {readable_time}", ln=True)
    pdf.cell(0, 6, "PHL Version: v1.0 (POC)", ln=True)
    pdf.ln(3)

    if analysis_results.get("case_name"):
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(
            0,
            8,
            "Demo Case: Pre-configured analysis (not real-time model output)",
            ln=True,
        )
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Executive Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "This report provides a structural diagnosis to support Adverse Action Explanation and "
        "EU AI Act high-risk AI system compliance for credit decisions.",
    )
    pdf.ln(2)
    if risk_level == "MEDIUM":
        pdf.multi_cell(
            0,
            6,
            "A MEDIUM risk level indicates potential inconsistency in credit decisions, "
            "particularly for borderline applications, which may increase appeal risk and regulatory scrutiny.",
        )
    else:
        pdf.multi_cell(
            0,
            6,
            f"A {risk_level} risk level indicates potential inconsistency in credit decisions, "
            "particularly for borderline applications, which may increase appeal risk and regulatory scrutiny.",
        )

    pdf.ln(2)
    if risk_level == "MEDIUM":
        pdf.set_text_color(255, 140, 0)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "[MEDIUM RISK]", ln=True)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, f"[{risk_level} RISK]", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Key Metrics", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 8, "Metric", border=1)
    pdf.cell(40, 8, "Value", border=1)
    pdf.cell(90, 8, "Business Implication", border=1, ln=True)

    pdf.set_font("Helvetica", "", 10)
    rows = [
        ("Volatility (sigma)", f"{sigma:.4f}", "Output variability in risk scoring"),
        ("Mid-density", f"{mid:.4f}", "Decision boundary uncertainty density"),
        (
            "Effective Rank",
            f"{r:.2f}",
            "Reduced model representational capacity, leading to higher sensitivity at decision boundary",
        ),
        ("SSI", f"{ssi:.4f}", "Internal feature concentration level"),
        ("Risk Score", f"{risk:.4f}", "Overall structural instability risk"),
    ]
    for metric, value, implication in rows:
        pdf.cell(60, 8, metric, border=1, align="L")
        pdf.cell(40, 8, value, border=1, align="C")
        pdf.cell(90, 8, implication, border=1, ln=True, align="L")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Covariance Spectrum Sharpening", ln=True)
    if img_bytes:
        try:
            pdf.image(io.BytesIO(img_bytes), w=175)
        except Exception:
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, "Spectrum image unavailable", ln=True)
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Spectrum image unavailable", ln=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Spectrum sharpening indicates internal feature concentration, increasing sensitivity near the decision boundary.",
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Structural Interpretation", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "The model exhibits reduced model representational capacity, leading to higher sensitivity at decision boundary. "
        "This forms a high-sensitivity zone near the decision boundary, where small changes in applicant features may lead "
        "to inconsistent approval outcomes.",
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Limitations", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "This analysis is based on an experimental structural diagnostic framework and should not be used as the sole "
        "basis for automated decision-making. It must be combined with traditional credit risk models and human review processes.",
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Recommended Actions", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "- For applications with probability near 0.5, trigger secondary human review process\n"
        "- Re-evaluate key input factors (credit history, loan amount, employment stability)\n"
        "- Avoid fully automated decisions in high-sensitivity regions\n"
        "- Integrate structural risk score into model governance workflow\n"
        "- Implement human oversight for critical decision paths\n"
        "- Monitor model structure post-deployment for drift and instability",
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Alignment with Regulatory Requirements", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "This report supports model risk management expectations under SR 11-7, "
        "Adverse Action Explanation requirements, and EU AI Act technical documentation for high-risk AI systems.",
    )

    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(
        0,
        6,
        f"Generated at {readable_time} | PHL v1.0 | Developed by Independent Researcher",
        align="C",
    )

    raw = pdf.output(dest="S")
    pdf_bytes = raw.encode("latin1") if isinstance(raw, str) else bytes(raw)
    return filename, pdf_bytes
