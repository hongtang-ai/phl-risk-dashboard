"""FINAL α ANALYSIS: FIG7 / FIG8 / FIG9."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PLOTS_DIR = Path(__file__).resolve().parents[1] / "plots"


def safe_log(x: np.ndarray) -> np.ndarray:
    return np.log(np.maximum(x, 1e-8))


def compute_r2(y: np.ndarray, y_pred: np.ndarray) -> float:
    ss_tot = float(((y - y.mean()) ** 2).sum())
    if ss_tot <= 0:
        return float("nan")
    return float(1.0 - (((y - y_pred) ** 2).sum() / ss_tot))


def plot_fig7(results: list[dict]) -> float:
    """Figure 7: log(mid·σ) vs log(r)，拟合全局 α。"""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    r = np.array([x["r"] for x in results], dtype=np.float64)
    y = np.array([x["mid_sigma"] for x in results], dtype=np.float64)
    m = np.isfinite(r) & np.isfinite(y) & (r > 0) & (y > 0)
    log_r = safe_log(r[m])
    log_y = safe_log(y[m])

    coef = np.polyfit(log_r, log_y, 1)
    alpha = float(coef[0])
    y_pred = coef[0] * log_r + coef[1]
    r2 = compute_r2(log_y, y_pred)

    plt.figure(figsize=(6, 5))
    plt.scatter(log_r, log_y, alpha=0.7, edgecolors="none")
    xs = np.linspace(float(log_r.min()), float(log_r.max()), 100)
    plt.plot(xs, coef[0] * xs + coef[1], label=f"α={alpha:.3f}, R²={r2:.3f}")
    plt.xlabel("log(r)")
    plt.ylabel("log(mid·σ)")
    plt.title("Figure 7: Scaling Law")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "fig7_log_mid_sigma_vs_r.png", dpi=160)
    plt.close()

    print("\n=== FIGURE 7 ===")
    print(f"Global α = {alpha:.4f}, R² = {r2:.4f}")
    return alpha


def plot_fig8(results: list[dict]) -> None:
    """Figure 8: α vs depth。"""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    grouped: dict[int, list[dict]] = defaultdict(list)
    for item in results:
        grouped[int(item["depth"])].append(item)

    depths: list[int] = []
    alphas: list[float] = []

    print("\n=== FIGURE 8 ===")
    for d in sorted(grouped.keys()):
        sub = grouped[d]
        if len(sub) < 3:
            continue
        r = np.array([x["r"] for x in sub], dtype=np.float64)
        y = np.array([x["mid_sigma"] for x in sub], dtype=np.float64)
        m = np.isfinite(r) & np.isfinite(y) & (r > 0) & (y > 0)
        if int(np.sum(m)) < 2:
            continue
        log_r = safe_log(r[m])
        log_y = safe_log(y[m])
        coef = np.polyfit(log_r, log_y, 1)
        alpha_d = float(coef[0])
        depths.append(d)
        alphas.append(alpha_d)
        print(f"depth={d}: α={alpha_d:.4f}")

    if not depths:
        print("No enough grouped data for FIGURE 8")
        return
    plt.figure(figsize=(6, 5))
    plt.plot(depths, alphas, marker="o")
    plt.xlabel("depth")
    plt.ylabel("α")
    plt.title("Figure 8: α vs Depth")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "fig8_alpha_vs_depth.png", dpi=160)
    plt.close()


def estimate_spectrum_slope(eigvals: list[float] | np.ndarray) -> float:
    eigvals = np.array(eigvals, dtype=np.float64)
    eigvals = eigvals[eigvals > 1e-8]
    if eigvals.size < 2:
        return float("nan")
    idx = np.arange(1, len(eigvals) + 1, dtype=np.float64)
    log_i = safe_log(idx)
    log_l = safe_log(eigvals)
    coef = np.polyfit(log_i, log_l, 1)
    return float(coef[0])


def plot_fig9(results: list[dict], alpha_global: float) -> None:
    """Figure 9: α vs spectrum slope（当前以全局 α 作为每点 α）。"""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    slopes: list[float] = []
    alphas: list[float] = []
    for item in results:
        if "eigvals" not in item:
            continue
        slope = estimate_spectrum_slope(item["eigvals"])
        if not np.isfinite(slope):
            continue
        slopes.append(slope)
        alphas.append(alpha_global)

    if len(slopes) < 5:
        print("Not enough spectrum data")
        return

    plt.figure(figsize=(6, 5))
    plt.scatter(slopes, alphas, alpha=0.7, edgecolors="none")
    plt.xlabel("spectrum slope (log λ_i)")
    plt.ylabel("α")
    plt.title("Figure 9: α vs Spectrum Slope")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "fig9_alpha_vs_spectrum.png", dpi=160)
    plt.close()

    print("\n=== FIGURE 9 ===")
    print("Check: slope ↓ -> α ↓ (should correlate)")
