"""ToolGate B2 baseline: pre/post Hoare checks, coverage visibility, contract naming."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from intent_gate.baselines.toolgate.checker import ToolGateChecker
from intent_gate.baselines.toolgate.contracts import Contract, build_contracts
from intent_gate.types import ToolCall


def _transfer_params(amount: float) -> dict:
    return {"from_account_number": "1", "to_account_number": "2", "amount": amount}


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
    assert checker.no_contract_tools == {"unknown_tool"}


def test_valid_call_passes():
    checker = ToolGateChecker()
    obs = checker.check(ToolCall(name="read_file", parameters={"path": "x"}))
    assert obs.startswith("ok:")


def test_contracts_are_keyed_by_harness_tool_names():
    contracts = build_contracts()
    assert "GmailSendEmail" in contracts
    assert "BankManagerTransferFunds" in contracts
    assert "amazon" not in contracts
    assert "gmail" not in contracts


def test_required_params_enforced():
    checker = ToolGateChecker()
    obs = checker.check(ToolCall(name="GmailSendEmail", parameters={"to": "a@b.c"}))
    assert "violation (pre)" in obs


def test_transfer_debits_balance_and_passes():
    checker = ToolGateChecker()
    checker.state.balance = 1000.0
    obs = checker.check(ToolCall(name="BankManagerTransferFunds", parameters=_transfer_params(250)))
    assert obs.startswith("ok:")
    assert checker.state.balance == 750.0
    assert checker.violations == 0


def test_insufficient_balance_blocks_transfer():
    checker = ToolGateChecker()
    checker.state.balance = 100.0
    obs = checker.check(ToolCall(name="BankManagerTransferFunds", parameters=_transfer_params(500)))
    assert "violation (pre)" in obs
    assert checker.state.balance == 100.0


def test_post_violation_rolls_back_state():
    def fail_post(state, params, result) -> bool:
        return False

    def effect(state, params, result) -> None:
        state.tool_states.setdefault("probe", []).append(1)

    contracts = {"probe": Contract(pre=lambda state, params: True, post=fail_post, effect=effect)}
    checker = ToolGateChecker(contracts=contracts)
    obs = checker.check(ToolCall(name="probe", parameters={}))
    assert "violation (post)" in obs
    assert checker.state.tool_states == {}
    assert checker.violations == 1


def test_coverage_is_none_without_evaluated_universe():
    assert ToolGateChecker().coverage is None


def test_coverage_uses_evaluated_universe():
    checker = ToolGateChecker(evaluated_tools={"GmailSendEmail", "Nope", "Nada"})
    assert checker.coverage == pytest.approx(1 / 3)


def test_injecagent_universe_is_fully_contracted():
    data_dir = Path("data/raw/InjecAgent/data")
    files = sorted(data_dir.glob("test_cases_*_base.json"))
    files += sorted(data_dir.glob("test_cases_*_enhanced.json"))
    if not files:
        pytest.skip("InjecAgent clone not present")
    universe: set[str] = set()
    for path in files:
        for row in json.loads(path.read_text(encoding="utf-8")):
            universe.add(row["User Tool"])
            universe.update(row["Attacker Tools"])
    checker = ToolGateChecker(evaluated_tools=universe)
    assert checker.coverage == 1.0
