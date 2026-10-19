"""E26c - offline evaluation of the verbatim-echo guard.

Applies the guard to the 34 strict E26b adaptive call instances and to all user-tool
calls in the frozen Phase 5 traces. No model or tool calls.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from intent_gate.scoring.echo_guard import echo_guard
from intent_gate.types import IntentContract, ToolCall

TRACE_PAIRS = [("dh", "base"), ("dh", "enhanced"), ("ds", "base"), ("ds", "enhanced")]


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_contract(record: dict[str, Any]) -> IntentContract:
    contract = record.get("contract") or {}
    return IntentContract(
        goals=list(contract.get("goals") or []),
        expected_tool_categories=list(contract.get("expected_tool_categories") or []),
        permitted_data_access=list(contract.get("permitted_data_access") or []),
        side_effect_limits=dict(contract.get("side_effect_limits") or {}),
        specificity=contract.get("specificity", "specific"),
        raw_request=contract.get("raw_request", ""),
    )


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def load_context() -> tuple[dict[str, IntentContract], dict[str, str]]:
    from harness.adapters.injecagent import load_injecagent_cases

    contracts: dict[str, IntentContract] = {}
    user_tools: dict[str, str] = {}
    for split, setting in TRACE_PAIRS:
        case_path = ROOT / "data/raw/InjecAgent/data" / f"test_cases_{split}_{setting}.json"
        for case in load_injecagent_cases(case_path, limit=None):
            user_tools[case.case_id] = case.user_tool
        trace_path = ROOT / "results/phase5" / f"ours_test_cases_{split}_{setting}_trace.jsonl"
        for row in load_rows(trace_path):
            contracts[row["case_id"]] = build_contract(row)
    return contracts, user_tools


def adaptive_metrics(report: dict[str, Any], contracts: dict[str, IntentContract], min_tokens: int):
    total = 0
    blocked = 0
    templates: set[tuple[str, str]] = set()
    blocked_templates: set[tuple[str, str]] = set()
    examples: list[dict[str, Any]] = []
    for call in report.get("calls") or []:
        if not call.get("strict_variants"):
            continue
        total += 1
        template = (str(call["tool"]), canonical(call.get("original_parameters") or {}))
        templates.add(template)
        contract = contracts.get(str(call["case_id"]))
        if contract is None:
            continue
        hit = None
        for variant in call.get("variants") or []:
            if not str(variant.get("strategy", "")).startswith("free_"):
                continue
            tool_call = ToolCall(name=str(call["tool"]), parameters=dict(variant["parameters"]))
            result = echo_guard(contract, tool_call, min_tokens=min_tokens)
            if result["triggered"]:
                hit = {"strategy": variant["strategy"], "hits": result["hits"]}
                break
        if hit is not None:
            blocked += 1
            blocked_templates.add(template)
            if len(examples) < 5:
                examples.append({"case_id": call["case_id"], "tool": call["tool"], **hit})
    return {
        "calls": total,
        "blocked": blocked,
        "templates": len(templates),
        "blocked_templates": len(blocked_templates),
        "examples": examples,
    }


def legit_metrics(
    contracts: dict[str, IntentContract],
    user_tools: dict[str, str],
    min_tokens: int,
):
    total = allowed = blocked = blocked_allowed = 0
    examples: list[dict[str, Any]] = []
    for split, setting in TRACE_PAIRS:
        trace_path = ROOT / "results/phase5" / f"ours_test_cases_{split}_{setting}_trace.jsonl"
        for row in load_rows(trace_path):
            case_id = row["case_id"]
            if row["tool_call"]["name"] != user_tools.get(case_id):
                continue
            contract = contracts.get(case_id)
            if contract is None:
                continue
            total += 1
            call = ToolCall(name=row["tool_call"]["name"], parameters=dict(row["tool_call"].get("parameters") or {}))
            result = echo_guard(contract, call, min_tokens=min_tokens)
            if result["triggered"]:
                blocked += 1
            if row["gate"]["decision"] == "allow":
                allowed += 1
                if result["triggered"]:
                    blocked_allowed += 1
                    if len(examples) < 5:
                        examples.append({"case_id": case_id, "tool": call.name, **result})
    return {
        "user_calls": total,
        "user_calls_allowed": allowed,
        "guard_blocks": blocked,
        "new_blocks_among_allowed": blocked_allowed,
        "new_block_rate": round(blocked_allowed / allowed, 4) if allowed else 0.0,
        "examples": examples,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="results/phase7/e26_adaptive/offline/e26b_threshold_probe.json")
    ap.add_argument("--thresholds", default="6,8,10,12")
    ap.add_argument("--out", default="results/phase7/e26_adaptive/offline/e26c_echo_guard.json")
    args = ap.parse_args()

    report_path = ROOT / args.report
    e26b = json.loads(report_path.read_text(encoding="utf-8"))
    contracts, user_tools = load_context()
    rows = {}
    for value in [int(item) for item in args.thresholds.split(",") if item.strip()]:
        rows[str(value)] = {
            "adaptive": adaptive_metrics(e26b, contracts, value),
            "legitimate": legit_metrics(contracts, user_tools, value),
        }
    output = {
        "experiment": "E26c verbatim-echo guard",
        "method": "longest contiguous token span from request/goals/access in free-text arguments",
        "source": str(report_path.relative_to(ROOT)),
        "thresholds": rows,
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"{'K':>3} {'adaptive':>12} {'templates':>12} {'legit allowed':>14} {'new blocks':>11} {'rate':>7}")
    for k, row in rows.items():
        a, l = row["adaptive"], row["legitimate"]
        print(
            f"{k:>3} {a['blocked']:>4}/{a['calls']:<7} {a['blocked_templates']:>4}/{a['templates']:<7} "
            f"{l['user_calls_allowed']:>14} {l['new_blocks_among_allowed']:>11} "
            f"{l['new_block_rate']*100:>6.2f}%"
        )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
