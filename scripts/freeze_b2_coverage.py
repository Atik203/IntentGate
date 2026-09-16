"""Freeze ToolGate B2 contract coverage over the evaluated benchmark tool universes.

Usage:
  python scripts/freeze_b2_coverage.py
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def injecagent_universe(case_files: list[Path]) -> tuple[set[str], int]:
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


def mcptox_universe(snapshot: Path) -> tuple[set[str], Counter, int]:
    from harness.adapters.mcptox import load_mcptox_cases

    cases = load_mcptox_cases(snapshot)
    availability: Counter = Counter()
    for case in cases:
        for tool in set(case.clean_tools):
            availability[tool] += 1
    return set(availability), availability, len(cases)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/raw/InjecAgent/data")
    ap.add_argument("--mcptox", default="data/raw/mcptox/response_all.json")
    ap.add_argument("--out", default="configs/b2_coverage.json")
    args = ap.parse_args()

    from intent_gate.baselines.toolgate.checker import ToolGateChecker

    data_dir = ROOT / args.data_dir
    case_files = sorted(data_dir.glob("test_cases_*_base.json"))
    case_files += sorted(data_dir.glob("test_cases_*_enhanced.json"))
    if not case_files:
        print(f"no InjecAgent case files under {data_dir}; clone benchmarks first")
        raise SystemExit(1)

    universe, n_cases = injecagent_universe(case_files)
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

    snapshot = ROOT / args.mcptox
    if snapshot.exists():
        mcptox_tools, availability, n_mcptox = mcptox_universe(snapshot)
        mc_checker = ToolGateChecker(evaluated_tools=mcptox_tools)
        mc_contracted = sorted(set(mc_checker.contracts) & mcptox_tools)
        total_slots = sum(availability.values())
        contracted_slots = sum(availability[tool] for tool in mc_contracted)
        report["mcptox"] = {
            "benchmark": "MCPTox static snapshot (registered toolset, incl. poisoned tools)",
            "snapshot": args.mcptox,
            "n_cases": n_mcptox,
            "evaluated_tools": len(mcptox_tools),
            "contracted_tools": len(mc_contracted),
            "coverage": round(len(mc_contracted) / len(mcptox_tools), 4) if mcptox_tools else 0.0,
            "availability_weighted_coverage": round(contracted_slots / total_slots, 4) if total_slots else 0.0,
            "contracted_names": mc_contracted,
            "missing_tools": sorted(mcptox_tools - set(mc_checker.contracts)),
        }

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"B2 coverage {report['contracted_tools']}/{report['evaluated_tools']} "
        f"({report['coverage']:.1%}) over {n_cases} InjecAgent cases -> {args.out}"
    )
    if "mcptox" in report:
        mc = report["mcptox"]
        print(
            f"MCPTox coverage {mc['contracted_tools']}/{mc['evaluated_tools']} "
            f"({mc['coverage']:.1%} tools; {mc['availability_weighted_coverage']:.1%} availability-weighted) "
            f"over {mc['n_cases']} cases"
        )
    if report["missing_tools"]:
        print(f"missing InjecAgent contracts ({len(report['missing_tools'])}): {report['missing_tools']}")


if __name__ == "__main__":
    main()
