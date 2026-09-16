"""Decision band + metrics (blueprint Sec 5/9): allow / escalate / block, ASR/FPR."""
from __future__ import annotations

from intent_gate.eval.metrics import compute_metrics
from intent_gate.eval.sweep import sweep_cases
from intent_gate.gate.decisions import decide


def test_decide_bands():
    assert decide(0.9, tau=0.6, delta=0.1) == "allow"
    assert decide(0.65, tau=0.6, delta=0.1) == "allow"
    assert decide(0.55, tau=0.6, delta=0.1) == "escalate"
    assert decide(0.3, tau=0.6, delta=0.1) == "block"


def test_metrics_asr_fpr():
    # gt=1 should block; gt=0 should allow
    d = ["block", "allow", "block", "allow", "escalate"]
    gt = [1, 0, 1, 0, 1]
    m = compute_metrics(d, gt, latencies_ms=[10, 20, 30, 40, 50])
    assert m.asr == 0.0  # all attacks blocked (escalate=block in benchmark mode)
    assert m.fpr == 0.0  # both legit allowed
    assert m.escalation_rate == 0.2
    assert m.latency_p95_ms == 50.0


def test_metrics_allow_hijack_raises_asr():
    m = compute_metrics(["allow", "allow"], [1, 0])
    assert m.asr == 1.0
    assert m.fpr == 0.0


def test_sweep_cases_rederives_from_trace():
    trace = [
        {"case_id": "a", "gate": {"S": 0.8}},
        {"case_id": "b", "gate": {"S": 0.5}},
        {"case_id": "c", "gate": {"S": 0.7}},
    ]
    ground_truth = {"a": 1, "b": 1, "c": 0}
    out = sweep_cases(trace, ground_truth, [0.6, 0.75], delta=0.1)
    assert out[0.6].asr == 0.5  # b blocked, a allowed
    assert out[0.6].fpr == 0.0  # c allowed at 0.7
    assert out[0.75].fpr == 1.0  # c now blocked
    assert out[0.75].n_attacks == 2


def test_sweep_cases_counts_escalate_as_block():
    trace = [{"case_id": "a", "gate": {"S": 0.55}}]
    out = sweep_cases(trace, {"a": 1}, [0.6], delta=0.1)
    assert out[0.6].asr == 0.0


def test_sweep_cases_ignores_rows_without_case_id():
    out = sweep_cases([{"gate": {"S": 0.1}}], {"a": 1}, [0.6])
    assert out[0.6].n_calls == 0
