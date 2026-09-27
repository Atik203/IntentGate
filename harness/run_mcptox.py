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
    ap.add_argument(
        "--ablation",
        choices=["none", "semantic-only", "rule-only", "raw-request"],
        default="none",
    )
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
    if args.ablation != "none" and args.gate != "ours":
        ap.error("--ablation requires --gate ours")

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from harness.adapters.mcptox import load_mcptox_cases
    from harness.gate_policy import build_policy_factory
    from harness.mcptox_runner import run_cases
    from intent_gate.agent.base import LLMClient
    from intent_gate.baselines.toolgate.world_state import seed_from_request
    from intent_gate.eval.cost import estimate_usage_cost
    from intent_gate.gate.trace import TraceLogger
    from intent_gate.parser.parser import build_parser
    from intent_gate.scoring.embeddings import EmbeddingBackend

    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")
    cases = load_mcptox_cases(ROOT / args.cases, limit=args.limit, seed=args.seed, risk=args.risk)
    llm = LLMClient(model_id=model_name)
    parser_llm = (
        LLMClient(model_id=os.getenv("PARSER_MODEL_ID", "gpt-4o-mini")) if args.gate == "ours" else None
    )

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
            "ablation": args.ablation,
            "embedding": backend.metadata,
        },
        append=False,
    )
    policy_factory = build_policy_factory(
        args.gate,
        parser=build_parser(llm=parser_llm),
        backend=backend,
        trace=trace,
        tau=args.threshold,
        delta=args.delta,
        alpha=args.alpha,
        state_factory=seed_from_request,
        ablation=args.ablation,
    )
    summary, _ = run_cases(cases, llm, policy_factory=policy_factory, jsonl_path=jsonl_path)
    trace.close()

    agent_cost = estimate_usage_cost(llm.usage)
    parser_cost = estimate_usage_cost(parser_llm.usage) if parser_llm else None
    total_cost = None
    if agent_cost is not None or parser_cost is not None:
        total_cost = round((agent_cost or 0.0) + (parser_cost or 0.0), 4)

    report = {
        "benchmark": "mcptox",
        "cases": args.cases,
        "snapshot": args.snapshot,
        "model_id": model_name,
        "gate": args.gate,
        "ablation": args.ablation,
        "tau": args.threshold,
        "delta": args.delta,
        "embedding": backend.metadata,
        "evaluator": "heuristic (payload/sensitive-path; see harness/mcptox_runner.py)",
        "usage": {"agent": llm.usage, "parser": parser_llm.usage if parser_llm else None},
        "estimated_cost_usd": total_cost,
        **summary,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
