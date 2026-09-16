"""Run a gated condition (none / ours / toolgate) on one InjecAgent case file (blueprint Sec 6/13).

Usage: python harness/run_injecagent.py --cases data/raw/InjecAgent/data/test_cases_dh_base.json \
  --gate ours --threshold 0.6 --report results/injecagent.json
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
    ap.add_argument("--cases", required=True, help="InjecAgent test_cases_*.json path")
    ap.add_argument("--gate", choices=["none", "ours", "toolgate"], default="none")
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--delta", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--model-name", default=None)
    ap.add_argument("--report", default="results/injecagent.json")
    ap.add_argument("--jsonl", default="")
    ap.add_argument("--trace", default="")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from harness.adapters.injecagent import load_injecagent_cases, load_tool_definitions
    from harness.gate_policy import build_policy_factory
    from harness.injecagent_runner import build_tool_dict, run_cases
    from intent_gate.agent.base import LLMClient
    from intent_gate.baselines.toolgate.world_state import seed_from_request
    from intent_gate.gate.trace import TraceLogger
    from intent_gate.parser.parser import build_parser
    from intent_gate.scoring.embeddings import EmbeddingBackend

    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")
    cases = load_injecagent_cases(ROOT / args.cases, limit=args.limit, seed=args.seed)
    tool_dict = build_tool_dict(
        load_tool_definitions(ROOT / "data/raw/InjecAgent/data/tools.json")
    )
    llm = LLMClient(model_id=model_name)

    report_path = (ROOT / args.report).resolve()
    jsonl_path = Path(args.jsonl) if args.jsonl else report_path.with_suffix(".jsonl")
    trace_path = Path(args.trace) if args.trace else report_path.with_name(f"{report_path.stem}_trace.jsonl")
    backend = EmbeddingBackend()
    trace = TraceLogger(
        trace_path,
        metadata={
            "benchmark": "injecagent",
            "cases": args.cases,
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
    summary, _ = run_cases(cases, llm, tool_dict, policy_factory=policy_factory, jsonl_path=jsonl_path)
    trace.close()

    report = {
        "benchmark": "injecagent",
        "cases": args.cases,
        "model_id": model_name,
        "gate": args.gate,
        "tau": args.threshold,
        "delta": args.delta,
        "embedding": backend.metadata,
        **summary,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
