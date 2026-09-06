"""Run gates on MCPTox (blueprint Sec 6/8). --snapshot falls back to static tool definitions
if live servers unavailable; document exact server/snapshot versions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from intent_gate.parser.parser import IntentParser


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True, help="path to MCPTox case/snapshot file")
    ap.add_argument("--gate", choices=["none", "ours", "toolgate"], default="ours")
    ap.add_argument("--snapshot", default="v1", help="snapshot version tag to document")
    ap.add_argument("--report", default="results/mcptox.json")
    args = ap.parse_args()

    from harness.common import load_cases, set_seed

    set_seed(42)
    cases = load_cases(args.cases)
    parser = IntentParser()
    # TODO(Gate 2): map MCPTox 10 risk categories -> rule engine vetoes; run agent loop.
    out = {
        "benchmark": "MCPTox",
        "gate": args.gate,
        "snapshot": args.snapshot,
        "n_cases": len(cases),
        "note": "static snapshot; live-server dynamics may differ (blueprint Sec 8 limitation)",
        "cases": [{"case_id": c["case_id"], "contract": parser.parse(c["user_request"]).to_dict()} for c in cases],
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {args.report} ({len(cases)} cases)")


if __name__ == "__main__":
    main()
