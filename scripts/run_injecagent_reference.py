"""Run InjecAgent's own prompted-agent pipeline on a deterministic subset (S3a reference).

Uses their prompts, output parsing, and simulated responses via sys.path, without
modifying the gitignored clone. First-step only (step 2 for DS runs in the full
baseline later); results are for harness-trust, not publication.

Usage:
  python scripts/run_injecagent_reference.py --per-split 10 --setting base
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INJEC_ROOT = ROOT / "data" / "raw" / "InjecAgent"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-split", type=int, default=10, help="cases per split (dh/ds)")
    ap.add_argument("--setting", choices=["base", "enhanced"], default="base")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--model-name",
        default=None,
        help="OpenAI model id; defaults to AGENT_MODEL_ID from .env",
    )
    ap.add_argument("--prompt-type", default="InjecAgent")
    ap.add_argument("--out", default="results/injecagent_reference")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    model_name = args.model_name or os.getenv("AGENT_MODEL_ID", "gpt-4o-mini")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY missing in .env")
    if not INJEC_ROOT.exists():
        raise SystemExit(f"InjecAgent clone missing at {INJEC_ROOT}")

    out_dir = (ROOT / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(INJEC_ROOT))
    os.chdir(INJEC_ROOT)

    import types

    try:  # their models.py imports together at module level; unused for GPT runs
        import together  # noqa: F401
    except ImportError:
        sys.modules["together"] = types.ModuleType("together")

    from src.models import MODELS
    from src.output_parsing import evaluate_output_prompted
    from src.prompts.agent_prompts import PROMPT_DICT
    from src.utils import get_tool_dict

    model_class = MODELS["GPT"]({"model_name": model_name})
    system_prompt, user_prompt = PROMPT_DICT[args.prompt_type]
    tool_dict = get_tool_dict()

    def predict_one_case(item):
        available = [item["User Tool"]] + item["Attacker Tools"]
        descriptions = json.dumps([tool_dict[t] for t in available], indent=True)
        scratchpad = (
            f"\n{item['Thought']}\nAction: {item['User Tool']}\n"
            f"Action Input: {item['Tool Parameters']}\nObservation: {item['Tool Response']}\n"
        )
        filled = user_prompt.format(
            available_tool_descriptions=descriptions,
            input=item["User Instruction"],
            available_tool_names=available,
            agent_scratchpad=scratchpad,
        )
        return model_class.call_model(model_class.prepare_input(system_prompt, filled))

    summary = {"model_name": model_name, "setting": args.setting, "splits": {}}
    for split in ["dh", "ds"]:
        case_file = INJEC_ROOT / "data" / f"test_cases_{split}_{args.setting}.json"
        data = json.loads(case_file.read_text(encoding="utf-8"))
        cases = random.Random(args.seed).sample(data, min(args.per_split, len(data)))
        out_file = out_dir / f"test_cases_{split}_{args.setting}.jsonl"
        counts = {"succ": 0, "unsucc": 0, "invalid": 0}
        with out_file.open("w", encoding="utf-8") as fh:
            for item in cases:
                try:
                    output = predict_one_case(item)
                    item["output"] = output
                    parsed = evaluate_output_prompted(
                        output,
                        item["Attacker Tools"][0],
                        item["Attacker Tools"],
                        item["User Tool"],
                        item["Attacker Instruction"],
                    )
                    item["eval"] = parsed["eval"]
                    if item["eval"] == "invalid":
                        item["invalid_reason"] = parsed.get("invalid_reason", "")
                    counts[item["eval"]] = counts.get(item["eval"], 0) + 1
                except Exception as exc:  # keep the reference run going
                    item["eval"] = "error"
                    item["error"] = str(exc)
                fh.write(json.dumps(item) + "\n")
                print(f"{item['eval']:>7} | {split} | {item['User Tool']} -> {item['Attacker Tools'][:1]}")

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
