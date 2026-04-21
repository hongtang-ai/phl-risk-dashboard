# PHL Risk Diagnostics Dashboard

Structure-aware model risk diagnostics for credit decision systems.

This project implements the Projection Density Law (PHL) framework and provides a practical tool for analyzing decision boundary sensitivity and structural instability in neural network models.

---

## Live Demo

Open the deployed dashboard:

https://phl-risk-dashboard-rngrymxad3purafnszxkax.streamlit.app/

---

## Run Locally

```bash
streamlit run app.py
```

Then open:

http://localhost:8501

---

## What This Project Does

This dashboard analyzes model behavior beyond traditional feature importance by focusing on decision structure:

- Logit scale (sigma) → output volatility
- Mid-density (mid) → decision boundary uncertainty
- Effective rank (r) → representation capacity
- Spectrum Sharpening Index (SSI) → feature concentration risk

It helps answer:

Why is a model decision unstable or sensitive near approval thresholds?

---

## Use Case: Credit Risk Explanation

Designed for bank Model Risk Management (MRM) and compliance teams.

Typical scenarios:

- Borderline applications (q ~ 0.5)
- Loan rejections requiring explanation
- High-sensitivity decision regions

PHL provides:

- Structural explanation (beyond feature attribution)
- Model risk diagnostics
- Automated PDF reporting

Supports:

- Adverse Action Explanation
- EU AI Act (high-risk AI system documentation)

---

## Demo Scenario (German Credit)

Includes a built-in interactive demo (no model training required):

German Credit – Rejection Analysis

- Applicant requests €5000 loan
- Model output: q = 0.48 (near decision boundary)
- Decision: Rejected

PHL reveals:

- Reduced effective rank → limited representation capacity
- Spectrum sharpening → feature concentration
- High-sensitivity zone near decision boundary

Small changes in applicant features may significantly affect outcomes.

---

## PDF Report Output

Generates a professional MRM-style risk report including:

- Executive Summary (Risk Level)
- Key Metrics (sigma, mid, rank, SSI)
- Spectrum Analysis
- Structural Interpretation
- Recommended Actions
- Compliance-oriented explanation

---

## PHL PDF Risk Report – Final Enhancement (MRM-ready POC)

This update upgrades the PHL PDF report to a professional, compliance-aligned format suitable for bank Model Risk Management (MRM) teams and regulatory audits.

### Key Improvements

1. Executive Summary (Business + Regulatory Focus)

- Added a strong regulatory-aligned opening referencing Adverse Action Explanation and EU AI Act high-risk AI systems.
- Explicitly interprets MEDIUM RISK in business terms: potential inconsistency in credit decisions and increased risk of appeals/regulatory scrutiny.

2. Financial Language Standardization

Translated technical terms into clear, business-oriented language:

- “Reduced model representational capacity, leading to higher sensitivity at decision boundary”
- “High-sensitivity zone near the decision boundary, where small changes in applicant features may lead to inconsistent approval outcomes”
- Recommendations rewritten as actionable banking procedures.

3. Visual and Layout Improvements

- Increased spacing and margins for better readability.
- Risk Level (MEDIUM) visually emphasized using professional color palettes.
- Key Metrics table redesigned with structured borders and audit-style alignment.
- Spectrum chart enlarged, centered, and given a clear business-oriented caption explaining spectrum sharpening.

4. Regulatory Alignment Section (New)

- Added dedicated section: “Alignment with Regulatory Requirements”
- Covers SR 11-7 Model Risk Management expectations, Adverse Action Explanation requirements, and EU AI Act technical documentation standards.

5. Compliance-safe Design

- No changes to core PHL metrics or computation logic.
- Maintains the fpdf2 + kaleido pipeline for high-quality PDF generation.
- Output remains fully compatible with Streamlit `download_button` (returns bytes).

### Result

The PHL PDF Risk Report is now positioned as:

A decision stability and structural risk explanation document for credit model governance.

Suitable for:

- Model validation and independent challenge
- Internal audit discussions
- Regulatory technical documentation support
- Loan rejection appeal explanations

This version makes the report MRM-ready — professional enough for bank risk and compliance teams while clearly highlighting the unique value of PHL’s spectrum-based structural diagnosis.

---

## Core Idea (Simplified)

We study the projection:

z = w^T h

Define:

mid = P(|q - 0.5| <= eps)

Empirically:

mid ~ eps / sigma

This links decision uncertainty to logit scale and representation geometry.

---

## Project Structure

phl-risk-dashboard/

- `app.py` — Streamlit entry point
- `ui/` — Dashboard UI modules
- `analyzer.py` — Core PHL metrics
- `data_loader_credit.py` — German Credit dataset loader
- `model.py` — Reference MLP (optional)

---

## Installation

```bash
pip install -r requirements.txt
```

Main dependencies:

- streamlit
- torch
- plotly
- fpdf2
- kaleido
- scikit-learn
- pandas

---

## Important Notes

- This is a research prototype (POC)
- Not intended as a standalone decision system
- Should be used with human oversight and existing governance frameworks

---

## Positioning

This is not a feature importance tool.

It introduces **structure-aware model risk diagnostics**, focusing on:

- Decision boundary behavior
- Representation collapse
- Structural instability

---

## Author

Independent Researcher  
Focus: Structure-aware XAI / Model Risk / AI Governance
