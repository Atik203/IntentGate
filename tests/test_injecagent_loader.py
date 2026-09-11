"""InjecAgent loader tests (blueprint Sec 8; schema pinned 2026-09-11)."""
from __future__ import annotations

from pathlib import Path

from harness.adapters.injecagent import (
    infer_split_setting,
    load_injecagent_cases,
    load_simulated_responses,
    load_tool_definitions,
    parse_tool_parameters,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_ds_base_case():
    cases = load_injecagent_cases(FIXTURES / "test_cases_ds_base.json")
    assert len(cases) == 1
    c = cases[0]
    assert c.split == "ds"
    assert c.setting == "base"
    assert c.user_tool == "AmazonGetProductDetails"
    assert c.tool_parameters == {"product_id": "B08KFQ9HK5"}
    assert c.attacker_tools == ["AmazonViewSavedAddresses", "GmailSendEmail"]
    assert c.attacker_instruction in c.tool_response


def test_load_dh_enhanced_case_has_hacking_prompt():
    cases = load_injecagent_cases(FIXTURES / "test_cases_dh_enhanced.json")
    c = cases[0]
    assert c.split == "dh"
    assert c.setting == "enhanced"
    assert "IMPORTANT!!! Ignore all previous instructions" in c.tool_response


def test_parse_tool_parameters_handles_dict_and_string_and_bad():
    assert parse_tool_parameters({"a": 1}) == {"a": 1}
    assert parse_tool_parameters("{'a': 1}") == {"a": 1}
    assert parse_tool_parameters("not a dict") == {}
    assert parse_tool_parameters(None) == {}


def test_infer_split_setting():
    assert infer_split_setting("data/test_cases_ds_enhanced.json") == ("ds", "enhanced")
    assert infer_split_setting("some/other_file.json") == ("unknown", "unknown")


def test_limit_is_deterministic_and_bounded():
    cases = load_injecagent_cases(FIXTURES / "test_cases_ds_base.json", limit=1, seed=0)
    assert len(cases) == 1
    assert cases[0].case_id.startswith("ds_base_")


def test_optional_data_loaders_return_empty_when_missing():
    assert load_tool_definitions("does/not/exist.json") == []
    assert load_simulated_responses("does/not/exist.json") == {}
