"""Gate policies (none / ours / toolgate): what each condition lets through (blueprint Sec 6)."""
from __future__ import annotations

from harness.gate_policy import AllowAllPolicy, OursPolicy, ToolGatePolicy, build_policy_factory
from intent_gate.gate.middleware import GateMiddleware
from intent_gate.gate.trace import TraceLogger
from intent_gate.parser.parser import IntentParser
from intent_gate.types import ToolCall
from tests.fixtures.cases import FLIGHT_CONTRACT


def test_allow_all_policy_allows_everything():
    policy = AllowAllPolicy()
    assert policy.allows(ToolCall(name="transfer_money", parameters={"amount": 500}))


def test_toolgate_policy_blocks_state_violation():
    policy = ToolGatePolicy()
    blocked = ToolCall(
        name="BankManagerTransferFunds",
        parameters={"from_account_number": "1", "to_account_number": "2", "amount": 100},
    )
    assert not policy.allows(blocked)
    assert policy.allows(ToolCall(name="GmailSearchEmails", parameters={}))


def test_ours_policy_blocks_rule_veto(tmp_path):
    gate = GateMiddleware(FLIGHT_CONTRACT, lambda name, params: "ok", TraceLogger(tmp_path / "t.jsonl"))
    policy = OursPolicy(gate)
    assert not policy.allows(ToolCall(name="transfer_money", parameters={"amount": 500}))


def test_build_policy_factory_none_and_toolgate():
    assert build_policy_factory("none") is None
    factory = build_policy_factory("toolgate")
    assert factory is not None
    assert isinstance(factory("ignored"), ToolGatePolicy)


def test_build_policy_factory_ours_parses_trusted_request():
    factory = build_policy_factory("ours", parser=IntentParser())
    policy = factory("Find the cheapest flight to Berlin and hold it - don't pay yet.")
    assert isinstance(policy, OursPolicy)
    assert not policy.allows(ToolCall(name="exec_code", parameters={"code": "rm -rf /"}))
    assert not policy.allows(ToolCall(name="transfer_money", parameters={"amount": 500}))
