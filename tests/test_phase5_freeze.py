"""Phase 5 freeze guard: --run must reproduce the frozen matrix/limit/settings, never drift."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("run_phase5", ROOT / "scripts" / "run_phase5.py")
run_phase5 = importlib.util.module_from_spec(_SPEC)
sys.modules["run_phase5"] = run_phase5  # dataclass field resolution needs this during exec
_SPEC.loader.exec_module(run_phase5)


def _args(**overrides) -> argparse.Namespace:
    base = {
        "tau": 0.75,
        "delta": 0.1,
        "alpha": 0.7,
        "seed": 42,
        "limit": None,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def _job(name: str) -> run_phase5.Job:
    return run_phase5.Job(
        name=name,
        benchmark="mcptox",
        command=[],
        report=Path(f"results/phase5/{name}.json"),
        log=Path(f"results/phase5/logs/{name}.log"),
        n_cases=10,
    )


def _manifest(matrix=("b1_mcptox", "ours_mcptox")) -> dict:
    return {
        "git_dirty": False,
        "configs": {},
        "settings": {"tau": 0.75, "delta": 0.1, "alpha": 0.7, "seed": 42},
        "matrix": list(matrix),
        "limit": None,
    }


def test_verify_manifest_accepts_matching_run():
    jobs = [_job("b1_mcptox"), _job("ours_mcptox")]
    assert run_phase5.verify_manifest(_manifest(), jobs, _args()) == []


def test_verify_manifest_rejects_different_matrix():
    jobs = [_job("b1_mcptox")]
    problems = run_phase5.verify_manifest(_manifest(), jobs, _args())
    assert any("matrix changed" in p for p in problems)


def test_verify_manifest_rejects_different_limit():
    jobs = [_job("b1_mcptox"), _job("ours_mcptox")]
    problems = run_phase5.verify_manifest(_manifest(), jobs, _args(limit=5))
    assert any("limit changed" in p for p in problems)


def test_verify_manifest_rejects_changed_setting():
    jobs = [_job("b1_mcptox"), _job("ours_mcptox")]
    problems = run_phase5.verify_manifest(_manifest(), jobs, _args(tau=0.6))
    assert any("tau" in p for p in problems)


def test_verify_manifest_rejects_dirty_freeze():
    jobs = [_job("b1_mcptox"), _job("ours_mcptox")]
    manifest = _manifest()
    manifest["git_dirty"] = True
    problems = run_phase5.verify_manifest(manifest, jobs, _args())
    assert any("dirty" in p for p in problems)
