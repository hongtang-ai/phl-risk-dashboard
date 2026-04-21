"""Projection density 全量可视化函数。"""

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
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    if ss_tot <= 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def plot_mid_vs_inv_sigma(results: list[dict]) -> None:
    _ensure_plots_dir()
    x = np.array([1.0 / r["sigma"] for r in results], dtype=np.float64)
    y = np.array([r["mid_raw"] for r in results], dtype=np.float64)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    coef = np.polyfit(x, y, 1)
    y_pred = coef[0] * x + coef[1]
    r2 = _r2(y, y_pred)

    plt.figure(figsize=(6, 5))
    plt.scatter(x, y, alpha=0.7, edgecolors="none")
    xs = np.linspace(float(x.min()), float(x.max()), 100)
    plt.plot(xs, coef[0] * xs + coef[1], label=f"R²={r2:.3f}")
    plt.xlabel("1/σ")
    plt.ylabel("mid")
    plt.title("mid vs 1/σ")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "mid_vs_inv_sigma.png", dpi=160)
    plt.close()
    print(f"[mid vs 1/σ] R²={r2:.4f}")


def plot_mid_sigma_vs_r(results: list[dict]) -> None:
    _ensure_plots_dir()
    x = np.array([r["r"] for r in results], dtype=np.float64)
    y = np.array([r["mid_sigma"] for r in results], dtype=np.float64)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    coef = np.polyfit(x, y, 1)
    y_pred = coef[0] * x + coef[1]
    r2 = _r2(y, y_pred)

    plt.figure(figsize=(6, 5))
    plt.scatter(x, y, alpha=0.7, edgecolors="none")
    xs = np.linspace(float(x.min()), float(x.max()), 100)
    plt.plot(xs, coef[0] * xs + coef[1], label=f"R²={r2:.3f}")
    plt.xlabel("r")
    plt.ylabel("mid * σ")
    plt.title("mid·σ vs r")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "mid_sigma_vs_r.png", dpi=160)
    plt.close()
    print(f"[mid·σ vs r] R²={r2:.4f}")


def fit_alpha(results: list[dict]) -> float:
    x = np.array([r["r"] for r in results], dtype=np.float64)
    y = np.array([r["mid_sigma"] for r in results], dtype=np.float64)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    log_x = np.log(x[m] + 1e-8)
    log_y = np.log(y[m] + 1e-8)
    coef = np.polyfit(log_x, log_y, 1)
    alpha = float(coef[0])
    print("=" * 60)
    print(f"Estimated α = {alpha:.4f}")
    print("=" * 60)
    return alpha


def plot_log_log(results: list[dict]) -> None:
    _ensure_plots_dir()
    x = np.array([r["r"] for r in results], dtype=np.float64)
    y = np.array([r["mid_sigma"] for r in results], dtype=np.float64)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    log_x = np.log(x[m] + 1e-8)
    log_y = np.log(y[m] + 1e-8)
    coef = np.polyfit(log_x, log_y, 1)
    xs = np.linspace(float(log_x.min()), float(log_x.max()), 200)

    plt.figure(figsize=(6, 5))
    plt.scatter(log_x, log_y, alpha=0.7, edgecolors="none")
    plt.plot(xs, coef[0] * xs + coef[1], label=f"α={coef[0]:.3f}")
    plt.xlabel("log(r)")
    plt.ylabel("log(mid·σ)")
    plt.title("Log-Log Fit")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "log_mid_sigma_vs_r.png", dpi=160)
    plt.close()


def plot_alpha_vs_depth(results: list[dict]) -> None:
    _ensure_plots_dir()
    grouped: dict[int, list[dict]] = defaultdict(list)
    for row in results:
        grouped[int(row["depth"])].append(row)

    depths: list[int] = []
    alphas: list[float] = []
    for d in sorted(grouped.keys()):
        sub = grouped[d]
        if len(sub) < 2:
            continue
        x = np.array([r["r"] for r in sub], dtype=np.float64)
        y = np.array([r["mid_sigma"] for r in sub], dtype=np.float64)
        m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
        if int(np.sum(m)) < 2:
            continue
        coef = np.polyfit(np.log(x[m] + 1e-8), np.log(y[m] + 1e-8), 1)
        depths.append(d)
        alphas.append(float(coef[0]))

    if not depths:
        return
    plt.figure(figsize=(6, 5))
    plt.plot(depths, alphas, marker="o")
    plt.xlabel("depth")
    plt.ylabel("α")
    plt.title("α vs depth")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "alpha_vs_depth.png", dpi=160)
    plt.close()
