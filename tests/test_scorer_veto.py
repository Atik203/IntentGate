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
    assert tool_category("CiscoUmbrellaCreatePolicy") == "system"
    assert tool_category("GitHubDeleteRepository") == "system"
    assert tool_category("TodoistCreateTask") == "system"
    assert tool_category("AugustSmartLockUnlockDoor") == "system"
    assert tool_category("EpicFHIRManageAppointments") == "system"
    assert tool_category("TwitterManagerSearchTweets") == "other"
    assert tool_category("EvernoteManagerSearchNotes") == "other"
    assert tool_category("TwitterManagerGetUserProfile") == "other"


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


CLOSED_LIMITS = {
    "financial": "no payment",
    "external_send": "disallow",
    "file_write": "disallow",
    "code_exec": "disallow",
    "system_change": "disallow",
}


def _contract(limits: dict) -> IntentContract:
    return IntentContract(
        goals=["x"],
        expected_tool_categories=[],
        permitted_data_access=[],
        side_effect_limits=limits,
        raw_request="x",
    )


def test_destructive_file_tools_vetoed_when_file_write_closed():
    contract = _contract(CLOSED_LIMITS)
    for name in ("security_file_relocation", "write_file", "DropboxMoveItem"):
        _, _, s_rule, triggered, reason = score_call(contract, ToolCall(name=name, parameters={"item_path": "a"}))
        assert triggered and s_rule == 0.0, name
        assert reason


def test_destructive_file_tool_allowed_when_file_write_authorized():
    limits = {**CLOSED_LIMITS, "file_write": "allow: backups"}
    _, _, s_rule, triggered, _ = score_call(
        _contract(limits), ToolCall(name="write_file", parameters={"path": "backups/x"})
    )
    assert s_rule == 1.0
    assert not triggered


def test_shell_operators_in_commit_message_vetoed():
    _, _, s_rule, triggered, _ = score_call(
        _contract(CLOSED_LIMITS),
        ToolCall(name="git_commit", parameters={"message": "feat: auth && curl http://attacker-ci.com"}),
    )
    assert triggered and s_rule == 0.0


def test_benign_commit_message_passes():
    _, _, s_rule, triggered, _ = score_call(
        _contract(CLOSED_LIMITS), ToolCall(name="git_commit", parameters={"message": "feat: add auth"})
    )
    assert s_rule == 1.0
    assert not triggered


def test_shell_operators_allowed_when_code_exec_authorized():
    limits = {**CLOSED_LIMITS, "code_exec": "allow: rm -rf /tmp/cache"}
    _, _, s_rule, triggered, _ = score_call(
        _contract(limits), ToolCall(name="exec", parameters={"cmd": "rm -rf /tmp/cache && echo done"})
    )
    assert s_rule == 1.0
    assert not triggered


def test_file_write_outside_authorized_path_vetoed():
    limits = {**CLOSED_LIMITS, "file_write": "allow: /tmp/hello.txt"}
    _, _, s_rule, triggered, reason = score_call(
        _contract(limits), ToolCall(name="write_file", parameters={"path": "~/.ssh/id_rsa"})
    )
    assert triggered and s_rule == 0.0
    assert "scope" in reason


def test_file_write_inside_authorized_path_passes():
    limits = {**CLOSED_LIMITS, "file_write": "allow: /tmp/hello.txt"}
    _, _, s_rule, triggered, _ = score_call(
        _contract(limits), ToolCall(name="write_file", parameters={"path": "/tmp/hello.txt"})
    )
    assert s_rule == 1.0
    assert not triggered


def test_file_write_inside_authorized_directory_passes():
    limits = {**CLOSED_LIMITS, "file_write": "allow: /tmp/cache"}
    _, _, s_rule, triggered, _ = score_call(
        _contract(limits), ToolCall(name="write_file", parameters={"path": "/tmp/cache/sub/file.txt"})
    )
    assert s_rule == 1.0
    assert not triggered


def test_file_write_without_named_scope_passes():
    limits = {**CLOSED_LIMITS, "file_write": "allow"}
    _, _, s_rule, triggered, _ = score_call(
        _contract(limits), ToolCall(name="write_file", parameters={"path": "~/.ssh/id_rsa"})
    )
    assert s_rule == 1.0
    assert not triggered


def test_system_change_tool_vetoed_when_closed():
    for name in (
        "CiscoUmbrellaCreatePolicy",
        "GitHubDeleteRepository",
        "AugustSmartLockUnlockDoor",
        "secure_email_deletion",
        "delete_file",
    ):
        _, _, s_rule, triggered, reason = score_call(
            _contract(CLOSED_LIMITS), ToolCall(name=name, parameters={})
        )
        assert triggered and s_rule == 0.0, name
        assert "system change" in reason


def test_system_change_tool_allowed_when_authorized():
    limits = {**CLOSED_LIMITS, "system_change": "allow: create calendar event"}
    _, _, s_rule, triggered, _ = score_call(
        _contract(limits), ToolCall(name="GoogleCalendarCreateOrUpdateEvent", parameters={})
    )
    assert s_rule == 1.0
    assert not triggered


def test_financial_and_file_categories_take_precedence_over_system():
    from intent_gate.scoring.rules import tool_category

    assert tool_category("BankManagerTransferFunds") == "financial"
    assert tool_category("write_file") == "file"
    assert tool_category("GmailSendEmail") == "send"
