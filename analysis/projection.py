"""投影方向上的方差与 z 的尺度估计。"""

from __future__ import annotations

import torch


def compute_projection_variance(h: torch.Tensor, w: torch.Tensor) -> float:
    """
    Var(z) = Var(w^T h)，w 与 h 最后一维对齐；w 可为 (d,) 或 (1, d)。
    """
    if h.dim() != 2:
        raise ValueError("h 形状应为 (N, d)")
    w = w.view(-1)
    if w.numel() != h.size(1):
        raise ValueError("w 长度必须与 h 的特征维一致")
    proj = h.float() @ w.float()
    if proj.numel() < 2:
        return float("nan")
    proj = proj - proj.mean()
    var = (proj**2).sum() / max(proj.numel() - 1, 1)
    return float(var.item())


def estimate_sigma(z: torch.Tensor) -> float:
    """σ = std(z)（无偏样本标准差）。"""
    if z.numel() < 2:
        return float("nan")
    return float(z.float().std(unbiased=True).item())
