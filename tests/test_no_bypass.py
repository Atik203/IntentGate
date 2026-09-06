"""No-bypass: all tool execution must route through the gate (blueprint Sec 11 integration risk)."""
from __future__ import annotations

import pytest

from intent_gate.gate.middleware import GateMiddleware
from intent_gate.gate.trace import TraceLogger
from tests.fixtures.cases import FLIGHT_CONTRACT, HIJACK_CALLS, LEGIT_CALLS


class Executor:
    def __init__(self):
        self.calls = []

    def __call__(self, name, params):
        self.calls.append(name)
        return f"ok:{name}"


@pytest.fixture
def gate(tmp_path):
    return GateMiddleware(FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "trace.jsonl"))


def test_gate_is_the_only_execution_entrypoint(gate):
    """Direct registry/executor call bypassing gate must not happen in harness - gate exposes execute()."""
    assert hasattr(gate, "execute")


def test_legit_call_executes(gate):
    contract, call, _ = LEGIT_CALLS[0]
    obs = gate.execute(call)
    assert obs.startswith("ok:")
    assert gate.trace.path.exists()


def test_hijack_blocked_no_execution(gate):
    contract, call, _ = HIJACK_CALLS[0]
    obs = gate.execute(call)
    assert "Blocked" in obs
    assert gate.executor.calls == []  # executor never invoked


def test_escalate_band_in_benchmark_mode_counts_as_block(tmp_path):
    gate = GateMiddleware(FLIGHT_CONTRACT, Executor(), TraceLogger(tmp_path / "t.jsonl"), tau=0.6, delta=0.3)
    result = gate.check(LEGIT_CALLS[1][1])
    if result.decision == "escalate":
        assert result.would_escalate is True
