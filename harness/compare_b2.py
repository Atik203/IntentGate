"""Compare B2 (ToolGate) vs ours on identical cases (README Quick Start: compare_b2.py)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from intent_gate.baselines.toolgate.checker import ToolGateChecker
from intent_gate.types import ToolCall


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--report", default="results/comparison.json")
    args = ap.parse_args()

    from harness.common import load_cases

    checker = ToolGateChecker()
    # TODO(Gate 2): run both gates through the same agent loop and fill real metrics.
    calls = [ToolCall(name="transfer_money", parameters={"amount": 500}), ToolCall(name="read_file", parameters={"path": "x"})]
    obs = [checker.check(c) for c in calls]
    out = {
        "baseline": "toolgate_b2",
        "n_cases": len(load_cases(args.cases)),
        "no_contract_count": checker.no_contract_count,
        "violations": checker.violations,
        "observations": obs,
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {args.report}")


if __name__ == "__main__":
    main()
