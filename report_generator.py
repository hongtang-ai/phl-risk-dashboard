from __future__ import annotations

"""Credit markdown report generator."""

from pathlib import Path


def generate_credit_report(stats: dict, output_path: str = "results/credit_report.md") -> None:
    """输出申诉友好的贷款拒绝解释报告。"""
    report = f"""
# Loan Rejection Explanation (PHL)

## Summary
- Volatility (σ): {stats.get('sigma', float('nan')):.4f}
- Mid-density: {stats.get('mid', float('nan')):.4f}
- Effective Rank: {stats.get('effective_rank', float('nan')):.2f}
- SSI (Concentration): {stats.get('ssi', float('nan')):.4f}
- Risk Score: {stats.get('risk_score', float('nan')):.4f}
- Reject Sample Count: {stats.get('reject_count', 0)}

## Interpretation

该申请被拒绝的主要结构原因是：

- 模型内部表示出现维度塌缩（rank下降）
- 谱分布高度集中（SSI较高）
- 决策边界附近样本密度异常（mid偏离正常范围）

这意味着模型在该区域具有更高的不稳定性与敏感性。

## Recommendation

建议人工复核以下关键特征：
- 信用历史（credit history）
- 贷款金额（loan amount）
- 账户状态（account status）
"""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.strip() + "\n", encoding="utf-8")
