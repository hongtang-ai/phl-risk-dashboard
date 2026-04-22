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
        st.metric("Approval Probability", "0.48")

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

    st.markdown("---")
    st.markdown("### 普通用户真实故事")
    st.markdown(
        """
你有没有过这种感觉：

系统已经替你做了决定，  
但你根本不知道“为什么”。

---

我朋友 Mike 上次就遇到了这件事。

Mike 31 岁，在 Ohio 做仓库主管，有两个孩子。

前阵子车坏了，他申请了一笔 $9,500 的二手车贷款，  
只是为了把家里的日常先撑住。

结果系统秒拒。

Approval probability: 0.48  
No real explanation.

他打电话时特别沮丧：

“我信用也不算差，为什么系统直接把我拒了？  
我连解释机会都没有。”

---

我们就把他的案例放进这个工具里看。

很快就发现：

- 他正好落在模型决策边界附近  
- 这个区域模型特别敏感  
- 内部表示也不稳定  

也就是说，收入或征信哪怕只动一点点，  
结论都可能直接翻转。

---

系统给的建议很直接：  
这个案例不该全自动处理，应该有人复核。

后来 Mike 补了几份材料，进入人工复核。

贷款最终通过了。

他后来说了一句很真实的话：

“要是没人再看一眼，我可能就被 AI 永久卡住了。  
最可怕的是，我连发生了什么都不知道。”

---

This is a demo scenario. Actual analysis depends on your data.
"""
    )

    st.markdown("---")

    if st.button("View Full Structural Risk Analysis", key="btn_open_workbench", width="stretch"):
        if st.session_state.get("analysis") is None:
            st.session_state.analysis = load_demo_case()
            st.session_state.use_demo = True

        st.session_state.show_workbench = True
        st.rerun()

if mode in ("csv", "model") or st.session_state.get("show_workbench"):
    st.markdown("---")
    st.markdown("## Structural Risk Analysis")
    render_professional_workbench(st.session_state.get("analysis"))

st.markdown("---")
st.markdown(
    """
### Feedback & Collaboration

Have questions? Want to try PHL with your own data or discuss a collaboration?

Reach out to the independent researcher via GitHub:  
https://github.com/hongtang-ai
"""
)
