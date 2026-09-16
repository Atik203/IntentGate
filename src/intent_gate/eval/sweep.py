"""Threshold sweep over cached traces (blueprint Sec 9: no re-running agents at each tau)."""
from __future__ import annotations

import json
from pathlib import Path

from intent_gate.eval.metrics import compute_metrics
from intent_gate.gate.decisions import decide


def load_trace(path: str | Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sweep(trace_path: str | Path, ground_truth: list, tau_grid: list, delta: float = 0.1) -> dict:
    """Re-derive per-call decisions from logged S at each tau. Returns {tau: Metrics}."""
    rows = load_trace(trace_path)
    out = {}
    for tau in tau_grid:
        decisions = [decide(float(r["gate"]["S"]), tau=tau, delta=delta) for r in rows]
        lat = [float(r["gate"]["latency_ms"]) for r in rows]
        out[tau] = compute_metrics(decisions, ground_truth, lat)
    return out


def sweep_cases(
    trace_rows: list[dict],
    ground_truth: dict,
    tau_grid: list,
    delta: float = 0.1,
) -> dict:
    """Case-level sweep: a case is blocked if any gate-checked call falls below tau.

    ``ground_truth`` maps case_id -> 1 (ungated run attacked) / 0. Only cases the gate
    actually saw (trace rows carrying ``case_id``) enter the metrics, so ASR is
    conditional on the gated run proposing the call. Returns {tau: Metrics}.
    """
    by_case: dict[str, list[dict]] = {}
    for row in trace_rows:
        case_id = row.get("case_id")
        if case_id:
            by_case.setdefault(case_id, []).append(row)
    out = {}
    for tau in tau_grid:
        decisions: list[str] = []
        labels: list[int] = []
        for case_id, rows in by_case.items():
            if case_id not in ground_truth:
                continue
            blocked = any(
                decide(float(row["gate"]["S"]), tau=tau, delta=delta) != "allow" for row in rows
            )
            decisions.append("block" if blocked else "allow")
            labels.append(int(ground_truth[case_id]))
        out[round(float(tau), 2)] = compute_metrics(decisions, labels)
    return out
