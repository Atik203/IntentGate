"""Run a gated condition (none / ours / toolgate) on the MCPTox static snapshot (blueprint Sec 6/8).

Usage: python harness/run_mcptox.py --gate ours --snapshot v1 --report results/mcptox.json
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
    ap.add_argument("--cases", default="data/raw/mcptox/response_all.json", help="MCPTox snapshot path")
    ap.add_argument("--gate", choices=["none", "ours", "toolgate"], default="ours")
    ap.add_argument("--snapshot", default="v1", help="snapshot version tag to document")
    ap.add_argument("--risk", default=None, help="filter to one risk category")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--delta", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--model-name", default=None)
    ap.add_argument("--report", default="results/mcptox.json")
    ap.add_argument("--jsonl", default="")
    ap.add_argument("--trace", default="")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from harness.adapters.mcptox import load_mcptox_cases
    from harness.gate_policy import build_policy_factory
    from harness.mcptox_runner import run_cases
    from intent_gate.agent.base import LLMClient
    from intent_gate.baselines.toolgate.world_state import seed_from_request
    from intent_gate.gate.trace import TraceLogger
    from intent_gate.parser.parser import build_parser
    from intent_gate.scoring.embeddings import EmbeddingBackend

    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")
    cases = load_mcptox_cases(ROOT / args.cases, limit=args.limit, seed=args.seed, risk=args.risk)
    llm = LLMClient(model_id=model_name)

    report_path = (ROOT / args.report).resolve()
    jsonl_path = Path(args.jsonl) if args.jsonl else report_path.with_suffix(".jsonl")
    trace_path = Path(args.trace) if args.trace else report_path.with_name(f"{report_path.stem}_trace.jsonl")
    backend = EmbeddingBackend()
    trace = TraceLogger(
        trace_path,
        metadata={
            "benchmark": "mcptox",
            "snapshot": args.snapshot,
            "model_id": model_name,
            "gate": args.gate,
            "tau": args.threshold,
            "delta": args.delta,
            "alpha": args.alpha,
            "embedding": backend.metadata,
        },
        append=False,
    )
    policy_factory = build_policy_factory(
        args.gate,
        parser=build_parser(model_id=os.getenv("PARSER_MODEL_ID")),
        backend=backend,
        trace=trace,
        tau=args.threshold,
        delta=args.delta,
        alpha=args.alpha,
        state_factory=seed_from_request,
    )
    summary, _ = run_cases(cases, llm, policy_factory=policy_factory, jsonl_path=jsonl_path)
    trace.close()

    report = {
        "benchmark": "mcptox",
        "cases": args.cases,
        "snapshot": args.snapshot,
        "model_id": model_name,
        "gate": args.gate,
        "tau": args.threshold,
        "delta": args.delta,
        "embedding": backend.metadata,
        "evaluator": "heuristic (payload/sensitive-path; see harness/mcptox_runner.py)",
        **summary,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
