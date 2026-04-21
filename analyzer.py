from __future__ import annotations

import math
from typing import Any

import numpy as np
import torch


# =========================
# 核心计算（公式见 PHL_完整公式推导与结果汇总.md）
# =========================

def compute_mid_fraction(q: torch.Tensor, eps: float = 0.05) -> float:
    """P(|q-0.5|<=eps)。"""
    q = q.float().flatten()
    return float(((q - 0.5).abs() <= eps).float().mean().item())


def compute_mid_from_z(z: torch.Tensor, eps: float = 0.05) -> float:
    """通过 q=sigmoid(z) 计算 mid。"""
    q = torch.sigmoid(z.float().flatten())
    return float(((q > (0.5 - eps)) & (q < (0.5 + eps))).float().mean().item())


def normalize_z(z: torch.Tensor) -> torch.Tensor:
    """z_norm=(z-mean)/std。"""
    z = z.float().flatten()
    return (z - z.mean()) / (z.std() + 1e-8)


def estimate_sigma(z: torch.Tensor) -> float:
    return float(z.float().std().item())


def compute_projection_variance(h: torch.Tensor, w: torch.Tensor) -> float:
    proj = h.float() @ w.float().view(-1)
    return float(proj.var(unbiased=True).item())


def compute_effective_rank(eigvals: np.ndarray | list[float]) -> float:
    """(sum lambda)^2 / sum(lambda^2)。"""
    ev = np.asarray(eigvals, dtype=np.float64)
    ev = ev[np.isfinite(ev)]
    ev = ev[ev >= 0]
    if ev.size == 0:
        return float("nan")
    s1 = float(ev.sum())
    s2 = float((ev**2).sum())
    if s2 <= 0:
        return 0.0
    return (s1 * s1) / s2


def compute_effective_rank_from_h(h: torch.Tensor) -> float:
    eigvals = compute_cov_eigvals(h)
    return compute_effective_rank(eigvals)


def compute_ssi(eigvals: np.ndarray | list[float]) -> float:
    """SSI = sum(lambda^2) / (sum lambda)^2。"""
    ev = np.asarray(eigvals, dtype=np.float64)
    ev = ev[np.isfinite(ev)]
    ev = ev[ev > 0]
    if ev.size == 0:
        return float("nan")
    return float((ev**2).sum() / ((ev.sum() ** 2) + 1e-8))


def estimate_spectrum_slope(eigvals: np.ndarray | list[float]) -> float:
    """拟合 log(lambda_i)=a*log(i)+b 的 slope a。"""
    ev = np.asarray(eigvals, dtype=np.float64)
    ev = ev[ev > 1e-8]
    if ev.size < 2:
        return float("nan")
    idx = np.arange(1, ev.size + 1, dtype=np.float64)
    a, _ = np.polyfit(np.log(idx), np.log(ev), 1)
    return float(a)


def compute_cov_eigvals(h: torch.Tensor, sample_size: int | None = None) -> np.ndarray:
    """计算 Cov(h) 特征值；大规模时可随机采样样本数。"""
    h_np = h.detach().cpu().numpy().astype(np.float64)
    n = h_np.shape[0]
    if sample_size is not None and n > sample_size:
        idx = np.random.choice(n, size=sample_size, replace=False)
        h_np = h_np[idx]
    cov = np.cov(h_np.T)
    eigvals = np.linalg.eigvalsh(cov)
    eigvals = np.sort(eigvals)[::-1]
    return eigvals


def theoretical_mid(sigma: float, eps: float = 0.05) -> float:
    """mid ≈ eps / sigma。"""
    if sigma <= 0 or not math.isfinite(sigma):
        return float("nan")
    return float(eps / sigma)


def gaussian_mid(sigma: float, eps: float = 0.05) -> float:
    if sigma <= 0 or not math.isfinite(sigma):
        return float("nan")
    t = eps / sigma
    return float(_phi(t) - _phi(-t))


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def spectrum_alpha_analyzer(results: list[dict[str, Any]]) -> dict[str, float]:
    """拟合 log(mid*sigma) vs log(r)，返回 alpha 与 R^2。"""
    r = np.array([row["r"] for row in results], dtype=np.float64)
    y = np.array([row["mid_sigma"] for row in results], dtype=np.float64)
    m = np.isfinite(r) & np.isfinite(y) & (r > 0) & (y > 0)
    if int(np.sum(m)) < 2:
        return {"alpha": float("nan"), "r2": float("nan")}
    x = np.log(r[m] + 1e-8)
    z = np.log(y[m] + 1e-8)
    a, b = np.polyfit(x, z, 1)
    zhat = a * x + b
    ss_tot = float(((z - z.mean()) ** 2).sum())
    r2 = float("nan") if ss_tot <= 0 else float(1.0 - ((z - zhat) ** 2).sum() / ss_tot)
    return {"alpha": float(a), "r2": r2}


def load_demo_case() -> dict[str, Any]:
    """Returns a fixed demo analysis result for German Credit rejection case."""
    eigvals = np.array([12.5, 4.2, 1.8, 0.9, 0.5, 0.3, 0.2, 0.1], dtype=float)

    return {
        "case_name": "German Credit – Rejection Analysis",
        "description": (
            "Applicant requested a €5000 used car loan. "
            "The model produced a probability of q = 0.48, placing the case near the decision boundary. "
            "The application was subsequently rejected."
        ),
        "sigma": 6.23,
        "mid": 0.0075,
        "effective_rank": 3.12,
        "ssi": 0.42,
        "risk_score": 0.135,
        "risk_level": "MEDIUM",
        "eigvals": eigvals.tolist(),
        "interpretation": (
            "The model exhibits reduced representational capacity, with feature importance highly concentrated "
            "in a few dominant directions. This creates a high-sensitivity zone near the decision boundary, "
            "where small variations in applicant attributes may lead to inconsistent credit decisions."
        ),
        "regulatory_note": (
            "This analysis supports Adverse Action Explanation requirements and aligns with EU AI Act "
            "expectations for high-risk credit scoring systems."
        ),
        "recommendations": [
            "Trigger secondary human review for borderline applications (q ≈ 0.5).",
            "Re-evaluate key features such as credit history, loan amount, and employment stability.",
            "Avoid fully automated decisions in high-sensitivity regions.",
            "Continuously monitor structural indicators (effective rank and SSI) for model drift.",
        ],
    }
