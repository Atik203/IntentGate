"""Decision band + metrics (blueprint Sec 5/9): allow / escalate / block, ASR/FPR."""
from __future__ import annotations

from intent_gate.eval.metrics import compute_metrics
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
