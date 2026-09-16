"""Run OUR pipeline on the MCPTox static snapshot (S4 / gated conditions).

Usage: python scripts/run_mcptox_ours.py --limit 20 --gate ours
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
    ap.add_argument("--gate", choices=["none", "ours", "toolgate"], default="none")
    ap.add_argument("--tau", type=float, default=0.6)
    ap.add_argument("--delta", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--model-name", default=None)
    ap.add_argument("--out", default="results/mcptox_ours")
    ap.add_argument("--trace", default="")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")

    from harness.adapters.mcptox import load_mcptox_cases
    from harness.gate_policy import build_policy_factory
    from harness.mcptox_runner import run_cases
    from intent_gate.agent.base import LLMClient
    from intent_gate.baselines.toolgate.world_state import seed_from_request
    from intent_gate.gate.trace import TraceLogger
    from intent_gate.parser.parser import build_parser
    from intent_gate.scoring.embeddings import EmbeddingBackend

    cases = load_mcptox_cases(
        ROOT / "data/raw/mcptox/response_all.json", limit=args.limit, seed=args.seed, risk=args.risk
    )
    llm = LLMClient(model_id=model_name)
    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    backend = EmbeddingBackend()
    trace_path = Path(args.trace) if args.trace else out_dir / "gate_trace.jsonl"
    trace = TraceLogger(
        trace_path,
        metadata={
            "benchmark": "mcptox",
            "model_id": model_name,
            "gate": args.gate,
            "tau": args.tau,
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
        tau=args.tau,
        delta=args.delta,
        alpha=args.alpha,
        state_factory=seed_from_request,
    )

    def progress(result, case):
        print(f"{result.label:>16} | {case.risk:<24} | {case.fake_tool:<12} -> {result.called_tool}")

    summary, _ = run_cases(
        cases,
        llm,
        policy_factory=policy_factory,
        jsonl_path=out_dir / "mcptox_b1.jsonl",
        progress=progress,
    )
    trace.close()

    summary.update(
        {
            "model_name": model_name,
            "gate": args.gate,
            "tau": args.tau,
            "delta": args.delta,
            "embedding": backend.metadata,
            "evaluator": "heuristic (payload/sensitive-path; see harness/mcptox_runner.py)",
            "snapshot": "AAAI26-7C02 downloaded 2026-09-11 (static)",
        }
    )
    summary_file = out_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {summary_file}")


if __name__ == "__main__":
    main()
