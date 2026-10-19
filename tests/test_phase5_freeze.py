"""Phase 5 freeze guard: --run must reproduce the frozen matrix/limit/settings, never drift."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pytest

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


def test_artifact_jobs_do_not_load_raw_datasets(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse_raw_dataset_load(limit: int | None) -> dict[str, int]:
        raise AssertionError("artifact checks must not require benchmark clones")

    monkeypatch.setattr(run_phase5, "_case_counts", refuse_raw_dataset_load)
    jobs = run_phase5.build_jobs(
        _args(artifacts_only=True, no_resume=False, conditions=[], benchmarks=[])
    )
    assert len(jobs) == 30
    assert sum(job.n_cases for job in jobs) == 6 * (2108 + 1348)
    assert {job.n_cases for job in jobs} == {510, 544, 1348}


def test_artifact_hashes_detect_changed_frozen_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    results = tmp_path / "results" / "phase5"
    results.mkdir(parents=True)
    artifact = results / "ours_mcptox.json"
    artifact.write_text("original", encoding="utf-8")
    manifest = tmp_path / "artifact_hashes.json"
    manifest.write_text(
        json.dumps({"files": {"results/phase5/ours_mcptox.json": run_phase5._sha256(artifact)}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(run_phase5, "ROOT", tmp_path)
    monkeypatch.setattr(run_phase5, "RESULT_DIR", results)
    monkeypatch.setattr(run_phase5, "ARTIFACT_HASHES_PATH", manifest)
    assert run_phase5.verify_artifact_hashes() == []
    artifact.write_text("edited after freeze", encoding="utf-8")
    assert run_phase5.verify_artifact_hashes() == [
        "artifact missing or changed: results/phase5/ours_mcptox.json"
    ]


def test_artifact_hashes_reject_paths_outside_published_results(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    manifest = tmp_path / "artifact_hashes.json"
    manifest.write_text(json.dumps({"files": {"README.md": "irrelevant"}}), encoding="utf-8")
    monkeypatch.setattr(run_phase5, "ROOT", tmp_path)
    monkeypatch.setattr(run_phase5, "RESULT_DIR", tmp_path / "results" / "phase5")
    monkeypatch.setattr(run_phase5, "ARTIFACT_HASHES_PATH", manifest)
    assert run_phase5.verify_artifact_hashes() == [
        "artifact path outside results/phase5: README.md"
    ]
