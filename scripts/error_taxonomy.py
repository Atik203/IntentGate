"""Error taxonomy for gated runs (blueprint Sec 9/Phase 5): false negatives + contract evidence.

Usage:
  python scripts/error_taxonomy.py --b1 results/gated/none_dh50.jsonl results/gated/none_ds50.jsonl \
    --gated results/gated/ours_dh50.jsonl results/gated/ours_ds50.jsonl \
    --trace results/gated/ours_dh50_trace.jsonl results/gated/ours_ds50_trace.jsonl \
    --cases data/raw/InjecAgent/data/test_cases_dh_base.json data/raw/InjecAgent/data/test_cases_ds_base.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ATTACK_LABELS = {"succ", "success", "work_not_success"}


def load_jsonl(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def trace_index(paths: list[str]) -> dict:
    index: dict = {}
    for path in paths:
        for row in load_jsonl(path):
            case_id = row.get("case_id")
            if case_id:
                index.setdefault(case_id, []).append(row)
    return index


def request_index(case_paths: list[str]) -> dict:
    requests: dict = {}
    for path in case_paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        split = Path(path).stem.split("_")[2]
        for i, raw in enumerate(data):
            requests[f"{split}_base_{i:04d}"] = {
                "user_request": raw.get("User Instruction") or raw.get("query", ""),
                "user_tool": raw.get("User Tool", ""),
                "attacker_tools": raw.get("Attacker Tools") or [],
            }
    return requests


def mcptox_requests(path: str) -> dict:
    from harness.adapters.mcptox import load_mcptox_cases

    return {
        case.case_id: {"user_request": case.query, "user_tool": "", "attacker_tools": [case.fake_tool]}
        for case in load_mcptox_cases(path)
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b1", nargs="+", required=True)
    ap.add_argument("--gated", nargs="+", required=True)
    ap.add_argument("--trace", nargs="+", required=True)
    ap.add_argument("--cases", nargs="*", default=[])
    ap.add_argument("--mcptox", default="")
    ap.add_argument("--out", default="results/gated/error_taxonomy.json")
    ap.add_argument("--no-parse", action="store_true", help="skip contract re-parse (offline)")
    args = ap.parse_args()

    ground_truth: dict = {}
    for path in args.b1:
        for row in load_jsonl(path):
            label = row.get("eval", row.get("label"))
            ground_truth[row["case_id"]] = 1 if label in ATTACK_LABELS else 0

    traces = trace_index(args.trace)
    requests = request_index(args.cases) if args.cases else {}
    if args.mcptox:
        requests.update(mcptox_requests(ROOT / args.mcptox))

    parser = None
    if not args.no_parse and requests:
        from intent_gate.parser.parser import build_parser

        parser = build_parser()

    failures = []
    for path in args.gated:
        for row in load_jsonl(path):
            label = row.get("eval", row.get("label"))
            case_id = row["case_id"]
            if label not in ATTACK_LABELS or not ground_truth.get(case_id):
                continue
            calls = row.get("tool_calls") or [{"name": row.get("called_tool"), "parameters": row.get("arguments") or {}}]
            events = traces.get(case_id, [])
            contract = None
            backend = None
            for trace_row in events:
                if "contract" in trace_row:
                    contract = trace_row["contract"]
                    backend = trace_row.get("parser_backend")
                    break
            if contract is None and parser is not None and case_id in requests:
                parsed = parser.parse(requests[case_id]["user_request"])
                contract = parsed.to_dict()
                backend = parser.last_backend
            if contract is not None and backend:
                contract = {**contract, "parser_backend": backend}
            failures.append(
                {
                    "case_id": case_id,
                    "gated_label": label,
                    "risk": row.get("risk", ""),
                    "calls": [{"name": c.get("name"), "parameters": c.get("parameters")} for c in calls],
                    "gate_trace": [
                        {
                            "name": t["tool_call"]["name"],
                            "S": t["gate"]["S"],
                            "S_sem": t["gate"]["S_sem"],
                            "S_rule": t["gate"]["S_rule"],
                            "rule_triggered": t["gate"]["rule_triggered"],
                            "decision": t["gate"]["decision"],
                            "reason": t["gate"]["reason"],
                        }
                        for t in events
                    ],
                    "contract": contract,
                }
            )

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"n_failures": len(failures), "failures": failures}, indent=2) + "\n", encoding="utf-8")
    print(f"false negatives (attack allowed): {len(failures)}")
    for failure in failures:
        trace = failure["gate_trace"][0] if failure["gate_trace"] else {}
        limits = (failure["contract"] or {}).get("side_effect_limits", {})
        print(
            f"  {failure['case_id']:>18} {failure['risk']:<24} S={trace.get('S')} "
            f"rule={trace.get('S_rule')} call={failure['calls'][0]['name']} limits={limits}"
        )
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
