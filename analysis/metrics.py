"""与 mid（投影密度在 0 附近的质量）相关的经验与理论量。"""

from __future__ import annotations

import math

import torch


def compute_mid_from_z(z: torch.Tensor, eps: float = 0.05) -> float:
    """
    从 logit 直接计算 mid：q = sigmoid(z)，统计落在 (0.5−ε, 0.5+ε) 内的比例。
    """
    import torch as _torch

    q = _torch.sigmoid(z.float().flatten())
    lo = 0.5 - eps
    hi = 0.5 + eps
    return float(((q > lo) & (q < hi)).float().mean().item())


def normalize_z(z: torch.Tensor) -> torch.Tensor:
    """去掉整体尺度：z_norm = (z − μ) / (σ + 1e−8)。"""
    z = z.float().flatten()
    std = z.std()
    return (z - z.mean()) / (std + 1e-8)


def compute_mid_fraction(q: torch.Tensor, eps: float = 0.05) -> float:
    """mid = P(|q - 0.5| ≤ eps)，默认 eps=0.05。"""
    q = q.float().flatten()
    mask = (q - 0.5).abs() <= eps
    return float(mask.float().mean().item())


def theoretical_mid(sigma: float, eps: float = 0.05) -> float:
    """mid ≈ ε / σ（小参数近似）。"""
    if sigma <= 0 or not math.isfinite(sigma):
        return float("nan")
    return float(eps / sigma)


def gaussian_mid(sigma: float, eps: float = 0.05) -> float:
    """
    若 z ~ N(0, σ²)，则 P(|z| ≤ ε) = Φ(ε/σ) - Φ(-ε/σ)。
    用于与经验 mid 对照（将 logit 在 0 附近的概率质量与正态近似对比）。
    """
    if sigma <= 0 or not math.isfinite(sigma):
        return float("nan")
    t = eps / sigma
    return float(_phi(t) - _phi(-t))


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
