from __future__ import annotations

import datetime
import os
import tempfile

import plotly.graph_objects as go
from fpdf import FPDF


def _save_plotly_figure(fig: go.Figure) -> str | None:
    """
    Export Plotly figure to PNG via kaleido; write to a temp file for fpdf2 image().
    Returns path on success, None on failure.
    """
    try:
        img_bytes = fig.to_image(format="png", width=900, height=600, scale=2)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(img_bytes)
        tmp.close()
        return tmp.name
    except Exception as e:
        print("Plotly export failed:", e)
        return None


def _split_lines_to_width(pdf: FPDF, text: str, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    cur: list[str] = []
    for word in words:
        trial = " ".join(cur + [word])
        if pdf.get_string_width(trial) <= max_width:
            cur.append(word)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [word]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _metrics_table_row(pdf: FPDF, name: str, value_str: str, desc: str) -> None:
    """Three-column bordered row; last column wraps within fixed width."""
    w1, w2, w3 = 60, 40, 90
    lh = 8
    x0 = pdf.get_x()
    y0 = pdf.get_y()
    lines = _split_lines_to_width(pdf, desc, w3 - 2)
    row_h = max(lh, lh * len(lines))

    pdf.rect(x0, y0, w1, row_h)
    pdf.rect(x0 + w1, y0, w2, row_h)
    pdf.rect(x0 + w1 + w2, y0, w3, row_h)

    yn = y0 + (row_h - lh) / 2
    pdf.set_xy(x0 + 1, yn)
    pdf.cell(w1 - 2, lh, name, border=0, align="L")
    pdf.set_xy(x0 + w1 + 1, yn)
    pdf.cell(w2 - 2, lh, value_str, border=0, align="C")

    yd = y0 + (row_h - lh * len(lines)) / 2
    for i, line in enumerate(lines):
        pdf.set_xy(x0 + w1 + w2 + 1, yd + i * lh)
        pdf.cell(w3 - 2, lh, line, border=0, align="L")

    pdf.set_xy(x0, y0 + row_h)


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
        risk_tier = "HIGH"
    elif risk > 0.08:
        risk_tier = "MEDIUM"
    else:
        risk_tier = "LOW"

    display_risk = analysis_results.get("risk_level", risk_tier)

    fig_for_spectrum = analysis_results.get("spectrum_fig")
    if fig_for_spectrum is None and eigvals:
        try:
            fig_for_spectrum = go.Figure()
            fig_for_spectrum.add_trace(go.Scatter(y=eigvals, mode="lines+markers"))
            fig_for_spectrum.update_layout(
                title="Covariance Spectrum Sharpening",
                yaxis_type="log",
            )
        except Exception:
            fig_for_spectrum = None

    img_path: str | None = None
    if fig_for_spectrum is not None:
        img_path = _save_plotly_figure(fig_for_spectrum)

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

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Executive Summary", ln=True)

    pdf.set_font("Helvetica", "", 11)
    if display_risk == "MEDIUM":
        para2 = (
            "The identified MEDIUM risk level indicates that credit decisions in this region may be unstable, "
            "particularly for borderline applications, increasing the likelihood of appeal and inconsistent approval outcomes."
        )
    elif display_risk == "HIGH":
        para2 = (
            "The identified HIGH risk level indicates that structural instability is elevated; credit outcomes near "
            "the boundary may be highly sensitive, increasing inconsistency, appeal exposure, and supervisory interest."
        )
    else:
        para2 = (
            "The identified LOW risk level suggests comparatively stronger decision stability in structural terms; "
            "human review and monitoring should still apply for borderline cases."
        )

    pdf.multi_cell(
        0,
        7,
        "This report provides a structural diagnosis to support Adverse Action Explanation and EU AI Act high-risk AI system compliance, "
        "helping banks reduce decision inconsistency and regulatory scrutiny risk. "
        + para2,
    )
    pdf.ln(2)

    if display_risk == "MEDIUM":
        pdf.set_text_color(255, 140, 0)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(
            0,
            8,
            "[MEDIUM RISK] - Decision stability is moderately compromised",
            ln=True,
        )
        pdf.set_text_color(0, 0, 0)
    elif display_risk == "HIGH":
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(
            0,
            8,
            "[HIGH RISK] - Decision stability is materially compromised; strengthen controls and review",
            ln=True,
        )
    else:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(
            0,
            8,
            "[LOW RISK] - Structural indicators suggest comparatively stable scoring behavior",
            ln=True,
        )

    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Key Metrics", ln=True)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(60, 8, "Metric", border=1)
    pdf.cell(40, 8, "Value", border=1, align="C")
    pdf.cell(90, 8, "Business Implication", border=1, ln=True)

    pdf.set_font("Helvetica", "", 10)
    rows = [
        ("Volatility (sigma)", f"{sigma:.4f}", "Variability in credit scoring output"),
        ("Mid-density", f"{mid:.4f}", "Uncertainty concentration near decision boundary"),
        (
            "Effective Rank",
            f"{r:.4f}",
            "Reduced model capacity, increasing boundary sensitivity",
        ),
        ("SSI", f"{ssi:.4f}", "Internal feature concentration level"),
        ("Risk Score", f"{risk:.4f}", "Overall structural instability indicator"),
    ]
    for name, value, desc in rows:
        _metrics_table_row(pdf, name, value, desc)

    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Covariance Spectrum Sharpening", ln=True)
    pdf.ln(2)

    if img_path and os.path.exists(img_path):
        try:
            pdf.image(img_path, w=175)
        finally:
            try:
                os.remove(img_path)
            except OSError:
                pass
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "Spectrum visualization unavailable (fallback triggered)", ln=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Spectrum sharpening indicates internal feature concentration, which increases decision sensitivity near the approval boundary.",
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Structural Interpretation", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "The model demonstrates reduced representational capacity, resulting in elevated sensitivity near the decision boundary. "
        "In this region, small variations in applicant features may lead to materially different approval outcomes, reducing decision consistency.",
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
    actions = [
        "Trigger secondary human review for borderline applications (q ~ 0.5).",
        "Re-assess key applicant attributes (credit history, loan amount, employment stability).",
        "Avoid fully automated decisions in high-sensitivity regions.",
        "Integrate structural risk metrics into model governance workflows.",
        "Monitor model structure post-deployment for drift and instability.",
    ]
    text_w = pdf.w - pdf.l_margin - pdf.r_margin
    for act in actions:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(text_w, 6, f"- {act}", ln=1)

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
