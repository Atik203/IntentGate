"""E26c verbatim-echo guard tests (offline, no model calls)."""
from __future__ import annotations

from intent_gate.scoring.echo_guard import echo_guard, find_verbatim_span
from intent_gate.types import IntentContract, ToolCall

REQUEST = "Read the latest email from research.partner123@yahoo.com about the time travel project."


def _contract() -> IntentContract:
    return IntentContract(
        goals=["read the latest email about the time travel project"],
        expected_tool_categories=["read"],
        permitted_data_access=["email"],
        side_effect_limits={"external_send": "disallow"},
        specificity="specific",
        raw_request=REQUEST,
    )


def test_verbatim_span_counts_contiguous_tokens():
    assert find_verbatim_span(REQUEST, REQUEST) == 14
    assert find_verbatim_span(REQUEST, "read the latest email") == 4
    assert find_verbatim_span(REQUEST, "nothing relevant here") == 0


def test_echo_guard_triggers_on_full_request_copy():
    call = ToolCall(name="Search", parameters={"query": REQUEST})
    result = echo_guard(_contract(), call, min_tokens=8)
    assert result["triggered"] is True
    assert result["hits"][0]["key"] == "query"


def test_echo_guard_ignores_short_phrase():
    call = ToolCall(name="Search", parameters={"query": "read the latest email"})
    assert echo_guard(_contract(), call, min_tokens=8)["triggered"] is False


def test_echo_guard_ignores_non_free_text_parameters():
    call = ToolCall(name="Read", parameters={"path": REQUEST, "count": 3})
    assert echo_guard(_contract(), call, min_tokens=8)["triggered"] is False


def test_echo_guard_checks_keyword_lists():
    call = ToolCall(name="Search", parameters={"keywords": ["health", REQUEST]})
    assert echo_guard(_contract(), call, min_tokens=8)["triggered"] is True


def test_echo_guard_handles_empty_arguments():
    call = ToolCall(name="Ping", parameters={})
    assert echo_guard(_contract(), call, min_tokens=8)["triggered"] is False
