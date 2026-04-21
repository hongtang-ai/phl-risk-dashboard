"""α 理论分析：FIG7/FIG8、spectrum slope 关联与理论对照。"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PLOTS_DIR = Path(__file__).resolve().parents[1] / "plots"


def _ensure_plots_dir() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def _r2(y: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    if ss_tot <= 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def plot_log_mid_sigma_vs_r(results: list[dict]) -> float:
    """图7：log(mid·σ) vs log(r)，返回全局 α。"""
    _ensure_plots_dir()
    r = np.array([x["r"] for x in results], dtype=np.float64)
    y = np.array([x["mid_sigma"] for x in results], dtype=np.float64)
    m = np.isfinite(r) & np.isfinite(y) & (r > 0) & (y > 0)
    log_r = np.log(r[m] + 1e-8)
    log_y = np.log(y[m] + 1e-8)

    coef = np.polyfit(log_r, log_y, 1)
    alpha = float(coef[0])
    y_pred = coef[0] * log_r + coef[1]
    r2 = _r2(log_y, y_pred)

    plt.figure(figsize=(6, 5))
    plt.scatter(log_r, log_y, alpha=0.7, edgecolors="none")
    xs = np.linspace(float(log_r.min()), float(log_r.max()), 100)
    plt.plot(xs, coef[0] * xs + coef[1], label=f"α={alpha:.3f}, R²={r2:.3f}")
    plt.xlabel("log(r)")
    plt.ylabel("log(mid·σ)")
    plt.title("Figure 7: log(mid·σ) vs log(r)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "fig7_log_mid_sigma_vs_r.png", dpi=160)
    plt.close()

    print(f"[FIG7] α={alpha:.4f}, R²={r2:.4f}")
    return alpha


def plot_alpha_vs_depth(results: list[dict]) -> None:
    """图8：按 depth 分组估计 α。"""
    _ensure_plots_dir()
    grouped: dict[int, list[dict]] = defaultdict(list)
    for item in results:
        grouped[int(item["depth"])].append(item)

    depths: list[int] = []
    alphas: list[float] = []
    for d in sorted(grouped.keys()):
        sub = grouped[d]
        if len(sub) < 3:
            continue
        r = np.array([x["r"] for x in sub], dtype=np.float64)
        y = np.array([x["mid_sigma"] for x in sub], dtype=np.float64)
        m = np.isfinite(r) & np.isfinite(y) & (r > 0) & (y > 0)
        if int(np.sum(m)) < 2:
            continue
        log_r = np.log(r[m] + 1e-8)
        log_y = np.log(y[m] + 1e-8)
        coef = np.polyfit(log_r, log_y, 1)
        alpha_d = float(coef[0])
        depths.append(d)
        alphas.append(alpha_d)
        print(f"[depth={d}] α={alpha_d:.4f}")

    if not depths:
        print("[FIG8] 无足够数据估计 α vs depth")
        return
    plt.figure(figsize=(6, 5))
    plt.plot(depths, alphas, marker="o")
    plt.xlabel("depth")
    plt.ylabel("α")
    plt.title("Figure 8: α vs depth")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "fig8_alpha_vs_depth.png", dpi=160)
    plt.close()


def estimate_spectrum_slope(eigvals: list[float] | np.ndarray) -> float:
    eigvals = np.asarray(eigvals, dtype=np.float64)
    eigvals = eigvals[eigvals > 1e-8]
    if eigvals.size < 2:
        return float("nan")
    idx = np.arange(1, eigvals.size + 1, dtype=np.float64)
    log_i = np.log(idx)
    log_l = np.log(eigvals)
    coef = np.polyfit(log_i, log_l, 1)
    return float(coef[0])


def plot_alpha_vs_spectrum(results: list[dict]) -> None:
    _ensure_plots_dir()
    slopes: list[float] = []
    alphas: list[float] = []
    for item in results:
        eigvals = item.get("eigvals")
        alpha = item.get("alpha")
        if eigvals is None or alpha is None:
            continue
        slope = estimate_spectrum_slope(eigvals)
        if not np.isfinite(slope) or not np.isfinite(alpha):
            continue
        slopes.append(float(slope))
        alphas.append(float(alpha))

    if len(slopes) < 5:
        print("Not enough data for spectrum plot")
        return

    plt.figure(figsize=(6, 5))
    plt.scatter(slopes, alphas, alpha=0.7, edgecolors="none")
    plt.xlabel("spectrum slope (log λ_i)")
    plt.ylabel("α")
    plt.title("α vs spectrum slope")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "alpha_vs_spectrum.png", dpi=160)
    plt.close()
