from __future__ import annotations

import numpy as np

from analyzer import compute_ssi


def compute_financial_metrics(result_row: dict) -> dict[str, float]:
    """金融语义映射层：不改数学，仅重命名解释。"""
    sigma = float(result_row["sigma"])
    mid = float(result_row["mid_raw"])
    r = float(result_row["r"])
    eigvals = np.array(result_row["eigvals"], dtype=np.float64)

    ssi = float(compute_ssi(eigvals))
    volatility = sigma
    uncertainty_density = mid
    diversification = r
    concentration = ssi
    risk_score = concentration / (diversification + 1e-8)

    return {
        "volatility": float(volatility),
        "uncertainty_density": float(uncertainty_density),
        "diversification": float(diversification),
        "concentration": float(concentration),
        "risk_score": float(risk_score),
    }


def generate_risk_report(results: list[dict]) -> dict[str, float]:
    metrics = [compute_financial_metrics(r) for r in results]
    avg_risk = float(np.mean([m["risk_score"] for m in metrics]))
    avg_vol = float(np.mean([m["volatility"] for m in metrics]))

    print("\n===== FINANCIAL RISK REPORT =====")
    print(f"Avg Volatility: {avg_vol:.4f}")
    print(f"Avg Risk Score: {avg_risk:.4f}")

    return {"avg_volatility": avg_vol, "avg_risk_score": avg_risk}
