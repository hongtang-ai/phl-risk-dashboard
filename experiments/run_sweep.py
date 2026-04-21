"""MNIST 二分类（标签>5）上扫描 MLP，估计 σ、mid、有效秩与投影方差。"""

from __future__ import annotations

import math
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from analysis.metrics import compute_mid_from_z, gaussian_mid, normalize_z, theoretical_mid
from analysis.projection import compute_projection_variance
from analysis.spectrum import compute_effective_rank, plot_spectrum
from experiments.configs import BATCH_SIZE, CONFIGS, DEPTHS, EPOCHS, LR, SEED, WIDTHS
from models.mlp import MLP
from models.utils import get_device, set_seed


def _make_binary_targets(dataset) -> torch.Tensor:
    ys = torch.tensor([int(dataset[i][1]) for i in range(len(dataset))], dtype=torch.long)
    return (ys > 5).float()


def load_mnist_binary(
    root: str | Path = "data",
) -> tuple[DataLoader, DataLoader, torch.Tensor]:
    """返回 train/test DataLoader 及训练集二值标签张量（与数据集顺序一致）。"""
    tfm = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train_full = datasets.MNIST(root=str(root), train=True, download=True, transform=tfm)
    test_full = datasets.MNIST(root=str(root), train=False, download=True, transform=tfm)

    train_y = _make_binary_targets(train_full)

    train_ds = train_full
    test_ds = test_full

    gen = torch.Generator()
    gen.manual_seed(SEED)
    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=gen,
        num_workers=0,
    )
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    return train_loader, test_loader, train_y


def _collect_test_activations(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    model.eval()
    zs: list[torch.Tensor] = []
    hs: list[torch.Tensor] = []
    qs: list[torch.Tensor] = []
    with torch.no_grad():
        for x, _ in loader:
            x = x.to(device)
            z, h = model(x)
            q = torch.sigmoid(z)
            zs.append(z.detach().cpu())
            hs.append(h.detach().cpu())
            qs.append(q.detach().cpu())
    return torch.cat(zs), torch.cat(hs), torch.cat(qs)


def _train_one(
    model: nn.Module,
    train_loader: DataLoader,
    train_y: torch.Tensor,
    device: torch.device,
    epochs: int,
) -> None:
    criterion = nn.BCEWithLogitsLoss()
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    model.train()
    for ep in range(epochs):
        for x, idx in train_loader:
            x = x.to(device)
            idx = idx.to(device)
            y = train_y[idx].to(device)
            opt.zero_grad(set_to_none=True)
            z, _ = model(x)
            loss = criterion(z, y)
            loss.backward()
            opt.step()


def _indexed_train_loader(train_ds, train_y: torch.Tensor) -> DataLoader:
    class _Wrap(torch.utils.data.Dataset):
        def __init__(self, base):
            self.base = base

        def __len__(self):
            return len(self.base)

        def __getitem__(self, i):
            x, _ = self.base[i]
            return x, i

    gen = torch.Generator()
    gen.manual_seed(SEED)
    return DataLoader(
        _Wrap(train_ds),
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=gen,
        num_workers=0,
    )


def run_sweep(
    root: str | Path | None = None,
    results_path: str | Path | None = None,
) -> list[dict]:
    """
    执行完整扫描，打印每个模型的 σ、mid、r，并写入 results/results.json。
    """
    root = Path(root or Path(__file__).resolve().parents[1] / "data")
    results_path = Path(results_path or Path(__file__).resolve().parents[1] / "results" / "results.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    set_seed(SEED)
    device = get_device()

    train_loader, test_loader, train_y = load_mnist_binary(root=root)
    train_ds = train_loader.dataset
    train_loader = _indexed_train_loader(train_ds, train_y)

    rows: list[dict] = []
    for width in WIDTHS:
        for depth in DEPTHS:
            for cfg in CONFIGS:
                use_bn = bool(cfg["bn"])
                use_res = bool(cfg["res"])
                tag = f"w{width}_d{depth}_bn{int(use_bn)}_res{int(use_res)}"
                model = MLP(depth=depth, width=width, use_bn=use_bn, use_residual=use_res).to(device)
                _train_one(model, train_loader, train_y, device, EPOCHS)

                z, h, _ = _collect_test_activations(model, test_loader, device)
                w = model.fc_out.weight.detach().view(-1).cpu()
                sigma = float(z.float().std().item())
                mid_raw = compute_mid_from_z(z)
                z_norm = normalize_z(z)
                mid_norm = compute_mid_from_z(z_norm)
                r = compute_effective_rank(h)
                mid_sigma = mid_raw * sigma
                sqrt_r = math.sqrt(max(r, 0.0))
                var_proj = compute_projection_variance(h, w)
                theo = theoretical_mid(sigma)
                gmid = gaussian_mid(sigma)
                h_np = h.detach().cpu().numpy()
                cov = np.cov(h_np.T)
                eigvals = np.linalg.eigvalsh(cov)
                eigvals = np.sort(eigvals)[::-1]
                plot_spectrum(cov, f"d{depth}_w{width}_bn{int(use_bn)}_res{int(use_res)}")

                row = {
                    "tag": tag,
                    "width": width,
                    "depth": depth,
                    "bn": use_bn,
                    "res": use_res,
                    "sigma": sigma,
                    "mid_raw": mid_raw,
                    "mid_norm": mid_norm,
                    "mid_sigma": mid_sigma,
                    "sqrt_r": sqrt_r,
                    "r": r,
                    "effective_rank": r,
                    "var_proj": var_proj,
                    "theoretical_mid": theo,
                    "gaussian_mid": gmid,
                    "eigvals": eigvals.tolist(),
                }
                rows.append(row)
                print(
                    f"[{tag}] σ={sigma:.4f} mid_raw={mid_raw:.4f} mid_norm={mid_norm:.4f} "
                    f"mid*σ={mid_sigma:.4f} sqrt(r)={sqrt_r:.4f} r={r:.4f} "
                    f"var_proj={var_proj:.6f} theo_mid={theo:.4f} g_mid={gmid:.4f}"
                )

    with results_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    return rows


if __name__ == "__main__":
    run_sweep()
