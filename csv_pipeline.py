"""CSV -> POC structural analysis dict compatible with the professional workbench."""

from __future__ import annotations

import io
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
