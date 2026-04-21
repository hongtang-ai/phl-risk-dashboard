import streamlit as st
import torch
from pathlib import Path

from analysis_pipeline import run_full_credit_pipeline
from ui.overview import render_overview
from ui.spectrum_tab import render_spectrum_tab
from ui.boundary_tab import render_boundary_tab
from ui.risk_tab import render_risk_tab
from ui.demo_tab import render_demo_tab

st.set_page_config(page_title="PHL Risk Dashboard", layout="wide")

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

# ===== Sidebar =====
st.sidebar.header("Configuration")

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

# ===== Analysis =====
@st.cache_data
def get_analysis(_model):
    if _model is None:
        return None
    return run_full_credit_pipeline(_model)


analysis = get_analysis(model)

# Keep the controls visible and ready for future wiring.
st.sidebar.caption(f"Selected scenario: {scenario}")
st.sidebar.caption(f"Mid threshold ε: {eps:.2f}")

# ===== Tabs =====
tabs = st.tabs(
    ["Overview", "Spectrum Analysis", "Decision Boundary", "Risk Report", "申诉解释 Demo"]
)

with tabs[0]:
    render_overview(model)

with tabs[1]:
    render_spectrum_tab(model, analysis)

with tabs[2]:
    render_boundary_tab(model, analysis)

with tabs[3]:
    render_risk_tab(model, analysis)

with tabs[4]:
    render_demo_tab(model, analysis)

# ===== Footer =====
st.markdown("---")
st.caption("Developed by Independent Researcher | Focus on Structured XAI")
