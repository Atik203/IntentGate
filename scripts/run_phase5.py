"""Phase 5 orchestrator: freeze lock, run the evaluation matrix, resume, integrity-check.

Usage:
  python scripts/run_phase5.py --freeze            # write lock + manifest (clean tree required)
  python scripts/run_phase5.py --run --jobs 3      # execute/resume the matrix
  python scripts/run_phase5.py --check             # verify artifacts vs manifest
  python scripts/run_phase5.py --dry-run           # list jobs + call estimate, no API calls
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RESULT_DIR = ROOT / "results" / "phase5"
LOG_DIR = RESULT_DIR / "logs"
LOCK_PATH = ROOT / "configs" / "phase5_lock.json"
MANIFEST_PATH = RESULT_DIR / "manifest.json"

INJECAGENT_FILES = [
    "test_cases_dh_base.json",
    "test_cases_ds_base.json",
    "test_cases_dh_enhanced.json",
    "test_cases_ds_enhanced.json",
]
MCPTOX_FILE = "data/raw/mcptox/response_all.json"

CONDITIONS = [
    ("b1", "none", "none"),
    ("b2", "toolgate", "none"),
    ("ours", "ours", "none"),
    ("a1_semantic_only", "ours", "semantic-only"),
    ("a2_rule_only", "ours", "rule-only"),
    ("a3_raw_request", "ours", "raw-request"),
]

LOCKED_CONFIGS = [
    "configs/intent_schema.json",
    "configs/parser_fewshots.json",
    "configs/thresholds.yaml",
    "configs/models.yaml",
    "configs/b2_coverage.json",
]


@dataclass
class Job:
    name: str
    benchmark: str
    command: list[str]
    report: Path
    log: Path
    n_cases: int

    @property
    def est_calls(self) -> int:
        return self.n_cases * (2 if "--gate" in self.command and "ours" in self.command else 1)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _case_counts(limit: int | None) -> dict[str, int]:
    import json as _json

    from harness.adapters.mcptox import load_mcptox_cases

    counts: dict[str, int] = {}
    for name in INJECAGENT_FILES:
        data = _json.loads((ROOT / "data/raw/InjecAgent/data" / name).read_text(encoding="utf-8"))
        counts[name] = min(limit, len(data)) if limit else len(data)
    total = len(load_mcptox_cases(ROOT / MCPTOX_FILE))
    counts["mcptox"] = min(limit, total) if limit else total
    return counts


def build_jobs(args) -> list[Job]:
    counts = _case_counts(args.limit)
    jobs: list[Job] = []
    for condition, gate, ablation in CONDITIONS:
        if args.conditions and condition not in args.conditions:
            continue
        for filename in INJECAGENT_FILES:
            if args.benchmarks and "injecagent" not in args.benchmarks:
                continue
            report = RESULT_DIR / f"{condition}_{Path(filename).stem}.json"
            command = [
                sys.executable,
                "harness/run_injecagent.py",
                "--cases",
                f"data/raw/InjecAgent/data/{filename}",
                "--gate",
                gate,
                "--ablation",
                ablation,
                "--threshold",
                str(args.tau),
                "--delta",
                str(args.delta),
                "--alpha",
                str(args.alpha),
                "--seed",
                str(args.seed),
                "--report",
                str(report),
            ]
            if args.limit:
                command += ["--limit", str(args.limit)]
            jobs.append(
                Job(
                    name=f"{condition}_{Path(filename).stem}",
                    benchmark="injecagent",
                    command=command,
                    report=report,
                    log=LOG_DIR / f"{condition}_{Path(filename).stem}.log",
                    n_cases=counts[filename],
                )
            )
        if not args.benchmarks or "mcptox" in args.benchmarks:
            report = RESULT_DIR / f"{condition}_mcptox.json"
            command = [
                sys.executable,
                "harness/run_mcptox.py",
                "--gate",
                gate,
                "--ablation",
                ablation,
                "--threshold",
                str(args.tau),
                "--delta",
                str(args.delta),
                "--alpha",
                str(args.alpha),
                "--seed",
                str(args.seed),
                "--report",
                str(report),
            ]
            if args.limit:
                command += ["--limit", str(args.limit)]
            jobs.append(
                Job(
                    name=f"{condition}_mcptox",
                    benchmark="mcptox",
                    command=command,
                    report=report,
                    log=LOG_DIR / f"{condition}_mcptox.log",
                    n_cases=counts["mcptox"],
                )
            )
    return jobs


def build_manifest(args) -> dict:
    from intent_gate.scoring.embeddings import EmbeddingBackend

    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    return {
        "created": datetime.now(UTC).isoformat(),
        "git_sha": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip(),
        "git_dirty": bool(dirty),
        "configs": {path: _sha256(ROOT / path) for path in LOCKED_CONFIGS},
        "models": {
            "agent": args.model_name,
            "parser": args.parser_model,
            "embedding": EmbeddingBackend().metadata,
        },
        "settings": {"tau": args.tau, "delta": args.delta, "alpha": args.alpha, "seed": args.seed},
        "matrix": [],
        "limit": args.limit,
    }


def verify_manifest(manifest: dict) -> list[str]:
    problems = []
    if manifest.get("git_dirty"):
        problems.append("manifest was created from a dirty working tree")
    for path, digest in (manifest.get("configs") or {}).items():
        if not (ROOT / path).exists() or _sha256(ROOT / path) != digest:
            problems.append(f"config changed since freeze: {path}")
    return problems


def run_job(job: Job, retries: int) -> tuple[str, int, float]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    for attempt in range(retries + 1):
        with job.log.open("w" if attempt == 0 else "a", encoding="utf-8") as handle:
            handle.write(f"$ {' '.join(job.command)}\n")
            handle.flush()
            proc = subprocess.run(
                job.command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False
            )
        if proc.returncode == 0:
            return job.name, 0, time.perf_counter() - started
        time.sleep(2 * (attempt + 1))
    return job.name, proc.returncode, time.perf_counter() - started


def run_check(jobs: list[Job], manifest: dict) -> list[str]:
    failures = []
    for job in jobs:
        if not job.report.exists():
            failures.append(f"missing report: {job.report.name}")
            continue
        report = json.loads(job.report.read_text(encoding="utf-8"))
        counts = report.get("counts") or {}
        if report.get("n") != job.n_cases:
            failures.append(f"{job.report.name}: n={report.get('n')} expected {job.n_cases}")
        if counts and sum(counts.values()) != report.get("n"):
            failures.append(f"{job.report.name}: counts do not sum to n")
        if report.get("gate") != "none" and not report.get("usage"):
            failures.append(f"{job.report.name}: missing usage block")
        if "embedding" not in report:
            failures.append(f"{job.report.name}: missing embedding metadata")
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true", help="write lock + manifest before runs")
    ap.add_argument("--run", action="store_true", help="execute/resume the matrix")
    ap.add_argument("--check", action="store_true", help="verify artifacts vs manifest")
    ap.add_argument("--dry-run", action="store_true", help="list jobs + call estimate only")
    ap.add_argument("--force", action="store_true", help="overwrite existing reports / lock")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--max-calls", type=int, default=30000)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--conditions", nargs="*", default=[])
    ap.add_argument("--benchmarks", nargs="*", default=[])
    ap.add_argument("--tau", type=float, default=0.75)
    ap.add_argument("--delta", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--model-name", default="gpt-4o-mini")
    ap.add_argument("--parser-model", default="gpt-4o-mini")
    args = ap.parse_args()

    jobs = build_jobs(args)
    est_calls = sum(job.est_calls for job in jobs)
    print(f"matrix jobs: {len(jobs)} | estimated LLM calls: {est_calls}")

    if args.dry_run:
        for job in jobs:
            print(f"  {job.name:<34} n={job.n_cases:<5} est_calls={job.est_calls:<6} -> {job.report.name}")
        return

    if args.freeze:
        problems = []
        if LOCK_PATH.exists() and not args.force:
            problems.append(f"{LOCK_PATH.name} already exists (use --force to overwrite)")
        if problems:
            print("freeze refused:")
            for problem in problems:
                print(f"  - {problem}")
            raise SystemExit(1)
        manifest = build_manifest(args)
        manifest["matrix"] = [job.name for job in jobs]
        if manifest["git_dirty"]:
            print("working tree is dirty - clean it before freezing")
            raise SystemExit(1)
        if est_calls > args.max_calls:
            print(f"estimated calls {est_calls} exceed --max-calls {args.max_calls}")
            raise SystemExit(1)
        RESULT_DIR.mkdir(parents=True, exist_ok=True)
        LOCK_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"frozen: {LOCK_PATH} + {MANIFEST_PATH}")
        return

    if args.check:
        if not MANIFEST_PATH.exists():
            print("no manifest; run --freeze first")
            raise SystemExit(1)
        failures = run_check(jobs, json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))
        if failures:
            print(f"integrity check FAILED ({len(failures)}):")
            for failure in failures:
                print(f"  - {failure}")
            raise SystemExit(1)
        print("integrity check passed")
        return

    if args.run:
        if not MANIFEST_PATH.exists():
            print("no manifest; run --freeze first")
            raise SystemExit(1)
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        problems = verify_manifest(manifest)
        if problems:
            print("refusing to run - freeze violated:")
            for problem in problems:
                print(f"  - {problem}")
            raise SystemExit(1)
        pending = [job for job in jobs if args.force or not job.report.exists()]
        print(f"running {len(pending)}/{len(jobs)} jobs (jobs={args.jobs})")
        failures = []
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futures = {pool.submit(run_job, job, args.retries): job for job in pending}
            for future in as_completed(futures):
                name, code, elapsed = future.result()
                status = "ok" if code == 0 else f"FAILED({code})"
                print(f"  {name:<34} {status:<12} {elapsed:6.1f}s")
                if code != 0:
                    failures.append(name)
        if failures:
            print(f"failed jobs ({len(failures)}): {failures}")
            raise SystemExit(1)
        print("all jobs complete")
        return

    ap.error("choose one of --freeze / --run / --check / --dry-run")


if __name__ == "__main__":
    main()
