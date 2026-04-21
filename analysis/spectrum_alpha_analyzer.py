"""Spectrum + α Analyzer 工具。"""

from __future__ import annotations

import numpy as np


def compute_ssi(eigvals: list[float] | np.ndarray) -> float:
    """
    Spectrum Sharpening Index:
    SSI = sum(lambda_i^2) / (sum(lambda_i)^2 + eps)
    值越大代表谱越尖锐（更容易塌缩）。
    """
    eigvals = np.asarray(eigvals, dtype=np.float64)
    eigvals = eigvals[np.isfinite(eigvals)]
    eigvals = eigvals[eigvals > 0]
    if eigvals.size == 0:
        return float("nan")
    s1 = float(eigvals.sum())
    s2 = float((eigvals**2).sum())
    return s2 / (s1**2 + 1e-8)


def compute_effective_rank_from_eigvals(eigvals: list[float] | np.ndarray) -> float:
    """谱熵定义的有效秩：exp(-sum(p log p))."""
    eigvals = np.asarray(eigvals, dtype=np.float64)
    eigvals = eigvals[np.isfinite(eigvals)]
    eigvals = eigvals[eigvals > 0]
    if eigvals.size == 0:
        return float("nan")
    p = eigvals / (eigvals.sum() + 1e-8)
    entropy = -np.sum(p * np.log(p + 1e-8))
    return float(np.exp(entropy))


def fit_alpha(results: list[dict]) -> float:
    r = np.array([x["r"] for x in results], dtype=np.float64)
    y = np.array([x["mid_sigma"] for x in results], dtype=np.float64)
    m = np.isfinite(r) & np.isfinite(y) & (r > 0) & (y > 0)
    if int(np.sum(m)) < 2:
        return float("nan")
    log_r = np.log(r[m] + 1e-8)
    log_y = np.log(y[m] + 1e-8)
    coef = np.polyfit(log_r, log_y, 1)
    return float(coef[0])


def analyze_model(results: list[dict]) -> dict[str, float]:
    """
    汇总模型的 α、SSI、有效秩与 collapse 风险评分。
    risk = mean(SSI) / (mean(rank) + eps)
    """
    print("\n=== MODEL ANALYSIS ===")

    ssis: list[float] = []
    ranks: list[float] = []
    for item in results:
        eigvals = item.get("eigvals")
        if eigvals is None:
            continue
        ssi = compute_ssi(eigvals)
        rank = compute_effective_rank_from_eigvals(eigvals)
        if np.isfinite(ssi):
            ssis.append(float(ssi))
        if np.isfinite(rank):
            ranks.append(float(rank))

    alpha = fit_alpha(results)
    ssi_mean = float(np.mean(ssis)) if ssis else float("nan")
    rank_mean = float(np.mean(ranks)) if ranks else float("nan")
    risk = ssi_mean / (rank_mean + 1e-8) if np.isfinite(ssi_mean) and np.isfinite(rank_mean) else float("nan")

    print(f"α (scaling exponent): {alpha:.4f}")
    print(f"SSI (mean): {ssi_mean:.4f}")
    print(f"Effective rank (mean): {rank_mean:.2f}")
    print(f"Collapse Risk Score: {risk:.4f}")

    return {
        "alpha": alpha,
        "ssi": ssi_mean,
        "rank": rank_mean,
        "risk": risk,
    }
