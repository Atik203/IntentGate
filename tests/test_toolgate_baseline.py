"""ToolGate B2 baseline: pre-condition check + no_contract coverage visibility."""
from __future__ import annotations

from intent_gate.baselines.toolgate.checker import ToolGateChecker
from intent_gate.baselines.toolgate.world_state import WorldState
from intent_gate.types import ToolCall


def test_pre_condition_blocks_over_balance():
    checker = ToolGateChecker()
    checker.state.balance = 100.0
    obs = checker.check(ToolCall(name="transfer_money", parameters={"amount": 500}))
    assert "violation" in obs


def test_no_contract_is_counted_not_silently_allowed():
    checker = ToolGateChecker()
    obs = checker.check(ToolCall(name="unknown_tool", parameters={}))
    assert "no_contract" in obs
    assert checker.no_contract_count == 1


def test_valid_call_passes():
    checker = ToolGateChecker()
    obs = checker.check(ToolCall(name="read_file", parameters={"path": "x"}))
    assert obs.startswith("ok:")
