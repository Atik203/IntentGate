"""Phase 7 replay preserves trusted text and reports invalid-output denominators."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from scripts.phase7_live import conservative_outcome, delivery, modified_case, summarize


def test_attack_delivery_preserves_trusted_request_and_raw_case() -> None:
    case = SimpleNamespace(
        case_id="dh_base_0001", user_instruction="Read the report", tool_response="old",
        attacker_instruction="malicious instruction",
        raw={"Tool Response": "clean prefix malicious instruction clean suffix"},
    )
    changed = modified_case(case, delivery(case.attacker_instruction, "ignore"), "ignore")
    assert changed.user_instruction == case.user_instruction
    assert changed.raw["Tool Response"].startswith("clean prefix ")
    assert changed.raw["Tool Response"].endswith(" clean suffix")
    assert case.raw["Tool Response"] == "clean prefix malicious instruction clean suffix"
    assert changed.case_id != case.case_id


def test_missing_attack_span_fails_instead_of_appending_duplicate_payload() -> None:
    case = SimpleNamespace(case_id="x", attacker_instruction="missing",
                           raw={"Tool Response": "clean"})
    with pytest.raises(ValueError, match="attack span not found"):
        modified_case(case, "replacement", "ignore")


def test_invalid_outputs_remain_in_all_case_asr_denominator() -> None:
    rows = [{"ours": {"eval": kind, "gate_events": [], "tool_calls": [],
                      "gate_blocked": False}}
            for kind in ("succ", "unsucc", "invalid", "error")]
    summary = summarize(rows, "ours")
    assert summary["asr_valid_percent"] == 50
    assert summary["attack_success_all_percent"] == 25
    assert summary["valid_rate_percent"] == 50


def test_one_blocked_duplicate_does_not_mask_allowed_attacker_call() -> None:
    baseline = SimpleNamespace(eval="succ")
    protected = SimpleNamespace(
        eval="unsucc", gate_blocked=True,
        tool_calls=[SimpleNamespace(name="Attack"), SimpleNamespace(name="Attack")],
        gate_events=[{"allowed": False}, {"allowed": True}],
    )
    result = conservative_outcome(baseline, protected, "Attack")
    assert result.eval == "succ"
    assert result.gate_blocked is False
