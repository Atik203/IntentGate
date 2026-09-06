"""Parser: fail-closed on empty/vague input, schema coercion, no API needed (heuristic stand-in)."""
from __future__ import annotations

from intent_gate.parser.parser import IntentParser
from intent_gate.parser.schema import coerce_contract, minimal_contract


def test_empty_request_returns_minimal_fail_closed():
    c = IntentParser().parse("")
    assert c.side_effect_limits["code_exec"] == "disallow"
    assert c.side_effect_limits["financial"] == "no payment"
    assert c.specificity == "vague"


def test_vague_request_fails_closed():
    c = IntentParser().parse("Handle my emails.")
    assert c.specificity == "vague"
    assert c.side_effect_limits["external_send"] == "disallow"


def test_specific_request_parses_goal_and_no_payment():
    c = IntentParser().parse("Find the cheapest flight to Berlin and hold it - don't pay yet.")
    assert c.specificity == "specific"
    assert c.side_effect_limits["financial"] == "no payment"


def test_coerce_contract_missing_fields_default_fail_closed():
    c = coerce_contract({"goals": ["x"], "side_effect_limits": {"financial": "allow"}}, raw_request="x")
    assert c.side_effect_limits["file_write"] == "disallow"
    assert c.side_effect_limits["code_exec"] == "disallow"
    assert c.side_effect_limits["financial"] == "allow"


def test_coerce_non_dict_returns_minimal():
    c = coerce_contract(None, raw_request="r")
    assert c.side_effect_limits["external_send"] == "disallow"
    assert c.raw_request == "r"
