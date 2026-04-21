"""
统一数据 → 模型 → PHL 分析接口
"""

from __future__ import annotations

from data_loader_credit import load_german_credit_data
from credit_analysis import run_credit_rejection_analysis


def run_full_credit_pipeline(model):
    """
    返回 dashboard 所需的全部分析数据。
    """
    train_loader, test_loader = load_german_credit_data()
    _ = train_loader  # 预留：后续可加入训练集分布对照分析
    stats = run_credit_rejection_analysis(model, test_loader)
    return stats
