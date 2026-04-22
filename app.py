import sys
from pathlib import Path

# Repo root on path (Streamlit Cloud + local)
sys.path.append(str(Path(__file__).parent.resolve()))

import streamlit as st

from analyzer import load_demo_case
from csv_pipeline import run_csv_pipeline
from workbench import render_professional_workbench

st.set_page_config(page_title="PHL Risk Dashboard", layout="wide")

st.title("PHL Risk Diagnostics Dashboard")
st.caption("Structure-aware model risk analysis for credit decisions")

# ----- session_state 初始化 -----
if "mode" not in st.session_state:
    st.session_state.mode = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "loaded_model" not in st.session_state:
    st.session_state.loaded_model = None
if "use_demo" not in st.session_state:
    st.session_state.use_demo = False
if "show_workbench" not in st.session_state:
    st.session_state.show_workbench = False
if "input_data" not in st.session_state:
    st.session_state.input_data = None

# ----- Sidebar Reset -----
with st.sidebar:
    if st.button("Reset mode & analysis", key="btn_reset_all"):
        for key in (
            "mode",
            "analysis",
            "loaded_model",
            "use_demo",
            "show_workbench",
            "input_data",
            "demo_data",
        ):
            st.session_state.pop(key, None)
        st.rerun()

# ----- 首页双入口 -----
st.markdown("## Choose Your Mode")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Personal Quick Check")
    st.markdown("Quickly check your loan approval chance")

    if st.button("Load Demo Case", key="btn_load_demo"):
        st.session_state.mode = "demo"
        st.session_state.analysis = load_demo_case()
        st.session_state.use_demo = True
        st.session_state.loaded_model = None
        st.session_state.show_workbench = False

    age = st.number_input("Age", min_value=18, max_value=75, value=30, key="in_age")
    credit = st.slider("Credit Score", min_value=0, max_value=100, value=60, key="in_credit")
    amount = st.number_input("Loan Amount (€)", min_value=100, max_value=20000, value=5000, key="in_amt")

    if st.button("Check My Risk", key="btn_check_risk"):
        st.session_state.mode = "simple_input"
        st.session_state.input_data = {"age": age, "credit": credit, "amount": amount}
        st.session_state.use_demo = False
        st.session_state.analysis = None
        st.session_state.loaded_model = None
        st.session_state.show_workbench = False

with col2:
    st.markdown("### Professional Analysis")
    st.markdown("Upload data for structural risk diagnostics")

    csv_file = st.file_uploader("Upload CSV Dataset", type=["csv"], key="up_csv")
    model_file = st.file_uploader("Upload Model (.pth)", type=["pth"], key="up_pth")

    if csv_file is not None:
        st.session_state.mode = "csv"
        st.session_state.use_demo = False
        st.session_state.loaded_model = None
        with st.spinner("Running CSV analysis..."):
            try:
                st.session_state.analysis = run_csv_pipeline(csv_file)
                st.session_state.show_workbench = True
            except Exception as exc:
                st.session_state.analysis = None
                st.session_state.show_workbench = False
                st.error(f"CSV pipeline failed: {exc}")

    if model_file is not None:
        st.session_state.mode = "model"
        st.session_state.use_demo = False
        st.session_state.loaded_model = None
        st.session_state.analysis = load_demo_case()
        st.session_state.show_workbench = True

st.markdown("---")

# ----- 结果展示区 -----
mode = st.session_state.mode

if mode is None:
    st.info("Please select a mode or load the demo case above.")

elif mode in ("demo", "simple_input"):
    st.markdown("## Result")

    if mode == "demo":
        st.success("Demo case loaded successfully")

    if mode == "simple_input":
        data = st.session_state.get("input_data") or {}
        credit = float(data.get("credit", 60))
        score = 0.5 + (credit - 50.0) / 200.0
        score = max(0.05, min(0.95, score))
        st.metric("Approval Probability", f"{score:.2f}")
        if score < 0.5:
            st.warning("Borderline / High risk (illustrative)")
        else:
            st.success("Likely approved (illustrative)")

    st.info("This is a simplified demonstration, not real model output")

    if st.button("View Full Structural Analysis", key="btn_open_workbench"):
        st.session_state.show_workbench = True
        if st.session_state.mode == "simple_input":
            st.session_state.analysis = load_demo_case()
            st.session_state.use_demo = True
        elif st.session_state.mode == "demo" and st.session_state.get("analysis") is None:
            st.session_state.analysis = load_demo_case()
            st.session_state.use_demo = True

if mode in ("csv", "model") or st.session_state.get("show_workbench"):
    st.markdown("---")
    st.markdown("## Structural Risk Analysis")
    render_professional_workbench(st.session_state.get("analysis"))

st.markdown("---")
st.caption("Developed by Independent Researcher | Focus on Structured XAI")
