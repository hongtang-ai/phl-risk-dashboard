# PHL Risk Diagnostics Dashboard

Structure-aware model risk diagnostics for credit decision systems.

This project implements the Projection Density Law (PHL) framework and provides:

- Interactive Streamlit Dashboard
- Automated PDF Risk Report (MRM-style)
- Structural explanation of model decisions
- Credit risk scenario demo (German Credit)

---

## Demo (Recommended)

Run the dashboard locally:

```bash
streamlit run app.py
```

Then open:

http://localhost:8501

---

## What This Project Does

This tool analyzes neural network decision behavior using:

- Logit scale (sigma)
- Decision boundary density (mid)
- Representation structure (effective rank r)
- Spectrum concentration (SSI)

It helps answer:

Why is a model decision unstable or sensitive?

---

## Use Case: Credit Risk Explanation

In credit approval scenarios:

- Borderline applications (q ~ 0.5)
- Rejected samples
- High-sensitivity decision regions

PHL provides:

- Structural explanation (not just feature attribution)
- Risk diagnostics (PDF report)
- Support for:
  - Adverse Action Explanation
  - EU AI Act high-risk system documentation

---

## PDF Report Output

The system generates a professional report including:

- Executive Summary (Risk Level)
- Key Metrics (sigma, mid, rank, SSI)
- Spectrum Analysis
- Structural Interpretation
- Recommended Actions (MRM-style)

---

## Core Idea (Simplified)

We study the projection:

z = w^T h

and define:

mid = P(|q - 0.5| <= eps)

Empirically:

mid ~ eps / sigma

This links decision uncertainty to logit scale and representation geometry.

---

## Project Structure

phl/
├── app.py                # Streamlit dashboard
├── ui/                   # UI modules
├── analyzer.py           # PHL metrics (sigma / mid / r / SSI helpers)
├── data_loader_credit.py # German Credit loader
├── model.py              # reference MLP definition (optional; uploads may use other checkpoints)

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Main libraries:

- streamlit
- torch
- plotly
- fpdf2
- kaleido

---

## Notes

- This is a research prototype (POC)
- Not intended as a standalone decision system
- Should be used with human oversight

---

## Author

Independent Researcher
Focus: Structure-aware XAI / Model Risk
