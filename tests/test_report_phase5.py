"""Phase 5 reporter helpers (name parsing, case labels)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("report_phase5", ROOT / "scripts" / "report_phase5.py")
report_phase5 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(report_phase5)


def test_parse_name_aliases():
    assert report_phase5.parse_name("ours_test_cases_dh_base") == ("ours", "injecagent:dh:base")
    assert report_phase5.parse_name("none_dh50") == ("b1", "dh50")
    assert report_phase5.parse_name("toolgate_mcptox100") == ("b2", "mcptox")
    assert report_phase5.parse_name("a1_semantic_only_mcptox") == ("a1", "mcptox")
    assert report_phase5.parse_name("not_a_condition") is None


def test_success_labels():
    assert report_phase5.success_label({"eval": "succ"}, "injecagent") is True
    assert report_phase5.success_label({"eval": "unsucc"}, "injecagent") is False
    assert report_phase5.success_label({"label": "success"}, "mcptox") is True
    assert report_phase5.success_label({"label": "work_not_success"}, "mcptox") is False
    assert report_phase5.case_success({"label": "work_not_success"}, "mcptox") is True
    assert report_phase5.case_success({"eval": "error"}, "injecagent") is None
