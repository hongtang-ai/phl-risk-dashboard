from __future__ import annotations

"""Credit Rejection Analysis (PHL layer)."""

from typing import Any

import torch

from analyzer import compute_effective_rank, compute_mid_fraction, compute_ssi


def run_credit_rejection_analysis(model: torch.nn.Module, dataloader) -> dict[str, Any]:
    """
    对拒绝样本区域做 PHL 分析。

    拒绝区域定义：
    - 低通过概率：q < 0.5
    - 或边界不确定区：0.45 < q < 0.55
    """
    model.eval()
    zs: list[torch.Tensor] = []
    hs: list[torch.Tensor] = []
    qs: list[torch.Tensor] = []

    with torch.no_grad():
        for x, _ in dataloader:
            z, h = model(x)
            q = torch.sigmoid(z)
            zs.append(z)
            hs.append(h)
            qs.append(q)

    z = torch.cat(zs)
    h = torch.cat(hs)
    q = torch.cat(qs)

    reject_mask = (q < 0.5) | ((q > 0.45) & (q < 0.55))
    if int(reject_mask.sum().item()) < 2:
        return {
            "sigma": float("nan"),
            "mid": float("nan"),
            "effective_rank": float("nan"),
            "ssi": float("nan"),
            "risk_score": float("nan"),
            "eigvals": [],
            "reject_count": int(reject_mask.sum().item()),
        }

    z_r = z[reject_mask]
    h_r = h[reject_mask]
    q_r = q[reject_mask]

    sigma = float(z_r.std().item())
    mid = compute_mid_fraction(q_r)

    h_center = h_r - h_r.mean(0)
    cov = (h_center.T @ h_center) / max(len(h_center) - 1, 1)
    eigvals = torch.linalg.eigvalsh(cov).cpu().numpy()

    r = compute_effective_rank(eigvals)
    ssi = compute_ssi(eigvals)
    risk_score = float(ssi / (r + 1e-8))

    return {
        "sigma": sigma,
        "mid": mid,
        "effective_rank": r,
        "ssi": ssi,
        "risk_score": risk_score,
        "eigvals": eigvals.tolist(),
        "reject_count": int(reject_mask.sum().item()),
    }
