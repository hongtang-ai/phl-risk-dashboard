"""CSV -> POC structural analysis dict compatible with the professional workbench."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

from analyzer import compute_effective_rank, compute_ssi
from inference import predict_probabilities


def _pick_column(columns: list[str], candidates: list[str]) -> str | None:
    for c in columns:
        cl = c.lower()
        if any(k in cl for k in candidates):
            return c
    return None


def _extract_core_features(df: pd.DataFrame) -> np.ndarray:
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if len(numeric_cols) < 3:
        raise ValueError("CSV needs at least 3 numeric columns to run model inference.")

    age_col = _pick_column(numeric_cols, ["age"])
    credit_col = _pick_column(numeric_cols, ["credit", "score"])
    amount_col = _pick_column(numeric_cols, ["amount", "loan"])

    if age_col and credit_col and amount_col:
        core = df[[age_col, credit_col, amount_col]].to_numpy(dtype=np.float64)
    else:
        # Fallback to first three numeric columns in order.
        core = df[numeric_cols[:3]].to_numpy(dtype=np.float64)
    return core


def _ks_statistic_np(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    # === UPDATED ===
    """Robust two-sample KS approximation without scipy dependency."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if a.size < 2 or b.size < 2:
        return 0.0, 1.0

    a_sorted = np.sort(a)
    b_sorted = np.sort(b)
    # Use merged support points to estimate empirical CDF gap.
    all_vals = np.sort(np.unique(np.concatenate([a_sorted, b_sorted])))
    cdf_a = np.searchsorted(a_sorted, all_vals, side="right") / a_sorted.size
    cdf_b = np.searchsorted(b_sorted, all_vals, side="right") / b_sorted.size
    stat = float(np.max(np.abs(cdf_a - cdf_b)))

    # Kolmogorov asymptotic approximation with finite-sample correction.
    n1, n2 = a_sorted.size, b_sorted.size
    en = np.sqrt(n1 * n2 / (n1 + n2))
    lam = (en + 0.12 + 0.11 / max(en, 1e-8)) * stat
    pvalue = float(np.clip(2.0 * np.exp(-2.0 * lam * lam), 0.0, 1.0))
    return stat, pvalue


def compute_drift(reference_df: pd.DataFrame, current_df: pd.DataFrame) -> dict[str, dict[str, float | str]]:
    drift: dict[str, dict[str, float | str]] = {}
    common_cols = list(set(reference_df.columns) & set(current_df.columns))
    for col in common_cols:
        if pd.api.types.is_numeric_dtype(reference_df[col]) and pd.api.types.is_numeric_dtype(current_df[col]):
            ref_vals = reference_df[col].dropna().to_numpy()
            cur_vals = current_df[col].dropna().to_numpy()
            n_ref = int(ref_vals.size)
            n_cur = int(cur_vals.size)
            stat, pvalue = _ks_statistic_np(ref_vals, cur_vals)
            small_sample = n_ref < 30 or n_cur < 30
            drift[col] = {
                "ks_stat": round(float(stat), 4),
                "pvalue": round(float(pvalue), 4),
                "sample_size_ref": n_ref,
                "sample_size_cur": n_cur,
                "drift_level": (
                    "Small Sample"
                    if small_sample
                    else "High" if stat > 0.2 else "Medium" if stat > 0.1 else "Low"
                ),
            }
    return drift


def compute_bias(df: pd.DataFrame) -> dict[str, float | str] | None:
    # === UPDATED ===
    if "age" not in df.columns or "q" not in df.columns:
        return None

    def _group_bias(low_group: np.ndarray, high_group: np.ndarray) -> dict[str, float | str]:
        if low_group.size < 2 or high_group.size < 2:
            return {"group_diff": float("nan"), "significance_proxy": float("nan"), "bias_level": "Small Sample"}
        low_mean = float(np.mean(low_group))
        high_mean = float(np.mean(high_group))
        diff = abs(low_mean - high_mean)
        pooled = float(
            np.sqrt((np.var(low_group, ddof=1) / low_group.size) + (np.var(high_group, ddof=1) / high_group.size))
        )
        t_stat = 0.0 if pooled < 1e-12 else diff / pooled
        return {
            "group_diff": round(diff, 4),
            "significance_proxy": round(float(t_stat), 4),
            "bias_level": "High" if diff > 0.15 else "Medium" if diff > 0.08 else "Low",
        }

    young_q = df[df["age"] < 40]["q"].dropna().to_numpy(dtype=np.float64)
    old_q = df[df["age"] >= 40]["q"].dropna().to_numpy(dtype=np.float64)
    age_bias = _group_bias(young_q, old_q)

    credit_col = "credit_score" if "credit_score" in df.columns else None
    if credit_col is not None:
        high_credit_q = df[df[credit_col] > 680]["q"].dropna().to_numpy(dtype=np.float64)
        low_credit_q = df[df[credit_col] <= 680]["q"].dropna().to_numpy(dtype=np.float64)
        credit_bias = _group_bias(low_credit_q, high_credit_q)
    else:
        credit_bias = {"group_diff": float("nan"), "significance_proxy": float("nan"), "bias_level": "Unavailable"}

    return {
        "age_group": age_bias,
        "credit_group_680_threshold": credit_bias,
    }


def run_csv_pipeline(uploaded_file: io.BytesIO | Any) -> dict[str, Any]:
    """
    Numeric columns: last column treated as label; preceding numeric columns as features.
    Uses a small untrained MLP + covariance of logits (POC only).
    """
    df = pd.read_csv(uploaded_file)
    if df.empty:
        raise ValueError("CSV file is empty")

    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        raise ValueError("CSV must contain at least two numeric columns (features + label).")

    core_x = _extract_core_features(df)
    inference_probs = predict_probabilities(core_x)
    q_first = float(inference_probs[0]) if inference_probs.size > 0 else float("nan")
    q_mean = float(np.mean(inference_probs)) if inference_probs.size > 0 else float("nan")

    # Build a lightweight monitoring frame for drift/bias.
    monitor_df = pd.DataFrame(core_x, columns=["age", "credit_score", "loan_amount"])
    monitor_df["q"] = inference_probs
    reference_df = monitor_df.head(max(1, len(monitor_df) // 2))
    current_df = monitor_df.tail(max(1, len(monitor_df) // 2))
    drift = compute_drift(reference_df, current_df)
    bias = compute_bias(monitor_df)

    X = numeric_df.iloc[:, :-1].values.astype(np.float64)

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_t = torch.from_numpy(X).float()

    model = nn.Sequential(
        nn.Linear(X.shape[1], 64),
        nn.ReLU(),
        nn.Linear(64, 64),
        nn.ReLU(),
        nn.Linear(64, 2),
    )
    model.eval()

    with torch.no_grad():
        logits = model(X_t)

    probs = torch.softmax(logits, dim=1)[:, 1].numpy()
    mid = float(np.mean(np.abs(probs - 0.5) < 0.05))

    h = logits.numpy().astype(np.float64)
    if h.shape[0] < 2:
        raise ValueError("Need at least 2 rows for covariance.")

    cov = np.cov(h.T)
    eigvals = np.linalg.eigvalsh(cov.astype(np.float64))
    eigvals = np.sort(np.real(eigvals))[::-1]
    eigvals = eigvals[np.isfinite(eigvals)]
    eigvals = eigvals[eigvals >= 0]

    r = compute_effective_rank(eigvals)
    ssi = compute_ssi(eigvals)
    r_f = float(r) if np.isfinite(r) else float("nan")
    ssi_f = float(ssi) if np.isfinite(ssi) else float("nan")
    risk_score = float(ssi_f / (r_f + 1e-8)) if np.isfinite(r_f) and np.isfinite(ssi_f) else float("nan")

    sigma = float(np.std(probs, ddof=1)) if probs.size > 1 else float(np.std(probs))

    ev_list = eigvals.tolist()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(ev_list))), y=ev_list, mode="lines+markers"))
    fig.update_layout(
        title="Covariance Spectrum (CSV POC)",
        xaxis_title="Index",
        yaxis_title="Eigenvalue (log scale)",
        yaxis_type="log",
    )

    if np.isfinite(risk_score):
        risk_level = "HIGH" if risk_score > 0.15 else "MEDIUM" if risk_score > 0.08 else "LOW"
    else:
        risk_level = "UNKNOWN"

    return {
        "case_name": "Uploaded CSV (POC)",
        "q": q_first,
        "inference_prob_mean": q_mean,
        "inference_prob_first": q_first,
        "drift": drift,
        "bias": bias,
        "monitoring_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sigma": sigma,
        "mid": mid,
        "effective_rank": r_f,
        "ssi": ssi_f,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "eigvals": ev_list,
        "spectrum_fig": fig,
        "sample_size": int(len(df)),
        "n_features": int(X.shape[1]),
    }
