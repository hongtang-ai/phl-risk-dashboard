"""Lightweight governance and audit logging utilities."""

from __future__ import annotations

import datetime
import hashlib


# === UPDATED ===
def _compute_input_hash(input_data: dict) -> str:
    payload = str(sorted(input_data.items())).encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def log_decision(session_state, input_data: dict, analysis_results: dict):
    input_hash = _compute_input_hash(input_data)
    seen_hashes = set(session_state.get("audit_input_hashes", []))
    if input_hash in seen_hashes:
        return None

    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_hash": input_hash,
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

    if "audit_input_hashes" not in session_state:
        session_state.audit_input_hashes = []
    session_state.audit_input_hashes.append(input_hash)
    if len(session_state.audit_input_hashes) > 100:
        session_state.audit_input_hashes = session_state.audit_input_hashes[-100:]

    return log_entry

