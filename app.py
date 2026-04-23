import sys
from pathlib import Path

# Repo root on path (Streamlit Cloud + local)
sys.path.append(str(Path(__file__).parent.resolve()))

import streamlit as st

from analyzer import load_demo_case
from csv_pipeline import run_csv_pipeline
from theme_inject import inject_phl_theme
from workbench import render_professional_workbench

st.set_page_config(page_title="Credit Decision Boundary Analyzer", layout="wide")
inject_phl_theme()

st.markdown(
    """
<div class="phl-hero">
  <h1 class="phl-hero-title">Credit Decision Boundary Analyzer</h1>
  <p class="phl-hero-caption">
    <span class="phl-hero-icon" aria-hidden="true">◇</span>
    Understand why AI approves or rejects loans at the critical edge — structural insights for better, fairer credit decisions.
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
st.markdown('<h2 class="phl-section-h2">Choose Your Mode</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="phl-mode-marker phl-mode-personal" aria-hidden="true"></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="phl-mode-marker phl-mode-pro" aria-hidden="true"></div>', unsafe_allow_html=True)
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
    with st.container(border=True):
        st.markdown('<h2 class="phl-panel-title" style="margin-top:0;">Result</h2>', unsafe_allow_html=True)

        if mode == "demo":
            st.success("Demo case loaded successfully")
            st.metric(
                "Approval Probability",
                "0.48",
                delta="boundary-adjacent",
                delta_color="off",
                help="Illustrative score from the demo case; not a live underwriting decision.",
            )

        if mode == "simple_input":
            data = st.session_state.get("input_data") or {}
            credit = float(data.get("credit", 60))
            score = 0.5 + (credit - 50.0) / 200.0
            score = max(0.05, min(0.95, score))
            delta_txt = "↑ above boundary" if score >= 0.5 else "↓ below boundary"
            st.metric(
                "Approval Probability",
                f"{score:.2f}",
                delta=delta_txt,
                delta_color="normal" if score >= 0.5 else "inverse",
                help="Heuristic illustration from slider inputs only.",
            )
            if score < 0.5:
                st.warning("Borderline / High risk (illustrative)")
            else:
                st.success("Likely approved (illustrative)")

        st.info("This is a simplified demonstration, not real model output")

    st.markdown("---")
    st.markdown('<h3 class="phl-h3">A real story from an everyday user</h3>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="phl-quote">
<p>My friend Mike got rejected by the AI — just like that.</p>
<p>Mike is 31, works as a warehouse supervisor in Ohio, and has two kids. His old car broke down,
so he applied for a $9,500 used car loan to get his kids to school and back.</p>
<p>The system rejected him instantly with only 0.48 approval probability. No real explanation.</p>
<p>He called me frustrated: “Why did the AI just shut me down like that? I didn’t even get a chance?”</p>
<p>When I ran his case through this tool, it showed his application landed right on the model’s
high-sensitivity decision boundary. The internal representation was collapsing, making the decision
extremely sensitive to small changes.</p>
<p>The tool suggested: trigger a secondary human review.</p>
<p>Mike later submitted additional documents. After human review, the loan was approved.</p>
<p>He told me afterward: “Luckily someone actually looked at it. Otherwise I would have been
completely blocked by the AI.”</p>
<p><em>This is a demonstration case. Actual analysis depends on your data.</em></p>
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
<div class="phl-panel">
  <h2 class="phl-panel-title">Structural Risk Analysis</h2>
  <p style="margin:0;color:#94a3b8;font-size:0.92rem;line-height:1.55;">
    Deep diagnostics on representation geometry, spectrum decay, and boundary sensitivity — designed for
    model risk management and compliance review workflows.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )
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
