"""基于隐层表示的谱量：有效秩与 PCA。"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch


def compute_effective_rank(h: torch.Tensor) -> float:
    """
    输入: h (N, d)
    输出: r = (Σλ)^2 / Σλ²，λ 为协方差阵特征值（仅非负部分）。
    """
    if h.dim() != 2:
        raise ValueError("h 形状应为 (N, d)")
    n = h.size(0)
    if n < 2:
        return float("nan")
    h = h.float()
    h = h - h.mean(dim=0, keepdim=True)
    cov = (h.T @ h) / max(n - 1, 1)
    eigvals = torch.linalg.eigvalsh(cov)
    eigvals = torch.clamp(eigvals, min=0.0)
    s = eigvals.sum()
    if s <= 0:
        return 0.0
    denom = (eigvals**2).sum()
    if denom <= 0:
        return 0.0
    r = (s * s) / denom
    return float(r.item())


def compute_pca(h: torch.Tensor, k: int = 10) -> tuple[torch.Tensor, torch.Tensor]:
    """
    返回前 k 个特征值（降序）与对应特征向量（列向量为特征向量）。
    """
    if h.dim() != 2:
        raise ValueError("h 形状应为 (N, d)")
    h = h.float()
    h = h - h.mean(dim=0, keepdim=True)
    n = h.size(0)
    cov = (h.T @ h) / max(n - 1, 1)
    eigvals, eigvecs = torch.linalg.eigh(cov)
    eigvals, eigvecs = eigvals.flip(0), eigvecs.flip(1)
    k = min(k, eigvals.numel())
    return eigvals[:k], eigvecs[:, :k]


def plot_spectrum(cov: np.ndarray, name: str) -> None:
    """绘制并保存协方差谱衰减图。"""
    plots_dir = Path(__file__).resolve().parents[1] / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    eigvals = np.linalg.eigvalsh(cov)
    eigvals = np.sort(eigvals)[::-1]
    eigvals = np.clip(eigvals, 1e-12, None)

    plt.figure(figsize=(6, 4))
    plt.plot(eigvals)
    plt.yscale("log")
    plt.title(f"Spectrum: {name}")
    plt.xlabel("index")
    plt.ylabel("eigenvalue (log)")
    plt.tight_layout()
    plt.savefig(plots_dir / f"spectrum_{name}.png", dpi=160)
    plt.close()
