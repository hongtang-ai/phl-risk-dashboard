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
