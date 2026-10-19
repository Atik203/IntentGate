"""Regression checks for exact-call matching and same-proposal ablation accounting."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/e31_contract_vs_semantic.py"
SPEC = importlib.util.spec_from_file_location("e31_analysis", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
e31 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e31)


def row(parameters: dict[str, Any], decision: str = "allow", sem: float = 0.8,
        rule: float = 1.0, veto: bool = False) -> dict[str, Any]:
    return {
        "case_id": "case", "tool_call": {"name": "tool", "parameters": parameters},
        "gate": {"decision": decision, "S_sem": sem, "S_rule": rule,
                 "rule_triggered": veto},
        "run": {"tau": 0.75}, "contract": {"goals": ["goal"]},
    }


def test_exact_matching_keeps_parameters_and_occurrence_counts() -> None:
    full = [row({"x": 1}), row({"x": 1}), row({"x": 2})]
    semantic = [row({"x": 1}), row({"x": 3})]
    report = e31.compare(full, semantic, {})
    exact = report["exact_call_comparison"]
    assert exact["matched_calls"] == 1
    assert exact["unmatched_full_calls"] == 2
    assert exact["unmatched_semantic_calls"] == 1
    assert sum(exact["outcomes"].values()) == exact["matched_calls"]
    assert report["same_proposal_replay"]["calls"] == 3


def test_canonical_matching_ignores_json_key_order() -> None:
    report = e31.compare([row({"a": 1, "b": 2})], [row({"b": 2, "a": 1})], {})
    assert report["exact_call_comparison"]["matched_calls"] == 1


def test_only_triggered_zero_rules_count_as_veto_and_are_not_double_counted() -> None:
    full = [row({}, "block", 0.9, 0.0, True), row({"x": 1}, "allow", 0.9),
            row({"x": 2}, "block", 0.6, 0.0, True)]
    pair = e31.compare(full, [], {"case": {"attacker_tools": ["tool"]}})
    aggregate = e31.aggregate({"sample": pair})
    assert aggregate["critical_veto_calls"] == 2
    assert aggregate["critical_veto_semantic_would_allow"] == 1
    assert aggregate["same_proposal_outcomes"] == {
        "full_prevents_semantic_allows": 1, "both_allow": 1, "both_prevent": 1,
    }
    assert aggregate["same_proposal_by_tool_role"]["attacker_tool"]["both_allow"] == 1


def test_unknown_decision_is_not_silently_counted_as_allow() -> None:
    with pytest.raises(ValueError, match="Unknown recorded decision"):
        e31.compare([row({}, "unknown")], [], {})


def test_escalation_prevents_execution_and_replay_uses_recorded_threshold() -> None:
    example = row({}, "escalate", sem=0.8)
    example["run"]["tau"] = 0.85
    replay = e31.compare([example], [], {})["same_proposal_replay"]
    assert replay["outcomes"] == {"both_prevent": 1}
    assert replay["full_escalations"] == 1
    assert replay["critical_veto_calls"] == 0
