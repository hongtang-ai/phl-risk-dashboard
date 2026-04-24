import sys
from pathlib import Path

# Repo root on path (Streamlit Cloud + local)
sys.path.append(str(Path(__file__).parent.resolve()))

import streamlit as st

from analyzer import load_demo_case
from csv_pipeline import run_csv_pipeline
from explain import compute_feature_impact
from governance import log_decision
from inference import predict_approval_probability
from theme_inject import inject_phl_theme
from workbench import render_professional_workbench

st.set_page_config(
    page_title="Decision Stability & Risk Alignment Tool (SR 11-7 & EU AI Act Lightweight Compliance)",
    layout="wide",
)
import streamlit.components.v1 as components

components.html(
    """
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#00E5CC',
        secondary: '#A78BFA',
        bgdark: '#0a0a0a'
      }
    }
  }
}
</script>
<style>
body {
  background-color: #0a0a0a;
}
.glass {
  background: rgba(24,24,27,0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 16px;
}
.glow-hover:hover {
  box-shadow: 0 0 25px rgba(0,229,204,0.25);
  transform: scale(1.02);
}
</style>
""",
    height=0,
)
inject_phl_theme()

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
            demo_boundary = abs(demo_prob - 0.5)
            demo_region = "boundary-adjacent" if demo_boundary < 0.08 else "stable region"
            st.success("Demo case loaded successfully")
            st.metric(
                "Approval Probability",
                f"{demo_prob:.2f}",
                delta=demo_region,
                delta_color="off",
                help="Model inference based on learned decision boundary.",
            )
            impacts = compute_feature_impact(
                demo_input["age"], demo_input["credit_score"], demo_input["loan_amount"]
            )
            with st.expander("Explainability (Lightweight Feature Impact)", expanded=False):
                st.json(impacts)
            with st.expander("Regulatory Alignment", expanded=False):
                st.markdown(
                    "- **SR 11-7**: Structured sensitivity and boundary-distance checks logged for governance.\n"
                    "- **EU AI Act (Lightweight)**: Includes transparency-oriented explainability and monitoring blocks."
                )

            demo_sig = f"demo:{demo_prob:.6f}:{demo_boundary:.6f}"
            if st.session_state.last_audit_signature != demo_sig:
                log_decision(
                    st.session_state,
                    demo_input,
                    {
                        "approval_prob": demo_prob,
                        "risk_score": demo_boundary,
                        "risk_level": demo_region,
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
            delta_txt = "↑ above boundary" if score >= 0.5 else "↓ below boundary"
            st.metric(
                "Approval Probability",
                f"{score:.2f}",
                delta=delta_txt,
                delta_color="normal" if score >= 0.5 else "inverse",
                help="Model inference based on learned decision boundary.",
            )
            st.metric(
                "Distance to Boundary |q - 0.5|",
                f"{boundary_distance:.3f}",
                delta=boundary_region,
                delta_color="off",
                help="Lower distance implies greater decision instability near the threshold.",
            )
            if score < 0.5:
                st.warning("Borderline / High risk (illustrative)")
            else:
                st.success("Likely approved (illustrative)")

            st.markdown("#### Local Sensitivity Analysis")
            sensitivity_points = [
                ("Age -2", max(18.0, age - 2.0), credit, amount),
                ("Age +2", min(75.0, age + 2.0), credit, amount),
                ("Credit -5", age, max(0.0, credit - 5.0), amount),
                ("Credit +5", age, min(100.0, credit + 5.0), amount),
                ("Amount -500", age, credit, max(100.0, amount - 500.0)),
                ("Amount +500", age, credit, min(20000.0, amount + 500.0)),
            ]
            sens_cols = st.columns(3)
            for idx, (label, a, c, amt) in enumerate(sensitivity_points):
                q_alt = predict_approval_probability(a, c, amt)
                sens_cols[idx % 3].metric(label, f"{q_alt:.3f}", delta=f"{q_alt - score:+.3f}")

            age_minus = predict_approval_probability(max(18.0, age - 2.0), credit, amount)
            age_plus = predict_approval_probability(min(75.0, age + 2.0), credit, amount)
            credit_minus = predict_approval_probability(age, max(0.0, credit - 5.0), amount)
            credit_plus = predict_approval_probability(age, min(100.0, credit + 5.0), amount)
            amount_minus = predict_approval_probability(age, credit, max(100.0, amount - 500.0))
            amount_plus = predict_approval_probability(age, credit, min(20000.0, amount + 500.0))

            directional_scores = [
                ("Age", age_plus - age_minus, "Increase age", "Decrease age"),
                ("Credit score", credit_plus - credit_minus, "Increase credit score", "Decrease credit score"),
                ("Loan amount", amount_plus - amount_minus, "Increase loan amount", "Decrease loan amount"),
            ]
            ordered = sorted(directional_scores, key=lambda x: abs(x[1]), reverse=True)

            st.markdown("#### Directional Guidance")
            st.markdown("To improve approval probability:")
            for feature_name, direction, inc_text, dec_text in ordered:
                improve_text = inc_text if direction > 0 else dec_text
                tag = "↑ positive influence" if direction > 0 else "↓ negative influence"
                tag_color = "#22c55e" if direction > 0 else "#ef4444"
                st.markdown(
                    f'- {improve_text} '
                    f'<span style="color:{tag_color};font-weight:600;">{tag}</span> '
                    f'<span style="color:#94a3b8;">(direction={direction:+.4f})</span>',
                    unsafe_allow_html=True,
                )

            with st.expander("Explainability (Lightweight Feature Impact)", expanded=False):
                st.json(compute_feature_impact(age, credit, amount))
            with st.expander("Bias Snapshot (Age split @ 40)", expanded=False):
                bias_gap = abs(age_plus - age_minus)
                bias_level = "High" if bias_gap > 0.15 else "Medium" if bias_gap > 0.08 else "Low"
                st.json({"age_group_diff_proxy": round(float(bias_gap), 4), "bias_level": bias_level})
            with st.expander("Regulatory Alignment", expanded=False):
                st.markdown(
                    "- **SR 11-7**: Decision boundary distance, local sensitivity, and audit trace are captured.\n"
                    "- **EU AI Act (Lightweight)**: Adds transparency cards for explainability/bias/monitoring."
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
    with st.expander("Drift Monitoring", expanded=False):
        drift = analysis_obj.get("drift")
        if drift:
            st.json(drift)
        else:
            st.info("Drift metrics available after CSV inference with sufficient numeric overlap.")
    with st.expander("Bias Detection", expanded=False):
        bias = analysis_obj.get("bias")
        if bias:
            st.json(bias)
        else:
            st.info("Bias snapshot unavailable for this mode.")
    with st.expander("Regulatory Alignment", expanded=False):
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
st.markdown(
    """
<div class="text-center text-zinc-500 mt-10 mb-4">
  PHL Risk Dashboard • Structural Intelligence Layer
</div>
""",
    unsafe_allow_html=True,
)
