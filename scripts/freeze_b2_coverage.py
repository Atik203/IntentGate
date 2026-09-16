"""Freeze ToolGate B2 contract coverage over the evaluated InjecAgent tool universe.

Usage:
  python scripts/freeze_b2_coverage.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def evaluated_universe(case_files: list[Path]) -> tuple[set[str], int]:
    from harness.adapters.injecagent import load_injecagent_cases

    universe: set[str] = set()
    n_cases = 0
    for path in case_files:
        cases = load_injecagent_cases(path)
        n_cases += len(cases)
        for case in cases:
            universe.add(case.user_tool)
            universe.update(case.attacker_tools)
    return universe, n_cases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/raw/InjecAgent/data")
    ap.add_argument("--out", default="configs/b2_coverage.json")
    args = ap.parse_args()

    from intent_gate.baselines.toolgate.checker import ToolGateChecker

    data_dir = ROOT / args.data_dir
    case_files = sorted(data_dir.glob("test_cases_*_base.json"))
    case_files += sorted(data_dir.glob("test_cases_*_enhanced.json"))
    if not case_files:
        print(f"no InjecAgent case files under {data_dir}; clone benchmarks first")
        raise SystemExit(1)

    universe, n_cases = evaluated_universe(case_files)
    checker = ToolGateChecker(evaluated_tools=universe)
    contracted = sorted(set(checker.contracts) & universe)
    report = {
        "benchmark": "InjecAgent (dh/ds, base+enhanced)",
        "frozen_on": datetime.now(UTC).date().isoformat(),
        "case_files": [str(p.relative_to(ROOT)) for p in case_files],
        "n_cases": n_cases,
        "evaluated_tools": len(universe),
        "contracted_tools": len(contracted),
        "coverage": round(checker.coverage or 0.0, 4),
        "missing_tools": sorted(universe - set(checker.contracts)),
        "extra_contracts": sorted(set(checker.contracts) - universe),
        "total_contracts": len(checker.contracts),
    }
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"B2 coverage {report['contracted_tools']}/{report['evaluated_tools']} "
        f"({report['coverage']:.1%}) over {n_cases} cases -> {args.out}"
    )
    if report["missing_tools"]:
        print(f"missing contracts ({len(report['missing_tools'])}): {report['missing_tools']}")


if __name__ == "__main__":
    main()
