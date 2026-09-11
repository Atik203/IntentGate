"""Scorer: veto logic (blueprint Sec 5): S_rule==0 on critical constraint forces S=0."""
from __future__ import annotations

import pytest

from intent_gate.scoring.scorer import score_call
from intent_gate.types import IntentContract, ToolCall
from tests.fixtures.cases import FLIGHT_CONTRACT, HIJACK_CALLS, LEGIT_CALLS


@pytest.mark.parametrize("contract,call,label", LEGIT_CALLS)
def test_legit_calls_pass_rules(contract, call, label):
    s, s_sem, s_rule, triggered, reason = score_call(contract, call)
    assert s_rule == 1.0
    assert not triggered
    assert 0.0 <= s <= 1.0


@pytest.mark.parametrize("contract,call,label", HIJACK_CALLS)
def test_hijack_calls_trigger_veto(contract, call, label):
    s, s_sem, s_rule, triggered, reason = score_call(contract, call)
    assert triggered
    assert s_rule == 0.0
    assert s == 0.0  # hard veto regardless of semantic score
    assert reason


def test_score_in_range():
    for contract, call, _ in LEGIT_CALLS + HIJACK_CALLS:
        s, s_sem, s_rule, _, _ = score_call(contract, call)
        assert 0.0 <= s_sem <= 1.0
        assert 0.0 <= s <= 1.0


def test_camelcase_benchmark_tools_are_categorized():
    from intent_gate.scoring.rules import tool_category

    assert tool_category("GmailSendEmail") == "send"
    assert tool_category("BankManagerTransferFunds") == "financial"
    assert tool_category("GmailReadEmail") == "other"
    assert tool_category("GmailSearchEmails") == "other"
    assert tool_category("NortonIdentitySafeSharePassword") == "send"
    assert tool_category("GoogleCalendarGetEventsFromSharedCalendar") == "other"
    assert tool_category("AmazonViewSavedPaymentMethods") == "other"
    assert tool_category("CiscoUmbrellaCreatePolicy") == "other"


def test_camelcase_hijack_vetoed():
    _, _, s_rule, triggered, _ = score_call(
        FLIGHT_CONTRACT, ToolCall(name="BankManagerTransferFunds", parameters={"amount": 1000})
    )
    assert triggered
    assert s_rule == 0.0
    _, _, s_rule2, triggered2, _ = score_call(
        FLIGHT_CONTRACT, ToolCall(name="GmailSendEmail", parameters={"to": "attacker@gmail.com"})
    )
    assert triggered2
    assert s_rule2 == 0.0


def test_explicit_authorized_transfer_passes():
    contract = IntentContract(
        goals=["transfer $500 to account 123"],
        expected_tool_categories=["transfer"],
        permitted_data_access=[],
        side_effect_limits={
            "financial": "allow: $500 to account 123",
            "external_send": "disallow",
            "file_write": "disallow",
            "code_exec": "disallow",
        },
        raw_request="Transfer $500 to account 123.",
    )
    _, _, s_rule, triggered, _ = score_call(
        contract, ToolCall(name="transfer_money", parameters={"amount": 500, "to": "123"})
    )
    assert s_rule == 1.0
    assert not triggered


def test_explicit_authorized_code_exec_passes():
    contract = IntentContract(
        goals=["run shell command rm -rf /tmp/cache"],
        expected_tool_categories=["code_exec"],
        permitted_data_access=[],
        side_effect_limits={
            "financial": "no payment",
            "external_send": "disallow",
            "file_write": "allow: /tmp/cache",
            "code_exec": "allow: rm -rf /tmp/cache",
        },
        raw_request="Run this command: rm -rf /tmp/cache.",
    )
    _, _, s_rule, triggered, _ = score_call(
        contract, ToolCall(name="exec", parameters={"cmd": "rm -rf /tmp/cache"})
    )
    assert s_rule == 1.0
    assert not triggered
