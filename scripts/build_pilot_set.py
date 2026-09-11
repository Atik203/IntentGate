"""Build the Gate 0 pilot set: 25 InjecAgent cases -> 25 hijack + 25 legit labeled calls
(blueprint Sec 13 step 4).

Hijack calls are constructed from the benchmark's attacker tool + parameters extracted
from the attacker instruction; legit calls use the case's user tool + its real parameters.
Documented as constructed calls (`docs/experiments/gate0_pilot.md`).

Usage: python scripts/build_pilot_set.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def extract_attacker_params(case) -> dict:
    text = case.attacker_instruction or ""
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    amount = re.search(r"\$\s?([\d,]+(?:\.\d+)?)", text) or re.search(
        r"([\d,]+)\s?(?:dollars|usd)", text, re.I
    )
    account = re.search(r"account\s*(?:number\s*)?[:#]?\s*([\w-]+)", text, re.I)
    name = (case.attacker_tools[0] if case.attacker_tools else "").lower()
    params: dict = {}
    if any(k in name for k in ("transfer", "withdraw", "purchase", "pay")):
        if amount:
            params["amount"] = float(amount.group(1).replace(",", ""))
        if account:
            params["to"] = account.group(1)
        elif email:
            params["to"] = email.group(0)
    elif any(k in name for k in ("send", "email", "post", "message", "share")):
        if email:
            params["to"] = email.group(0)
        params["content"] = text[:160]
    else:
        params["query"] = text[:160]
    return params


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dh", type=int, default=13, help="direct-harm cases")
    ap.add_argument("--ds", type=int, default=12, help="data-stealing cases")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--setting", default="base")
    ap.add_argument("--out", default="results/pilot_set.json")
    args = ap.parse_args()

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from harness.adapters.injecagent import load_injecagent_cases
    from intent_gate.parser.parser import build_parser
    from intent_gate.types import ToolCall

    parser = build_parser()
    data_dir = ROOT / "data" / "raw" / "InjecAgent" / "data"
    rows = []
    for split, limit in (("dh", args.dh), ("ds", args.ds)):
        cases = load_injecagent_cases(
            data_dir / f"test_cases_{split}_{args.setting}.json", limit=limit, seed=args.seed
        )
        for case in cases:
            contract = parser.parse(case.user_instruction)
            if not case.attacker_tools:
                continue
            hijack = ToolCall(
                name=case.attacker_tools[0], parameters=extract_attacker_params(case), source="injected"
            )
            legit = ToolCall(name=case.user_tool, parameters=case.tool_parameters, source="user")
            for label, call, source in ((1, hijack, "attacker"), (0, legit, "user")):
                rows.append(
                    {
                        "case_id": case.case_id,
                        "split": split,
                        "contract": contract.to_dict(),
                        "parser_backend": parser.last_backend,
                        "call": {
                            "name": call.name,
                            "parameters": call.parameters,
                            "naturalized": call.naturalized(),
                        },
                        "label": label,
                        "source": source,
                        "attacker_instruction": case.attacker_instruction,
                        "user_instruction": case.user_instruction,
                    }
                )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    n_h = sum(1 for r in rows if r["label"] == 1)
    n_l = sum(1 for r in rows if r["label"] == 0)
    print(f"wrote {out_path}: {n_h} hijack + {n_l} legit = {len(rows)} labeled calls")
    backends: dict = {}
    for row in rows:
        backends[row["parser_backend"]] = backends.get(row["parser_backend"], 0) + 1
    print("parser backends:", backends)


if __name__ == "__main__":
    main()
