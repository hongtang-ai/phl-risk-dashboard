"""Lightweight explainability helpers."""

from __future__ import annotations


def compute_feature_impact(age, credit_score, loan_amount, **kwargs):
    # === UPDATED ===
    # Lightweight heuristic contribution with nonlinear credit term
    # to mimic threshold-like effects in underwriting.
    weighted_age = float(age) * 0.25
    weighted_credit = float(credit_score) * 0.35 + (float(credit_score) ** 2) * 0.005
    weighted_loan = float(loan_amount) * 0.15
    total = weighted_age + weighted_credit + weighted_loan
    if abs(total) < 1e-8:
        return {
            "impact_pct": {"Age": 0.0, "Credit Score": 0.0, "Loan Amount": 0.0},
            "description": "No dominant factor detected for near-zero combined impact.",
        }

    impacts = {
        "Age": round(weighted_age / total * 100, 1),
        "Credit Score": round(weighted_credit / total * 100, 1),
        "Loan Amount": round(weighted_loan / total * 100, 1),
    }
    dominant_feature = max(impacts, key=impacts.get)
    description = f"{dominant_feature} is the dominant factor in the current decision."

    return {
        "impact_pct": impacts,
        "description": description,
    }

