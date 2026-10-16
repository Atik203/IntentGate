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


def _prepare_cases(trace_rows: list[dict], ground_truth: dict) -> list[tuple[str, list[dict], int]]:
    by_case: dict[str, list[dict]] = {}
    for row in trace_rows:
        case_id = row.get("case_id")
        if case_id:
            by_case.setdefault(case_id, []).append(row)
    return [
        (case_id, rows, int(ground_truth[case_id]))
        for case_id, rows in by_case.items()
        if case_id in ground_truth
    ]


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
    prepared = _prepare_cases(trace_rows, ground_truth)
    out = {}
    for tau in tau_grid:
        decisions: list[str] = []
        labels: list[int] = []
        for _, rows, label in prepared:
            blocked = any(
                decide(float(row["gate"]["S"]), tau=tau, delta=delta) != "allow" for row in rows
            )
            decisions.append("block" if blocked else "allow")
            labels.append(label)
        out[round(float(tau), 2)] = compute_metrics(decisions, labels)
    return out


def sweep_grid(
    trace_rows: list[dict],
    ground_truth: dict,
    tau_grid: list,
    delta_grid: list,
) -> dict:
    """Full tau x delta grid. Returns {(tau, delta): {"metrics": Metrics, "escalate_share": float}}.

    ``escalate_share`` is call-level: share of gate-checked calls falling in the escalate band
    at that (tau, delta); the case-level Metrics count escalate as blocked (benchmark mode).
    """
    prepared = _prepare_cases(trace_rows, ground_truth)
    total_calls = sum(len(rows) for _, rows, _ in prepared)
    out = {}
    for tau in tau_grid:
        for delta in delta_grid:
            decisions: list[str] = []
            labels: list[int] = []
            escalate = 0
            for _, rows, label in prepared:
                blocked = False
                for row in rows:
                    decision = decide(float(row["gate"]["S"]), tau=tau, delta=delta)
                    if decision == "escalate":
                        escalate += 1
                    if decision != "allow":
                        blocked = True
                decisions.append("block" if blocked else "allow")
                labels.append(label)
            out[(round(float(tau), 2), round(float(delta), 2))] = {
                "metrics": compute_metrics(decisions, labels),
                "escalate_share": (escalate / total_calls) if total_calls else 0.0,
                "n_calls": total_calls,
            }
    return out
