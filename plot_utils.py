from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _r2(y: np.ndarray, yhat: np.ndarray) -> float:
    ss_tot = float(((y - y.mean()) ** 2).sum())
    if ss_tot <= 0:
        return float("nan")
    return float(1.0 - ((y - yhat) ** 2).sum() / ss_tot)


def plot_mid_vs_inv_sigma(results: list[dict], plots_dir: Path) -> None:
    x = np.array([1.0 / r["sigma"] for r in results], dtype=np.float64)
    y = np.array([r["mid_raw"] for r in results], dtype=np.float64)
    coef = np.polyfit(x, y, 1)
    yhat = coef[0] * x + coef[1]
    r2 = _r2(y, yhat)

    plt.figure(figsize=(6, 5))
    plt.scatter(x, y, alpha=0.7, edgecolors="none")
    xs = np.linspace(float(x.min()), float(x.max()), 100)
    plt.plot(xs, coef[0] * xs + coef[1], label=f"R²={r2:.3f}")
    plt.xlabel("1/σ")
    plt.ylabel("mid")
    plt.title("mid vs 1/σ")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / "mid_vs_inv_sigma.png", dpi=160)
    plt.close()


def plot_mid_sigma_vs_r(results: list[dict], plots_dir: Path) -> None:
    x = np.array([r["r"] for r in results], dtype=np.float64)
    y = np.array([r["mid_sigma"] for r in results], dtype=np.float64)
    coef = np.polyfit(x, y, 1)

    plt.figure(figsize=(6, 5))
    plt.scatter(x, y, alpha=0.7, edgecolors="none")
    xs = np.linspace(float(x.min()), float(x.max()), 100)
    plt.plot(xs, coef[0] * xs + coef[1], label="linear fit")
    plt.xlabel("r")
    plt.ylabel("mid * σ")
    plt.title("mid·σ vs r")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / "mid_sigma_vs_r.png", dpi=160)
    plt.close()


def plot_log_mid_sigma_vs_r(results: list[dict], plots_dir: Path) -> None:
    x = np.array([r["r"] for r in results], dtype=np.float64)
    y = np.array([r["mid_sigma"] for r in results], dtype=np.float64)
    m = (x > 0) & (y > 0)
    log_x = np.log(x[m] + 1e-8)
    log_y = np.log(y[m] + 1e-8)
    coef = np.polyfit(log_x, log_y, 1)

    plt.figure(figsize=(6, 5))
    plt.scatter(log_x, log_y, alpha=0.7, edgecolors="none")
    xs = np.linspace(float(log_x.min()), float(log_x.max()), 100)
    plt.plot(xs, coef[0] * xs + coef[1], label=f"α={coef[0]:.3f}")
    plt.xlabel("log(r)")
    plt.ylabel("log(mid·σ)")
    plt.title("Figure 7: log(mid·σ) vs log(r)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / "fig7_log_mid_sigma_vs_r.png", dpi=160)
    plt.close()


def plot_alpha_vs_depth(results: list[dict], plots_dir: Path) -> None:
    depth_to_alpha: dict[int, float] = {}
    for d in sorted(set(int(r["depth"]) for r in results)):
        sub = [r for r in results if int(r["depth"]) == d and r["r"] > 0 and r["mid_sigma"] > 0]
        if len(sub) < 2:
            continue
        x = np.log(np.array([r["r"] for r in sub], dtype=np.float64) + 1e-8)
        y = np.log(np.array([r["mid_sigma"] for r in sub], dtype=np.float64) + 1e-8)
        a, _ = np.polyfit(x, y, 1)
        depth_to_alpha[d] = float(a)

    if not depth_to_alpha:
        return
    xs = np.array(list(depth_to_alpha.keys()), dtype=np.int64)
    ys = np.array(list(depth_to_alpha.values()), dtype=np.float64)
    plt.figure(figsize=(6, 5))
    plt.plot(xs, ys, marker="o")
    plt.xlabel("depth")
    plt.ylabel("α")
    plt.title("Figure 8: α vs depth")
    plt.tight_layout()
    plt.savefig(plots_dir / "fig8_alpha_vs_depth.png", dpi=160)
    plt.close()


def plot_alpha_vs_spectrum(results: list[dict], plots_dir: Path) -> None:
    slopes = []
    alphas = []
    for row in results:
        if "spectrum_slope" not in row or "alpha_global" not in row:
            continue
        slopes.append(float(row["spectrum_slope"]))
        alphas.append(float(row["alpha_global"]))
    if len(slopes) < 3:
        return

    plt.figure(figsize=(6, 5))
    plt.scatter(slopes, alphas, alpha=0.7, edgecolors="none")
    plt.xlabel("spectrum slope (log λ_i)")
    plt.ylabel("α")
    plt.title("Figure 9: α vs spectrum slope")
    plt.tight_layout()
    plt.savefig(plots_dir / "fig9_alpha_vs_spectrum.png", dpi=160)
    plt.close()


def plot_spectrum(eigvals: np.ndarray, plots_dir: Path, name: str) -> None:
    ev = np.asarray(eigvals, dtype=np.float64)
    ev = np.clip(ev, 1e-12, None)
    plt.figure(figsize=(6, 4))
    plt.plot(ev)
    plt.yscale("log")
    plt.xlabel("index")
    plt.ylabel("eigenvalue (log)")
    plt.title(f"Spectrum: {name}")
    plt.tight_layout()
    plt.savefig(plots_dir / f"spectrum_{name}.png", dpi=160)
    plt.close()


def plot_credit_spectrum(
    eigvals_reject: np.ndarray | list[float],
    eigvals_accept: np.ndarray | list[float],
    plots_dir: Path,
) -> None:
    """拒绝样本与接受样本的谱对比图。"""
    er = np.asarray(eigvals_reject, dtype=np.float64)
    ea = np.asarray(eigvals_accept, dtype=np.float64)
    er = np.clip(er, 1e-12, None)
    ea = np.clip(ea, 1e-12, None)

    plt.figure(figsize=(6, 5))
    plt.plot(er, label="reject")
    plt.plot(ea, label="accept")
    plt.yscale("log")
    plt.legend()
    plt.title("Spectrum Comparison")
    plt.tight_layout()
    plt.savefig(plots_dir / "credit_spectrum.png", dpi=160)
    plt.close()


def plot_mid_heatmap(mid_values: np.ndarray | list[float], plots_dir: Path) -> None:
    """信用任务中 mid 分布直方图。"""
    mids = np.asarray(mid_values, dtype=np.float64)
    mids = mids[np.isfinite(mids)]
    if mids.size == 0:
        return
    plt.figure(figsize=(6, 5))
    plt.hist(mids, bins=30)
    plt.title("Mid Density Distribution")
    plt.tight_layout()
    plt.savefig(plots_dir / "credit_mid_hist.png", dpi=160)
    plt.close()
