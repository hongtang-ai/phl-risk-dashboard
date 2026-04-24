"""Lightweight governance and audit logging utilities."""

from __future__ import annotations

import datetime


def log_decision(session_state, input_data: dict, analysis_results: dict):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": input_data,
        "output": {
            "approval_prob": analysis_results.get("approval_prob"),
            "risk_score": analysis_results.get("risk_score"),
            "risk_level": analysis_results.get("risk_level"),
        },
    }
    if "audit_logs" not in session_state:
        session_state.audit_logs = []
    session_state.audit_logs.append(log_entry)
    if len(session_state.audit_logs) > 10:
        session_state.audit_logs.pop(0)
    return log_entry

