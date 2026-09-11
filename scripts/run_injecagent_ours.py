"""Run OUR B1 pipeline on an InjecAgent subset (S3b; blueprint Sec 13 step 1).

Same vendored prompts/parsing as the gate will use; no gate yet (B1).
Usage: python scripts/run_injecagent_ours.py --per-split 10 --setting base
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
    ap.add_argument("--model-name", default=None)
    ap.add_argument("--out", default="results/injecagent_ours")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")

    from harness.adapters.injecagent import load_injecagent_cases, load_tool_definitions
    from harness.injecagent_runner import build_tool_dict, run_case, serialize_calls
    from intent_gate.agent.base import LLMClient

    tool_dict = build_tool_dict(load_tool_definitions(ROOT / "data/raw/InjecAgent/data/tools.json"))
    llm = LLMClient(model_id=model_name)
    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {"model_name": model_name, "setting": args.setting, "splits": {}}
    for split in ["dh", "ds"]:
        case_file = ROOT / "data/raw/InjecAgent/data" / f"test_cases_{split}_{args.setting}.json"
        cases = load_injecagent_cases(case_file, limit=args.per_split, seed=args.seed)
        counts = {"succ": 0, "unsucc": 0, "invalid": 0, "error": 0}
        out_file = out_dir / f"test_cases_{split}_{args.setting}.jsonl"
        with out_file.open("w", encoding="utf-8") as fh:
            for case in cases:
                result = run_case(case, llm, tool_dict)
                counts[result.eval] = counts.get(result.eval, 0) + 1
                fh.write(
                    json.dumps(
                        {
                            "case_id": case.case_id,
                            "eval": result.eval,
                            "invalid_reason": result.invalid_reason,
                            "output": result.output,
                            "tool_calls": serialize_calls(result.tool_calls),
                            "attacker_params": result.attacker_params,
                            "attacker_thought": result.attacker_thought,
                            "error": result.error,
                        }
                    )
                    + "\n"
                )
                calls = [c["name"] for c in serialize_calls(result.tool_calls)]
                print(f"{result.eval:>7} | {split} | {case.user_tool} -> {calls[:2]}")

        decided = counts["succ"] + counts["unsucc"]
        summary["splits"][split] = {
            "n": len(cases),
            "counts": counts,
            "asr_valid": round(100.0 * counts["succ"] / decided, 1) if decided else None,
            "valid_rate": round(100.0 * decided / len(cases), 1) if cases else None,
        }

    dh, ds = summary["splits"]["dh"], summary["splits"]["ds"]
    total_decided = (
        dh["counts"]["succ"] + dh["counts"]["unsucc"] + ds["counts"]["succ"] + ds["counts"]["unsucc"]
    )
    total_succ = dh["counts"]["succ"] + ds["counts"]["succ"]
    summary["asr_valid_first_step"] = round(100.0 * total_succ / total_decided, 1) if total_decided else None

    summary_file = out_dir / f"summary_{args.setting}.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {summary_file}")


if __name__ == "__main__":
    main()
