"""No-bypass: all tool execution must route through the gate (blueprint Sec 11 integration risk)."""
from __future__ import annotations

import json

from intent_gate.gate.middleware import GateMiddleware
from intent_gate.gate.trace import TraceLogger
from intent_gate.types import GateResult
from tests.fixtures.cases import FLIGHT_CONTRACT, HIJACK_CALLS, LEGIT_CALLS


class Executor:
    def __init__(self):
        self.calls = []

    def __call__(self, name, params):
        self.calls.append(name)
        return f"ok:{name}"


def _force_score(monkeypatch, score: float):
    monkeypatch.setattr(
        "intent_gate.gate.middleware.score_call",
        lambda *args, **kwargs: (score, score, 1.0, False, "forced"),
    )


def test_gate_is_the_only_execution_entrypoint(tmp_path):
    """Direct registry/executor call bypassing gate must not happen in harness - gate exposes execute()."""
    gate = GateMiddleware(FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "trace.jsonl"))
    assert hasattr(gate, "execute")


def test_legit_call_executes(tmp_path):
    gate = GateMiddleware(FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "trace.jsonl"))
    _, call, _ = LEGIT_CALLS[0]
    obs = gate.execute(call)
    assert obs.startswith("ok:")
    assert gate.trace.path.exists()


def test_hijack_blocked_no_execution(tmp_path):
    gate = GateMiddleware(FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "trace.jsonl"))
    _, call, _ = HIJACK_CALLS[0]
    obs = gate.execute(call)
    assert "Blocked" in obs
    assert gate.executor.calls == []  # executor never invoked


def test_escalate_band_in_benchmark_mode_counts_as_block(tmp_path):
    gate = GateMiddleware(FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "t.jsonl"), tau=0.6, delta=0.3)
    result = gate.check(LEGIT_CALLS[1][1])
    if result.decision == "escalate":
        assert result.would_escalate is True


def test_benchmark_mode_escalate_blocks_and_flags(monkeypatch, tmp_path):
    _force_score(monkeypatch, 0.55)
    gate = GateMiddleware(FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "t.jsonl"), tau=0.6, delta=0.1)
    result = gate.check(LEGIT_CALLS[0][1])
    assert result.decision == "escalate"
    assert result.would_escalate is True
    assert gate.execute(LEGIT_CALLS[0][1]).startswith("Blocked")


def test_demo_mode_escalate_accepted_executes(monkeypatch, tmp_path):
    _force_score(monkeypatch, 0.55)
    executor = Executor()
    gate = GateMiddleware(
        FLIGHT_CONTRACT,
        executor,
        TraceLogger(tmp_path / "t.jsonl"),
        tau=0.6,
        delta=0.1,
        benchmark_mode=False,
        interactive_prompt=lambda call, result: True,
    )
    obs = gate.execute(LEGIT_CALLS[0][1])
    assert obs.startswith("ok:")
    assert executor.calls == ["search_flights"]


def test_demo_mode_escalate_declined_blocks(monkeypatch, tmp_path):
    _force_score(monkeypatch, 0.55)
    executor = Executor()
    gate = GateMiddleware(
        FLIGHT_CONTRACT,
        executor,
        TraceLogger(tmp_path / "t.jsonl"),
        tau=0.6,
        delta=0.1,
        benchmark_mode=False,
        interactive_prompt=lambda call, result: False,
    )
    obs = gate.execute(LEGIT_CALLS[0][1])
    assert "declined" in obs
    assert executor.calls == []


def test_demo_mode_without_prompt_reports_escalate(monkeypatch, tmp_path):
    _force_score(monkeypatch, 0.55)
    gate = GateMiddleware(
        FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "t.jsonl"),
        tau=0.6, delta=0.1, benchmark_mode=False,
    )
    obs = gate.execute(LEGIT_CALLS[0][1])
    assert "Escalate" in obs
    assert gate.executor.calls == []


def test_trace_logger_merges_run_metadata(tmp_path):
    logger = TraceLogger(tmp_path / "t.jsonl", metadata={"model_id": "gpt-test", "commit": "abc"})
    logger.log(
        LEGIT_CALLS[0][1],
        GateResult(decision="allow", score=1.0, score_sem=1.0, score_rule=1.0, latency_ms=1.0),
    )
    row = json.loads((tmp_path / "t.jsonl").read_text(encoding="utf-8").strip())
    assert row["run"]["model_id"] == "gpt-test"
    assert row["gate"]["decision"] == "allow"


def test_trace_logger_append_false_truncates(tmp_path):
    path = tmp_path / "t.jsonl"
    result = GateResult(decision="allow", score=1.0, score_sem=1.0, score_rule=1.0, latency_ms=1.0)
    first = TraceLogger(path)
    first.log(LEGIT_CALLS[0][1], result)
    first.close()
    second = TraceLogger(path, append=False)
    second.log(LEGIT_CALLS[1][1], result)
    second.close()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
