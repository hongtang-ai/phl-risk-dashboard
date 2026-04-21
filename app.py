import sys
from pathlib import Path
from typing import Any

import streamlit as st
import torch

sys.path.append(str(Path(__file__).parent))

from analyzer import compute_effective_rank, compute_mid_fraction, compute_ssi, load_demo_case
from data_loader_credit import load_german_credit_data
from ui.overview import render_overview
from ui.spectrum_tab import render_spectrum_tab
from ui.boundary_tab import render_boundary_tab
from ui.risk_tab import render_risk_tab
from ui.demo_tab import render_demo_tab

st.set_page_config(page_title="PHL Risk Dashboard", layout="wide")

if "use_demo" not in st.session_state:
    st.session_state.use_demo = False
if "analysis" not in st.session_state:
    st.session_state.analysis = None


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


def run_full_credit_pipeline(model: torch.nn.Module) -> dict[str, Any]:
    train_loader, test_loader = load_german_credit_data()
    _ = train_loader
    return run_credit_rejection_analysis(model, test_loader)


# ===== Header =====
col1, col2 = st.columns([1, 6])
with col1:
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        try:
            st.image(str(logo_path), width=80)
        except Exception:
            st.markdown("### 🏦")
    else:
        st.markdown("### 🏦")
with col2:
    st.title("PHL Risk Diagnostics Dashboard")
    st.caption("Structure-aware model risk analysis for credit decisions")

if st.session_state.get("use_demo", False):
    st.warning(
        "You are viewing a pre-configured demonstration case. "
        "Results do not reflect real-time model inference."
    )

# ===== Sidebar =====
st.sidebar.header("Configuration")

if st.session_state.get("use_demo", False):
    st.sidebar.info("Demo mode active: model upload disabled")
    model_file = None
else:
    model_file = st.sidebar.file_uploader("Upload Model (.pth)", type=["pth"])
scenario = st.sidebar.selectbox("Scenario", ["German Credit - Rejection Analysis"])
eps = st.sidebar.slider("Mid Threshold ε", 0.01, 0.1, 0.05)


# ===== Load Model =====
@st.cache_data
def load_model(file):
    if file:
        return torch.load(file)
    return None


model = load_model(model_file)

# ===== Demo (no model required) =====
st.sidebar.markdown("---")
st.sidebar.subheader("Demo")
if st.sidebar.button("Load German Credit Rejection Demo Case"):
    st.session_state.use_demo = True
    _demo = load_demo_case()
    st.session_state.analysis = _demo
    st.session_state["demo_data"] = _demo
    st.success("Demo case loaded")
if st.sidebar.button("Clear Demo Case"):
    st.session_state.use_demo = False
    st.session_state.analysis = None
    st.session_state.pop("demo_data", None)

effective_model = None if st.session_state.use_demo else model

# ===== Analysis =====
@st.cache_data
def get_analysis(_model, use_demo: bool):
    if use_demo:
        return load_demo_case()
    if _model is None:
        return None
    return run_full_credit_pipeline(_model)


if st.session_state.get("use_demo", False):
    analysis = st.session_state.analysis or load_demo_case()
    st.session_state.analysis = analysis
else:
    analysis = get_analysis(effective_model, False)

# Keep the controls visible and ready for future wiring.
st.sidebar.caption(f"Selected scenario: {scenario}")
st.sidebar.caption(f"Mid threshold ε: {eps:.2f}")
if st.session_state.use_demo:
    st.sidebar.success("Demo mode: using fixed case data (no model inference).")
elif model is None:
    st.sidebar.info("Upload a .pth model or load the demo case.")

# ===== Demo strip (bank-friendly entry) =====
st.markdown("## Demo: How PHL Explains a Loan Rejection Appeal")
if st.session_state.use_demo and analysis is not None:
    st.success("Demo case loaded")
    st.caption(analysis.get("case_name", "Demo case"))
else:
    st.caption("Tip: click **Load German Credit Rejection Demo Case** in the sidebar for a stable walkthrough.")

# ===== Tabs =====
tabs = st.tabs(
    ["Overview", "Spectrum Analysis", "Decision Boundary", "Risk Report", "申诉解释 Demo"]
)

with tabs[0]:
    render_overview(effective_model, analysis)

with tabs[1]:
    render_spectrum_tab(effective_model, analysis)

with tabs[2]:
    render_boundary_tab(effective_model, analysis)

with tabs[3]:
    render_risk_tab(effective_model, analysis)

with tabs[4]:
    render_demo_tab()

# ===== Footer =====
st.markdown("---")
st.caption("Developed by Independent Researcher | Focus on Structured XAI")
