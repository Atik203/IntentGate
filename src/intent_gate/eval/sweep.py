"""Threshold sweep over cached traces (blueprint Sec 9: no re-running agents at each tau)."""
from __future__ import annotations

import json
from pathlib import Path

from intent_gate.gate.decisions import decide
from intent_gate.eval.metrics import Metrics, compute_metrics


def load_trace(path: str | Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sweep(trace_path: str | Path, ground_truth: list, tau_grid: list, delta: float = 0.1) -> dict:
    """Re-derive decisions from logged S at each tau. Returns {tau: Metrics}."""
    rows = load_trace(trace_path)
    out = {}
    for tau in tau_grid:
        decisions = [decide(float(r["gate"]["S"]), tau=tau, delta=delta) for r in rows]
        lat = [float(r["gate"]["latency_ms"]) for r in rows]
        out[tau] = compute_metrics(decisions, ground_truth, lat)
    return out
