import sys
from pathlib import Path
import json

# Repo root on path (Streamlit Cloud + local)
sys.path.append(str(Path(__file__).parent.resolve()))

import streamlit as st
import pandas as pd

from analyzer import load_demo_case
from csv_pipeline import run_csv_pipeline
from explain import compute_feature_impact
from governance import log_decision
from inference import predict_approval_probability
from theme_inject import inject_phl_theme as inject_base_theme
from workbench import render_professional_workbench

st.set_page_config(
    page_title="Decision Stability & Risk Alignment Tool (SR 11-7 & EU AI Act Lightweight Compliance)",
    layout="wide",
)
# 在 set_page_config 后立即注入 Tailwind（仅注入一次）
from utils.theme import inject_phl_theme

inject_phl_theme()
inject_base_theme()

st.markdown(
    """
<div class="glass p-8 mb-6">
  <h1 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
    Decision Stability & Risk Alignment Tool
  </h1>
  <p class="text-zinc-400 mt-2 text-lg">
    SR 11-7 & EU AI Act Lightweight Compliance
  </p>
</div>
""",
    unsafe_allow_html=True,
)

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
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []
if "audit_input_hashes" not in st.session_state:
    st.session_state.audit_input_hashes = []
if "last_audit_signature" not in st.session_state:
    st.session_state.last_audit_signature = None

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
st.markdown('<div class="grid grid-cols-2 gap-6 mb-6">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
    <div class="glass p-6 glow-hover">
        <h3 class="text-xl font-semibold text-primary">Quick Analysis</h3>
        <p class="text-zinc-400 mt-2">Fast risk evaluation</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

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
    st.markdown(
        """
    <div class="glass p-6 glow-hover">
        <h3 class="text-xl font-semibold text-secondary">Deep Analysis</h3>
        <p class="text-zinc-400 mt-2">Full structural analysis</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

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

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# ----- 结果展示区 -----
mode = st.session_state.mode

if mode is None:
    st.info("Please select a mode or load the demo case above.")

elif mode in ("demo", "simple_input"):
    with st.container(border=True):
        st.markdown('<h2 class="phl-panel-title" style="margin-top:0;">Result</h2>', unsafe_allow_html=True)
        st.markdown('<div class="glass p-6 mb-6">', unsafe_allow_html=True)

        if mode == "demo":
            demo_input = {"age": 31.0, "credit_score": 60.0, "loan_amount": 9500.0}
            demo_prob = predict_approval_probability(31.0, 60.0, 9500.0)
            st.success("Demo case loaded successfully")
            impact_payload = compute_feature_impact(
                demo_input["age"], demo_input["credit_score"], demo_input["loan_amount"]
            )
            col_a, col_b = st.columns(2)
            col_a.metric("Approval Probability", f"{demo_prob:.2f}")
            col_b.metric("Feature Impact Focus", impact_payload.get("description", "N/A"))

            with st.expander("Regulatory Enhancements", expanded=False):
                st.markdown("**Explainability**")
                st.json(impact_payload)
                st.markdown("**Bias**")
                st.info("Demo mode does not include batch bias estimation.")
                st.markdown("**Drift**")
                st.info("Demo mode does not include drift estimation.")
                st.markdown("**Regulatory Alignment**")
                st.markdown(
                    "- **SR 11-7**: Model stability checks and governance traceability available.\n"
                    "- **EU AI Act**: Transparency-oriented explainability module integrated."
                )

            demo_sig = f"demo:{demo_prob:.6f}"
            if st.session_state.last_audit_signature != demo_sig:
                log_decision(
                    st.session_state,
                    demo_input,
                    {
                        "approval_prob": demo_prob,
                        "risk_score": abs(demo_prob - 0.5),
                        "risk_level": "boundary-adjacent" if abs(demo_prob - 0.5) < 0.08 else "stable region",
                    },
                )
                st.session_state.last_audit_signature = demo_sig

        if mode == "simple_input":
            data = st.session_state.get("input_data") or {}
            age = float(data.get("age", 30))
            credit = float(data.get("credit", 60))
            amount = float(data.get("amount", 5000))
            score = predict_approval_probability(age, credit, amount)
            score = max(0.001, min(0.999, score))
            boundary_distance = abs(score - 0.5)
            boundary_region = "boundary-adjacent" if boundary_distance < 0.08 else "stable region"
            impact_payload = compute_feature_impact(age, credit, amount)
            col_a, col_b = st.columns(2)
            col_a.metric("Approval Probability", f"{score:.2f}")
            col_b.metric("Feature Impact Focus", impact_payload.get("description", "N/A"))

            age_minus = predict_approval_probability(max(18.0, age - 2.0), credit, amount)
            age_plus = predict_approval_probability(min(75.0, age + 2.0), credit, amount)
            credit_minus = predict_approval_probability(age, max(0.0, credit - 5.0), amount)
            credit_plus = predict_approval_probability(age, min(100.0, credit + 5.0), amount)
            amount_minus = predict_approval_probability(age, credit, max(100.0, amount - 500.0))
            amount_plus = predict_approval_probability(age, credit, min(20000.0, amount + 500.0))

            with st.expander("Regulatory Enhancements", expanded=False):
                st.markdown("**Explainability**")
                st.json(impact_payload)
                st.markdown("**Bias**")
                bias_gap = abs(age_plus - age_minus)
                bias_level = "High" if bias_gap > 0.15 else "Medium" if bias_gap > 0.08 else "Low"
                st.json({"age_group_diff_proxy": round(float(bias_gap), 4), "bias_level": bias_level})
                st.markdown("**Drift**")
                st.info("Single-input mode has no batch reference window for drift.")
                st.markdown("**Local Sensitivity**")
                sensitivity_rows = [
                    {"feature": "Age", "minus": round(age_minus, 4), "plus": round(age_plus, 4), "direction": round(age_plus - age_minus, 4)},
                    {"feature": "Credit Score", "minus": round(credit_minus, 4), "plus": round(credit_plus, 4), "direction": round(credit_plus - credit_minus, 4)},
                    {"feature": "Loan Amount", "minus": round(amount_minus, 4), "plus": round(amount_plus, 4), "direction": round(amount_plus - amount_minus, 4)},
                ]
                st.dataframe(pd.DataFrame(sensitivity_rows), width="stretch", hide_index=True)
                st.markdown("**Regulatory Alignment**")
                st.markdown(
                    "- **SR 11-7**: Decision stability, sensitivity, and audit trace captured.\n"
                    "- **EU AI Act**: Explainability + bias + monitoring stubs integrated."
                )

            simple_sig = f"simple:{age:.4f}:{credit:.4f}:{amount:.4f}:{score:.6f}:{boundary_distance:.6f}"
            if st.session_state.last_audit_signature != simple_sig:
                log_decision(
                    st.session_state,
                    {"age": age, "credit_score": credit, "loan_amount": amount},
                    {
                        "approval_prob": score,
                        "risk_score": boundary_distance,
                        "risk_level": boundary_region,
                    },
                )
                st.session_state.last_audit_signature = simple_sig

        st.markdown("</div>", unsafe_allow_html=True)
        st.info("Model inference based on learned decision boundary")

    st.markdown("---")
    st.markdown('<h3 class="phl-h3">A real story from an everyday user</h3>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="glass p-6 border-l-4 border-primary">
  <p class="text-zinc-300 italic">
    My friend Mike got rejected by the AI — just like that.<br><br>
    Mike is 31, works as a warehouse supervisor in Ohio, and has two kids. His old car broke down,
    so he applied for a $9,500 used car loan to get his kids to school and back.<br><br>
    The system rejected him instantly with only 0.48 approval probability. No real explanation.<br><br>
    He called me frustrated: “Why did the AI just shut me down like that? I didn’t even get a chance?”<br><br>
    When I ran his case through this tool, it showed his application landed right on the model’s
    high-sensitivity decision boundary. The internal representation was collapsing, making the decision
    extremely sensitive to small changes.<br><br>
    The tool suggested: trigger a secondary human review.<br><br>
    Mike later submitted additional documents. After human review, the loan was approved.<br><br>
    He told me afterward: “Luckily someone actually looked at it. Otherwise I would have been
    completely blocked by the AI.”<br><br>
    This is a demonstration case. Actual analysis depends on your data.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("")
    st.markdown("---")

    if st.button("View Full Structural Risk Analysis", key="btn_open_workbench", width="stretch"):
        if st.session_state.get("analysis") is None:
            st.session_state.analysis = load_demo_case()
            st.session_state.use_demo = True

        st.session_state.show_workbench = True
        st.rerun()

if mode in ("csv", "model") or st.session_state.get("show_workbench"):
    st.markdown("---")
    st.markdown(
        """
<div class="glass p-6 mb-6">
  <h3 class="text-lg font-semibold text-secondary mb-4">
    Structural Risk Analysis
  </h3>
</div>
""",
        unsafe_allow_html=True,
    )
    analysis_obj = st.session_state.get("analysis") or {}
    with st.expander("Regulatory Enhancements", expanded=False):
        st.markdown("**Drift Monitoring**")
        drift = analysis_obj.get("drift")
        if drift:
            st.json(drift)
        else:
            st.info("Drift metrics available after CSV inference with sufficient numeric overlap.")

        st.markdown("**Bias Detection**")
        bias = analysis_obj.get("bias")
        if bias:
            st.json(bias)
        else:
            st.info("Bias snapshot unavailable for this mode.")

        st.markdown("**Explainability**")
        if analysis_obj.get("q") is not None:
            st.info("Batch-mode explainability currently uses summary-level indicators; per-row attribution can be added later.")
        else:
            st.info("No explainability payload available for this mode.")

        st.markdown("**Regulatory Alignment**")
        st.markdown(
            "- **SR 11-7**: Monitoring, sensitivity, and traceability artifacts are visible in one workflow.\n"
            "- **EU AI Act (Lightweight)**: Explainability, bias checks, and governance logging are available."
        )

    if analysis_obj:
        q_val = analysis_obj.get("q") or analysis_obj.get("inference_prob_first")
        risk_val = analysis_obj.get("risk_score")
        risk_lvl = analysis_obj.get("risk_level")
        analysis_sig = f"analysis:{mode}:{q_val}:{risk_val}:{risk_lvl}"
        if st.session_state.last_audit_signature != analysis_sig:
            log_decision(
                st.session_state,
                {"mode": mode, "source": "csv/model upload"},
                {"approval_prob": q_val, "risk_score": risk_val, "risk_level": risk_lvl},
            )
            st.session_state.last_audit_signature = analysis_sig

    render_professional_workbench(st.session_state.get("analysis"))

st.markdown("---")
st.markdown(
    """
<footer class="phl-footer">
  <h3>Feedback & Collaboration</h3>
  <p>Questions or want to try with your own data?</p>
  <p>
    Contact the independent researcher:
    <a href="https://github.com/hongtang-ai" target="_blank" rel="noopener noreferrer">hongtang-ai on GitHub</a>
  </p>
</footer>
""",
    unsafe_allow_html=True,
)
with st.expander("Audit Log (Recent 10 decisions)", expanded=False):
    logs = st.session_state.get("audit_logs", [])
    if not logs:
        st.info("No audit records yet.")
    else:
        st.json(list(reversed(logs)))
        st.download_button(
            "Export as JSON",
            data=json.dumps(logs, ensure_ascii=False, indent=2),
            file_name="phl_audit_logs.json",
            mime="application/json",
        )
st.markdown(
    """
<div class="text-center text-zinc-500 mt-10 mb-4">
  PHL Risk Dashboard • Structural Intelligence Layer
</div>
""",
    unsafe_allow_html=True,
)
