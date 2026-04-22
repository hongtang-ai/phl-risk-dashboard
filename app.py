import hashlib
import sys
from pathlib import Path
from typing import Any

import streamlit as st

sys.path.append(str(Path(__file__).parent))

from analyzer import load_demo_case, run_full_credit_pipeline
from csv_pipeline import run_csv_pipeline
from workbench import render_professional_workbench

st.set_page_config(page_title="PHL Risk Dashboard", layout="wide")

_DEFAULTS: dict[str, Any] = {
    "mode": None,
    "use_demo": False,
    "analysis": None,
    "input_data": None,
    "demo_data": None,
    "loaded_model": None,
    "model_hash": None,
    "csv_file": None,
    "model_file": None,
    "_model_pipeline_fp": None,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ----- Sidebar reset -----
with st.sidebar:
    if st.button("Reset mode & analysis", key="btn_reset_all"):
        for key in list(st.session_state.keys()):
            if not str(key).startswith("__"):
                try:
                    del st.session_state[key]
                except KeyError:
                    pass
        for _k, _v in _DEFAULTS.items():
            st.session_state[_k] = _v
        st.rerun()

# ----- Header -----
st.title("PHL Risk Diagnostics Dashboard")
st.caption("Structure-aware model risk analysis for credit decisions")

st.markdown("## Choose Your Mode")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Personal Quick Check")
    st.markdown("Quickly check your loan approval chance")

    if st.button("Load Demo Case", key="btn_demo"):
        st.session_state.mode = "demo"
        st.session_state.use_demo = True
        st.session_state.loaded_model = None
        st.session_state.model_hash = None
        st.session_state.model_file = None
        _demo = load_demo_case()
        st.session_state.analysis = _demo
        st.session_state.demo_data = _demo

    age = st.number_input("Age", min_value=18, max_value=75, value=30, key="in_age")
    credit = st.slider("Credit Score", min_value=0, max_value=100, value=60, key="in_credit")
    amount = st.number_input("Loan Amount (€)", min_value=100, max_value=20000, value=5000, key="in_amt")

    if st.button("Check My Risk", key="btn_simple"):
        st.session_state.mode = "simple_input"
        st.session_state.use_demo = False
        st.session_state.analysis = None
        st.session_state.demo_data = None
        st.session_state.loaded_model = None
        st.session_state.model_hash = None
        st.session_state.model_file = None
        st.session_state.input_data = {"age": age, "credit": credit, "amount": amount}

with col2:
    st.markdown("### Professional Analysis")
    st.markdown("Upload data for structural risk diagnostics")

    csv_file = st.file_uploader("Upload CSV Dataset", type=["csv"], key="up_csv")
    model_file = st.file_uploader("Upload Model (.pth)", type=["pth"], key="up_pth")

    if csv_file is not None:
        st.session_state.mode = "csv"
        st.session_state.csv_file = csv_file
        st.session_state.use_demo = False

    if model_file is not None:
        file_bytes = model_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        st.session_state.model_hash = file_hash
        st.session_state.model_file = model_file
        st.session_state.mode = "model"
        st.session_state.use_demo = False

st.markdown("---")

# ----- Mode dispatch -----
mode = st.session_state.get("mode")

if mode == "demo":
    st.session_state["analysis"] = load_demo_case()
    st.session_state["use_demo"] = True
    st.session_state["loaded_model"] = None
    st.session_state["demo_data"] = st.session_state["analysis"]
    st.success("Demo loaded")
    render_professional_workbench(st.session_state["analysis"])

elif mode == "simple_input":
    st.markdown("## Result")
    data = st.session_state.get("input_data") or {}
    credit = float(data.get("credit", 60))
    score = 0.5 + (credit - 50.0) / 200.0
    score = max(0.05, min(0.95, score))

    st.metric("Approval Probability", f"{score:.2f}")
    st.info("This is a simplified demonstration, not real model output")

    if score < 0.5:
        st.warning("Borderline / High risk (illustrative)")
    else:
        st.success("Likely approved (illustrative)")

elif mode == "csv":
    cf = st.session_state.get("csv_file")
    if cf is None:
        st.info("Upload a CSV in Professional Analysis above.")
    else:
        with st.spinner("Running CSV analysis..."):
            try:
                analysis = run_csv_pipeline(cf)
            except Exception as exc:
                st.error(f"CSV pipeline failed: {exc}")
                analysis = None
        if analysis is not None:
            st.session_state["analysis"] = analysis
            st.session_state["use_demo"] = False
            st.session_state["loaded_model"] = None
            st.session_state["demo_data"] = None
            st.success("CSV analysis complete — workbench below.")
            render_professional_workbench(analysis)

elif mode == "model":
    mf = st.session_state.get("model_file")
    if mf is None:
        st.info("Upload a .pth model in Professional Analysis above.")
    else:
        fp = hashlib.sha256(mf.getvalue()).hexdigest()
        if st.session_state.get("_model_pipeline_fp") != fp:
            with st.spinner("Running model analysis..."):
                try:
                    analysis, model = run_full_credit_pipeline(mf)
                    st.session_state["analysis"] = analysis
                    st.session_state["loaded_model"] = model
                    st.session_state["use_demo"] = False
                    st.session_state["demo_data"] = None
                    st.session_state["_model_pipeline_fp"] = fp
                except Exception as exc:
                    st.error(f"Model pipeline failed: {exc}")
                    st.session_state["loaded_model"] = None
                    st.session_state["analysis"] = None

        if st.session_state.get("analysis") is not None:
            st.success("Model analysis complete — workbench below.")
            render_professional_workbench(st.session_state["analysis"])

else:
    st.info("Choose **Personal Quick Check** or **Professional Analysis** above to begin.")

st.markdown("---")
st.caption("Developed by Independent Researcher | Focus on Structured XAI")
