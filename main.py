from __future__ import annotations

from typing import Any

import numpy as np
import torch
import torch.nn as nn

from analyzer import (
    compute_cov_eigvals,
    compute_effective_rank,
    compute_mid_from_z,
    compute_projection_variance,
    compute_ssi,
    estimate_sigma,
    estimate_spectrum_slope,
    gaussian_mid,
    normalize_z,
    spectrum_alpha_analyzer,
    theoretical_mid,
)
from config import ExperimentConfig, SweepConfig
from credit_analysis import run_credit_rejection_analysis
from data_loader import load_mnist_binary
from data_loader_credit import load_german_credit_data
from finance_wrapper import compute_financial_metrics, generate_risk_report
from model import MLP
from plot_utils import (
    plot_alpha_vs_depth,
    plot_alpha_vs_spectrum,
    plot_credit_spectrum,
    plot_log_mid_sigma_vs_r,
    plot_mid_heatmap,
    plot_mid_sigma_vs_r,
    plot_mid_vs_inv_sigma,
    plot_spectrum,
)
from report_generator import generate_credit_report
from utils import ensure_dirs, get_device, save_json, set_seed


def train_one(
    model: nn.Module,
    train_loader,
    train_y: torch.Tensor,
    device: torch.device,
    epochs: int,
    lr: float,
) -> None:
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    for _ in range(epochs):
        for x, idx in train_loader:
            x = x.to(device)
            y = train_y[idx].to(device)
            optimizer.zero_grad(set_to_none=True)
            z, _ = model(x)
            loss = criterion(z, y)
            loss.backward()
            optimizer.step()


def collect_outputs(model: nn.Module, test_loader, device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    model.eval()
    zs, hs = [], []
    with torch.no_grad():
        for x, _ in test_loader:
            x = x.to(device)
            z, h = model(x)
            zs.append(z.detach().cpu())
            hs.append(h.detach().cpu())
    return torch.cat(zs), torch.cat(hs)


def run_experiments(sweep: SweepConfig) -> list[dict[str, Any]]:
    set_seed(sweep.seed)
    device = get_device()
    ensure_dirs(sweep.data_dir, sweep.plots_dir, sweep.results_path.parent)

    # 用默认 batch/epoch 作为全局设置，再按单实验配置覆盖
    base_exp = ExperimentConfig()
    train_loader, test_loader, train_y = load_mnist_binary(
        root=sweep.data_dir,
        batch_size=base_exp.batch_size,
        seed=sweep.seed,
    )

    results: list[dict[str, Any]] = []
    for width in sweep.widths:
        for depth in sweep.depths:
            for st in sweep.structures:
                exp = ExperimentConfig(
                    width=width,
                    depth=depth,
                    use_bn=bool(st["bn"]),
                    use_residual=bool(st["res"]),
                    batch_size=base_exp.batch_size,
                    epochs=base_exp.epochs,
                    lr=base_exp.lr,
                )
                tag = f"w{exp.width}_d{exp.depth}_bn{int(exp.use_bn)}_res{int(exp.use_residual)}"
                model = MLP(
                    depth=exp.depth,
                    width=exp.width,
                    use_bn=exp.use_bn,
                    use_residual=exp.use_residual,
                ).to(device)
                train_one(model, train_loader, train_y, device, epochs=exp.epochs, lr=exp.lr)
                z, h = collect_outputs(model, test_loader, device)

                sigma = estimate_sigma(z)
                mid_raw = compute_mid_from_z(z)
                mid_norm = compute_mid_from_z(normalize_z(z))
                mid_sigma = mid_raw * sigma

                eigvals = compute_cov_eigvals(h, sample_size=sweep.analysis_sample_size)
                r = compute_effective_rank(eigvals)
                ssi = compute_ssi(eigvals)
                slope = estimate_spectrum_slope(eigvals)

                w = model.fc_out.weight.detach().view(-1).cpu()
                var_proj = compute_projection_variance(h, w)

                row: dict[str, Any] = {
                    "tag": tag,
                    "width": exp.width,
                    "depth": exp.depth,
                    "bn": exp.use_bn,
                    "res": exp.use_residual,
                    "sigma": sigma,
                    "mid_raw": mid_raw,
                    "mid_norm": mid_norm,
                    "mid_sigma": mid_sigma,
                    "r": r,
                    "effective_rank": r,
                    "ssi": ssi,
                    "spectrum_slope": slope,
                    "var_proj": var_proj,
                    "theoretical_mid": theoretical_mid(sigma),
                    "gaussian_mid": gaussian_mid(sigma),
                    "eigvals": eigvals.tolist(),
                }

                fin = compute_financial_metrics(row)
                row.update(fin)
                results.append(row)

                plot_spectrum(eigvals, sweep.plots_dir, tag)
                print(
                    f"[{tag}] σ={sigma:.4f} mid={mid_raw:.4f} r={r:.4f} "
                    f"ssi={ssi:.4f} risk={row['risk_score']:.4f}"
                )

    alpha_info = spectrum_alpha_analyzer(results)
    for row in results:
        row["alpha_global"] = alpha_info["alpha"]

    save_json(sweep.results_path, results)
    print(f"\n[alpha] global α={alpha_info['alpha']:.4f}, R²={alpha_info['r2']:.4f}")
    return results


def main() -> None:
    sweep = SweepConfig()
    results = run_experiments(sweep)

    # 统一绘图入口
    plot_mid_vs_inv_sigma(results, sweep.plots_dir)
    plot_mid_sigma_vs_r(results, sweep.plots_dir)
    plot_log_mid_sigma_vs_r(results, sweep.plots_dir)
    plot_alpha_vs_depth(results, sweep.plots_dir)
    plot_alpha_vs_spectrum(results, sweep.plots_dir)

    # 金融语义风险报告
    generate_risk_report(results)
    run_credit_experiment(sweep)


def train_credit_model(model: nn.Module, train_loader, epochs: int = 20, lr: float = 1e-3) -> None:
    """German Credit 的标准 BCE 训练。"""
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    for _ in range(epochs):
        for x, y in train_loader:
            optimizer.zero_grad(set_to_none=True)
            z, _ = model(x)
            loss = criterion(z, y)
            loss.backward()
            optimizer.step()


def _collect_credit_accept_eigvals(model: nn.Module, dataloader) -> np.ndarray:
    """采集接受样本区域（q>=0.55）的谱。"""
    model.eval()
    hs: list[torch.Tensor] = []
    qs: list[torch.Tensor] = []
    with torch.no_grad():
        for x, _ in dataloader:
            z, h = model(x)
            q = torch.sigmoid(z)
            hs.append(h)
            qs.append(q)
    h = torch.cat(hs)
    q = torch.cat(qs)
    accept_mask = q >= 0.55
    if int(accept_mask.sum().item()) < 2:
        return np.array([], dtype=np.float64)
    h_a = h[accept_mask]
    h_c = h_a - h_a.mean(0)
    cov = (h_c.T @ h_c) / max(len(h_c) - 1, 1)
    eigvals = torch.linalg.eigvalsh(cov).cpu().numpy()
    return np.sort(eigvals)[::-1]


def run_credit_experiment(sweep: SweepConfig) -> None:
    """
    新增金融实验：
    German Credit 上执行“信贷拒绝解释”。
    不修改 PHL 核心计算函数，仅复用。
    """
    print("\n===== CREDIT REJECTION EXPERIMENT =====")
    try:
        train_loader, test_loader = load_german_credit_data(batch_size=128)
    except Exception as exc:  # noqa: BLE001
        print(f"[credit] 数据加载失败，跳过信用实验: {exc}")
        return

    first_x, _ = next(iter(train_loader))
    in_dim = int(first_x.shape[1])
    model = MLP(depth=3, width=64, use_bn=False, use_residual=False, in_dim=in_dim)
    train_credit_model(model, train_loader, epochs=20, lr=1e-3)

    stats = run_credit_rejection_analysis(model, test_loader)
    generate_credit_report(stats)

    eigvals_accept = _collect_credit_accept_eigvals(model, test_loader)
    eigvals_reject = np.array(stats.get("eigvals", []), dtype=np.float64)
    if eigvals_reject.size > 0 and eigvals_accept.size > 0:
        plot_credit_spectrum(eigvals_reject, eigvals_accept, sweep.plots_dir)
    plot_mid_heatmap([stats.get("mid", float("nan"))], sweep.plots_dir)
    print(stats)


if __name__ == "__main__":
    main()
