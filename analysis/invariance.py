"""尺度不变性：对比原始 mid 与标准化 logit 后的 mid 与 1/σ 的相关性。"""

from __future__ import annotations

from typing import Any


def compare_invariance(results: list[dict[str, Any]]) -> dict[str, float]:
    """
    判断结构 vs scale：比较 mid_raw、mid_norm 与 1/σ 的 Pearson 相关。
    """
    import numpy as np

    mids_raw = np.array([r["mid_raw"] for r in results], dtype=np.float64)
    mids_norm = np.array([r["mid_norm"] for r in results], dtype=np.float64)
    sigmas = np.array([r["sigma"] for r in results], dtype=np.float64)
    inv = 1.0 / sigmas

    def _corr(a: np.ndarray, b: np.ndarray) -> float:
        m = np.isfinite(a) & np.isfinite(b)
        if int(m.sum()) < 2:
            return float("nan")
        aa, bb = a[m], b[m]
        if float(np.std(aa)) == 0.0 or float(np.std(bb)) == 0.0:
            return float("nan")
        return float(np.corrcoef(aa, bb)[0, 1])

    return {
        "corr_raw_vs_1_sigma": _corr(mids_raw, inv),
        "corr_norm_vs_1_sigma": _corr(mids_norm, inv),
    }
