"""Run OUR pipeline on an InjecAgent subset (S3b / gated conditions; blueprint Sec 13).

Usage: python scripts/run_injecagent_ours.py --per-split 10 --setting base --gate ours
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
    ap.add_argument("--per-split", type=int, default=10)
    ap.add_argument("--setting", choices=["base", "enhanced"], default="base")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--gate", choices=["none", "ours", "toolgate"], default="none")
    ap.add_argument("--tau", type=float, default=0.6)
    ap.add_argument("--delta", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--model-name", default=None)
    ap.add_argument("--out", default="results/injecagent_ours")
    ap.add_argument("--trace", default="")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")

    from harness.adapters.injecagent import load_injecagent_cases, load_tool_definitions
    from harness.gate_policy import build_policy_factory
    from harness.injecagent_runner import build_tool_dict, run_cases, serialize_calls
    from intent_gate.agent.base import LLMClient
    from intent_gate.baselines.toolgate.world_state import seed_from_request
    from intent_gate.gate.trace import TraceLogger
    from intent_gate.parser.parser import build_parser
    from intent_gate.scoring.embeddings import EmbeddingBackend

    tool_dict = build_tool_dict(load_tool_definitions(ROOT / "data/raw/InjecAgent/data/tools.json"))
    llm = LLMClient(model_id=model_name)
    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    backend = EmbeddingBackend()
    trace_path = Path(args.trace) if args.trace else out_dir / f"gate_trace_{args.setting}.jsonl"
    trace = TraceLogger(
        trace_path,
        metadata={
            "benchmark": "injecagent",
            "setting": args.setting,
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

    summary = {"model_name": model_name, "setting": args.setting, "gate": args.gate, "splits": {}}
    for split in ["dh", "ds"]:
        case_file = ROOT / "data/raw/InjecAgent/data" / f"test_cases_{split}_{args.setting}.json"
        cases = load_injecagent_cases(case_file, limit=args.per_split, seed=args.seed)
        out_file = out_dir / f"test_cases_{split}_{args.setting}.jsonl"

        def progress(result, case, split=split):
            calls = [c["name"] for c in serialize_calls(result.tool_calls)]
            print(f"{result.eval:>7} | {split} | {case.user_tool} -> {calls[:2]}")

        split_summary, _ = run_cases(
            cases, llm, tool_dict, policy_factory=policy_factory, jsonl_path=out_file, progress=progress
        )
        summary["splits"][split] = split_summary

    trace.close()

    dh, ds = summary["splits"]["dh"], summary["splits"]["ds"]
    total_decided = (
        dh["counts"]["succ"] + dh["counts"]["unsucc"] + ds["counts"]["succ"] + ds["counts"]["unsucc"]
    )
    total_succ = dh["counts"]["succ"] + ds["counts"]["succ"]
    summary["asr_valid_first_step"] = round(100.0 * total_succ / total_decided, 1) if total_decided else None
    summary["embedding"] = backend.metadata

    summary_file = out_dir / f"summary_{args.setting}.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {summary_file}")


if __name__ == "__main__":
    main()
