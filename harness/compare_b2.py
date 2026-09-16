"""B2 (ToolGate) report: contract coverage + recorded-call replay (README Quick Start)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.adapters.injecagent import load_injecagent_cases
from intent_gate.baselines.toolgate.checker import ToolGateChecker
from intent_gate.types import ToolCall


def _load_recorded_calls(path: Path) -> list[ToolCall]:
    calls: list[ToolCall] = []
    if not path.exists():
        return calls
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for call in row.get("tool_calls") or []:
            calls.append(ToolCall(name=call["name"], parameters=call.get("parameters") or {}))
    return calls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", nargs="+", required=True)
    ap.add_argument("--replay", nargs="*", default=[])
    ap.add_argument("--report", default="results/comparison.json")
    args = ap.parse_args()

    cases = [case for path in args.cases for case in load_injecagent_cases(path)]
    universe = {case.user_tool for case in cases}
    for case in cases:
        universe.update(case.attacker_tools)

    checker = ToolGateChecker(evaluated_tools=universe)
    replay = {"calls": 0, "violations": 0, "no_contract": 0}
    for replay_path in args.replay:
        for call in _load_recorded_calls(Path(replay_path)):
            obs = checker.check(call)
            replay["calls"] += 1
            replay["violations"] += 1 if obs.startswith("ToolGate violation") else 0
            replay["no_contract"] += 1 if obs.startswith("no_contract:") else 0

    out = {
        "baseline": "toolgate_b2",
        "n_cases": len(cases),
        "evaluated_tools": len(universe),
        "contracted_tools": len(set(checker.contracts) & universe),
        "coverage": checker.coverage,
        "violations": checker.violations,
        "no_contract_count": checker.no_contract_count,
        "no_contract_tools": sorted(checker.no_contract_tools),
        "replay": replay,
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {args.report}")


if __name__ == "__main__":
    main()
