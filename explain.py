"""Lightweight explainability helpers."""

from __future__ import annotations


def compute_feature_impact(age, credit_score, loan_amount, **kwargs):
    # Lightweight heuristic contribution; can be replaced by model-attribution later.
    weighted_age = float(age) * 0.3
    weighted_credit = float(credit_score) * 0.5
    weighted_loan = float(loan_amount) * 0.2
    total = weighted_age + weighted_credit + weighted_loan
    if abs(total) < 1e-8:
        return {"Age": 0.0, "Credit Score": 0.0, "Loan Amount": 0.0}
    return {
        "Age": round(weighted_age / total * 100, 1),
        "Credit Score": round(weighted_credit / total * 100, 1),
        "Loan Amount": round(weighted_loan / total * 100, 1),
    }

