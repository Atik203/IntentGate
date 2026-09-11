"""Run OUR B1 pipeline on the MCPTox static snapshot (S4).

Usage: python scripts/run_mcptox_ours.py --limit 20
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--risk", default=None, help="filter to one risk category")
    ap.add_argument("--model-name", default=None)
    ap.add_argument("--out", default="results/mcptox_ours")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")

    from harness.adapters.mcptox import load_mcptox_cases
    from harness.mcptox_runner import run_case
    from intent_gate.agent.base import LLMClient

    cases = load_mcptox_cases(ROOT / "data/raw/mcptox/response_all.json", limit=args.limit, seed=args.seed, risk=args.risk)
    llm = LLMClient(model_id=model_name)
    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    counts: dict = {}
    by_risk: dict = {}
    out_file = out_dir / "mcptox_b1.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for case in cases:
            result = run_case(case, llm)
            counts[result.label] = counts.get(result.label, 0) + 1
            by_risk.setdefault(case.risk, {}).setdefault(result.label, 0)
            by_risk[case.risk][result.label] += 1
            fh.write(
                json.dumps(
                    {
                        "case_id": case.case_id,
                        "server": case.server,
                        "risk": case.risk,
                        "paradigm": case.paradigm,
                        "fake_tool": case.fake_tool,
                        "label": result.label,
                        "called_tool": result.called_tool,
                        "arguments": result.arguments,
                        "indicators": result.indicators,
                        "error": result.error,
                    }
                )
                + "\n"
            )
            print(f"{result.label:>16} | {case.risk:<24} | {case.fake_tool:<12} -> {result.called_tool}")

    summary = {
        "model_name": model_name,
        "n": len(cases),
        "counts": counts,
        "by_risk": by_risk,
        "evaluator": "heuristic (payload/sensitive-path; see harness/mcptox_runner.py)",
        "snapshot": "AAAI26-7C02 downloaded 2026-09-11 (static)",
    }
    summary_file = out_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {summary_file}")


if __name__ == "__main__":
    main()
