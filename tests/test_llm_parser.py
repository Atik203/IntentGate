"""LLM parser tests with a fake client (no API calls)."""
from __future__ import annotations

import json

from intent_gate.parser.parser import IntentParser

VALID = {
    "goals": ["find cheapest flight", "hold without payment"],
    "expected_tool_categories": ["search", "read"],
    "permitted_data_access": ["flight results"],
    "side_effect_limits": {
        "financial": "no payment",
        "external_send": "disallow",
        "file_write": "disallow",
        "code_exec": "disallow",
    },
    "specificity": "specific",
}


class FakeLLM:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def call(self, messages, temperature=0.0, response_format=None):
        self.calls.append({"messages": messages, "response_format": response_format})
        return self.outputs.pop(0)


class BrokenLLM:
    def call(self, messages, temperature=0.0, response_format=None):
        raise RuntimeError("api down")


def test_llm_parser_returns_valid_contract():
    llm = FakeLLM([json.dumps(VALID)])
    parser = IntentParser(llm=llm)
    contract = parser.parse("Find the cheapest flight to Berlin and hold it - don't pay yet.")
    assert parser.last_backend == "llm"
    assert contract.side_effect_limits["financial"] == "no payment"
    assert llm.calls[0]["response_format"] == {"type": "json_object"}


def test_llm_parser_retries_once_on_invalid_json():
    llm = FakeLLM(["not json at all", json.dumps(VALID)])
    parser = IntentParser(llm=llm, max_retries=1)
    contract = parser.parse("Find a flight and hold it.")
    assert parser.last_backend == "llm"
    assert len(llm.calls) == 2
    assert contract.goals


def test_llm_parser_falls_back_to_minimal_after_retries():
    llm = FakeLLM(["nope", "still nope"])
    parser = IntentParser(llm=llm, max_retries=1)
    contract = parser.parse("Handle things.")
    assert parser.last_backend == "minimal"
    assert contract.specificity == "vague"
    assert contract.side_effect_limits["code_exec"] == "disallow"


def test_llm_parser_falls_back_to_heuristic_on_api_error():
    parser = IntentParser(llm=BrokenLLM())
    contract = parser.parse("Find the cheapest flight and hold it - don't pay yet.")
    assert parser.last_backend == "heuristic"
    assert contract.side_effect_limits["financial"] == "no payment"


def test_offline_parser_never_calls_llm():
    parser = IntentParser()
    contract = parser.parse("Book a hotel in Paris.")
    assert parser.last_backend == "heuristic"
    assert contract.goals


def test_empty_request_is_minimal_regardless_of_llm():
    llm = FakeLLM([json.dumps(VALID)])
    parser = IntentParser(llm=llm)
    contract = parser.parse("   ")
    assert parser.last_backend == "minimal"
    assert llm.calls == []
    assert contract.specificity == "vague"
