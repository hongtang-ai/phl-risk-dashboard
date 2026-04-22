"""Unified professional workbench (5 tabs) — analysis-only Tab API."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.boundary_tab import render_boundary_tab
from ui.demo_tab import render_demo_tab
from ui.overview import render_overview
from ui.risk_tab import render_risk_tab
from ui.spectrum_tab import render_spectrum_tab


def render_professional_workbench(analysis: dict[str, Any] | None) -> None:
    if analysis is None:
        st.info("No analysis available yet. Please load demo or upload data.")
        return

    use_demo = st.session_state.get("use_demo", False)

    if use_demo:
        st.warning(
            "Demo Mode: Using pre-configured German Credit Rejection Case for illustration only."
        )

    if use_demo:
        st.markdown("### Case Background")
        st.info(
            "Demo Case: 张伟（31岁）申请 €5000 二手车贷款，信用分 60 分。"
            "模型输出概率 q = 0.48，处于决策边界附近，被自动拒绝。"
        )

    if use_demo:
        st.markdown("### Key Risk Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volatility (σ)", "6.23")
        col2.metric("Mid-density", "0.0075")
        col3.metric("Effective Rank", "3.12")
        col4, col5 = st.columns(2)
        col4.metric("SSI", "0.42")
        col5.metric("Risk Score", "0.135 (MEDIUM)")

    st.markdown("---")
    st.markdown("### 银行合规团队真实案例")
    st.markdown(
        """
如果你做过模型风险或合规，这个场景基本都会遇到。

---

Sarah 是一家银行的合规负责人。  
她说：“这种电话，我几乎每周都要接。”

上周，一位客户来投诉：

申请 $9,500 二手车贷款，系统自动拒绝。

客户在电话里很激动：  
“材料我都交了，为什么拒我？至少告诉我原因吧。”

---

这时压力就落在 Sarah 身上了。

按监管要求，  
她不能只说“模型就是这么判的”。

她必须给出可解释、可记录、可复核的说明。

---

She ran the case through PHL.

结果很清楚：

- 申请样本正好卡在决策边界  
- 模型在该区域敏感度偏高  
- 内部表示压缩（effective rank 低）  
- 谱特征集中度明显偏高  

---

工具给她的，不只是一个分数：

- A clear risk signal: MEDIUM risk
- A concrete action: trigger human review
- A structured explanation she could document

---

这直接帮她完成两件事：

1. 给客户一个说得清的回复  
2. 给审计和监管留下一份结构化记录  

---

后来 Sarah 说：

“真正有用的，不只是知道哪个特征重要。  
而是知道模型什么时候开始不稳定。  
这才是合规团队能落地用起来的关键。”

---

This is a demo scenario. Actual analysis depends on your data.
"""
    )

    st.markdown("---")

    tabs = st.tabs(
        [
            "Overview",
            "Spectrum Analysis",
            "Decision Boundary",
            "Risk Report",
            "Loan Explanation",
        ]
    )

    with tabs[0]:
        render_overview(analysis)
    with tabs[1]:
        render_spectrum_tab(analysis)
    with tabs[2]:
        render_boundary_tab(analysis)
    with tabs[3]:
        render_risk_tab(analysis)
    with tabs[4]:
        render_demo_tab(analysis)
