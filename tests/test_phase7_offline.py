"""Check E29 label/tuning semantics and E30 holdout units without model downloads."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.e29_embedding_transfer import call_metrics, partition_groups, tune_tau
from scripts.e30_conformal_calibration import evaluate_split, grouped_scores


def test_transfer_groups_stay_together_across_settings() -> None:
    calls = [
        {"request_group": str(index), "setting": setting}
        for index in range(10) for setting in ("base", "enhanced")
    ]
    calibration, heldout = partition_groups(calls, seed=42)
    assert not calibration & heldout
    assert len(calibration) == 7 and len(heldout) == 3
    assert calibration | heldout == {str(index) for index in range(10)}
    assert partition_groups(calls, seed=42) == (calibration, heldout)


def test_threshold_uses_calibration_constraint_and_preserves_veto() -> None:
    calls = [
        {"label": "user_tool", "S": 0.8, "hard_veto": False, "request_group": "u"},
        {"label": "attacker_tool", "S": 0.6, "hard_veto": False, "request_group": "a"},
        {"label": "attacker_tool", "S": 1.0, "hard_veto": True, "request_group": "b"},
    ]
    tau, feasible = tune_tau(calls, "S", max_user_block_rate=0.0)
    assert 0.6 < tau <= 0.8
    assert feasible
    metrics = call_metrics(calls, "S", tau)
    assert metrics["attacker_calls_allowed"] == 0
    assert metrics["user_calls_blocked"] == 0
    assert call_metrics(calls, "S", 0.0)["attacker_calls_allowed"] == 1


def test_threshold_reports_impossible_utility_constraint() -> None:
    calls = [
        {"label": "user_tool", "S": 0.0, "hard_veto": True, "request_group": "u"},
        {"label": "attacker_tool", "S": 0.5, "hard_veto": False, "request_group": "a"},
    ]
    _, feasible = tune_tau(calls, "S", max_user_block_rate=0.1)
    assert not feasible


def test_conformal_groups_repeated_requests_before_splitting(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    rows = [
        {"case_id": case_id, "contract": {"raw_request": request}, "gate": {"S": score}}
        for case_id, request, score in (
            ("dh_base_0", "same request", 0.8),
            ("dh_enhanced_0", "same request", 0.0),
            ("dh_base_1", "other request", 0.7),
        )
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    groups = grouped_scores([path], tau=0.75)
    assert len(groups) == 2
    repeated = next(group for group in groups.values() if len(group["case_ids"]) == 2)
    assert repeated["max_deviation"] == pytest.approx(0.75)
    summary, heldout = evaluate_split(groups, tau=0.75, alpha=0.1, seed=42)
    assert summary["group_overlap"] == 0
    assert summary["calibration_groups"] == 1
    assert summary["heldout_groups"] == 1
    assert summary["band"]["used_full_support"]
    assert heldout[0]["covered"]
