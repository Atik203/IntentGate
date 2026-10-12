"""E21 — Escalate precision analysis (Phase 6 P1).

Extracts all escalated tool calls from Phase 5 traces, classifies each using
ground truth (attacker tool vs user tool, MCPTox label), and reports
escalate precision: of escalated calls, what fraction were attacker calls
that the gate correctly flagged vs user calls that were falsely escalated.

All offline: reads cached trace JSONL + case meta, no LLM calls.

Usage:
  python scripts/e21_escalate_precision.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from intent_gate.scoring.rules import tool_category


def load_meta() -> dict[str, dict]:
    """Load case metadata: user_tool, attacker_tools, label, risk, etc."""
    meta: dict = {}

    # InjecAgent
    base = ROOT / "data/raw/InjecAgent/data"
    for path in sorted(base.glob("test_cases_*.json")):
        split = "dh" if "_dh_" in path.name else "ds"
        setting = "enhanced" if "enhanced" in path.name else "base"
        for index, raw in enumerate(json.loads(path.read_text(encoding="utf-8"))):
            case_id = f"{split}_{setting}_{index:04d}"
            attacker_tools = raw.get("Attacker Tools") or []
            meta[case_id] = {
                "benchmark": "injecagent",
                "split": split,
                "setting": setting,
                "user_tool": raw.get("User Tool", ""),
                "attacker_tools": attacker_tools,
                "attack_type": raw.get("Attack Type", ""),
                "risk": "",
            }

    # MCPTox
    from harness.adapters.mcptox import load_mcptox_cases
    for case in load_mcptox_cases(ROOT / "data/raw/mcptox/response_all.json"):
        meta[case.case_id] = {
            "benchmark": "mcptox",
            "split": "snapshot",
            "setting": "static",
            "user_tool": "",
            "attacker_tools": [case.fake_tool],
            "attack_type": case.paradigm,
            "risk": case.risk,
        }
    return meta


def extract_trace_escalated(trace_files: list[str], source: str) -> list[dict]:
    """Extract all gate events with decision == 'escalate' or would_escalate == true."""
    results = []
    for tf in trace_files:
        path = ROOT / tf
        if not path.exists():
            print(f"  WARNING: {tf} not found")
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                gate = row.get("gate", {})
                if not isinstance(gate, dict):
                    continue
                decision = gate.get("decision")
                would_escalate = gate.get("would_escalate", False)
                if decision != "escalate" and not would_escalate:
                    continue
                tool_name = row.get("tool_call", {}).get("name", "")
                results.append({
                    "source": source,
                    "case_id": row.get("case_id", ""),
                    "tool": tool_name,
                    "S": gate.get("S"),
                    "S_sem": gate.get("S_sem"),
                    "S_rule": gate.get("S_rule"),
                    "rule_triggered": gate.get("rule_triggered", False),
                    "reason": gate.get("reason", ""),
                    "latency_ms": gate.get("latency_ms"),
                    "raw_request": row.get("contract", {}).get("raw_request", ""),
                    "side_effect_limits": row.get("contract", {}).get("side_effect_limits", {}),
                    "risk": row.get("risk", ""),
                    "label": row.get("label", ""),
                    "split": row.get("split", ""),
                    "setting": row.get("setting", ""),
                })
    return results


def classify_escalated(tool_name: str, meta: dict) -> str:
    """Classify an escalated call using ground truth.

    - 'attacker_tool': the escalated tool is in the case's attacker_tools list
      -> gate correctly flagged an attack (true positive escalate)
    - 'user_tool': the escalated tool is the user_tool
      -> gate falsely escalated a legitimate user call (false positive escalate)
    - 'other_tool': neither attacker nor user tool (e.g., intermediate call)
      -> ambiguous; check if tool category is high-risk
    """
    attacker_tools = meta.get("attacker_tools", [])
    user_tool = meta.get("user_tool", "")

    if tool_name in attacker_tools:
        return "attacker_tool"
    if tool_name == user_tool:
        return "user_tool"
    # Other: check if high-risk category
    cat = tool_category(tool_name)
    if cat in ("financial", "code", "file", "system"):
        return "high_risk_other"
    return "other_tool"


def main():
    print("=== E21 — Escalate Precision Analysis (Ground-Truth) ===\n")

    meta = load_meta()
    print(f"Loaded meta for {len(meta)} cases")

    # InjecAgent trace files
    injecagent_traces = [
        "results/phase5/ours_test_cases_dh_base_trace.jsonl",
        "results/phase5/ours_test_cases_dh_enhanced_trace.jsonl",
        "results/phase5/ours_test_cases_ds_base_trace.jsonl",
        "results/phase5/ours_test_cases_ds_enhanced_trace.jsonl",
    ]
    mcptox_traces = ["results/phase5/ours_mcptox_trace.jsonl"]

    injecagent_escalated = extract_trace_escalated(injecagent_traces, "injecagent")
    mcptox_escalated = extract_trace_escalated(mcptox_traces, "mcptox")

    all_escalated = injecagent_escalated + mcptox_escalated
    print(f"\nTotal escalated tool calls: {len(all_escalated)}")
    print(f"  InjecAgent: {len(injecagent_escalated)}")
    print(f"  MCPTox: {len(mcptox_escalated)}")

    # Classify each using ground truth
    classifications = Counter()
    by_source = {"injecagent": Counter(), "mcptox": Counter()}
    by_split_setting = defaultdict(Counter)

    for case in all_escalated:
        m = meta.get(case["case_id"], {})
        label = classify_escalated(case["tool"], m)
        case["classification"] = label
        case["tool_category"] = tool_category(case["tool"])
        case["is_attacker_tool"] = (label == "attacker_tool")
        case["is_user_tool"] = (label == "user_tool")
        classifications[label] += 1
        by_source[case["source"]][label] += 1
        by_split_setting[f"{m.get('split','')}:{m.get('setting','')}"][label] += 1

    print(f"\n=== Classification (Ground Truth) ===")
    for label, count in classifications.most_common():
        pct = count / len(all_escalated) * 100 if all_escalated else 0
        print(f"  {label}: {count} ({pct:.1f}%)")

    print(f"\n=== By source ===")
    for src in ("injecagent", "mcptox"):
        total = sum(by_source[src].values())
        print(f"  {src} ({total} escalated calls):")
        for label, count in by_source[src].most_common():
            pct = count / total * 100 if total else 0
            print(f"    {label}: {count} ({pct:.1f}%)")

    # MCPTox risk distribution
    risk_dist = Counter(c["risk"] for c in mcptox_escalated)
    print(f"\n=== MCPTox risk distribution in escalated ===")
    for risk, count in risk_dist.most_common():
        print(f"  {risk}: {count}")

    # Sample attacker_tool escalations (gate correctly caught attack)
    attacker_esc = [c for c in all_escalated if c["classification"] == "attacker_tool"]
    print(f"\n=== Sample attacker_tool escalations (gate caught attack) ===")
    for c in attacker_esc[:10]:
        print(f"  [{c['source']}] {c['case_id']} | {c['tool']} | "
              f"S={c['S']:.2f} S_sem={c['S_sem']:.2f} | intent: {c['raw_request'][:80]}")

    # Sample user_tool escalations (gate falsely escalated legitimate call)
    user_esc = [c for c in all_escalated if c["classification"] == "user_tool"]
    print(f"\n=== Sample user_tool escalations (false escalate) ===")
    for c in user_esc[:10]:
        print(f"  [{c['source']}] {c['case_id']} | {c['tool']} | "
              f"S={c['S']:.2f} S_sem={c['S_sem']:.2f} | intent: {c['raw_request'][:80]}")

    # Sample high_risk_other
    high_risk = [c for c in all_escalated if c["classification"] == "high_risk_other"]
    print(f"\n=== Sample high_risk_other escalations ===")
    for c in high_risk[:10]:
        print(f"  [{c['source']}] {c['case_id']} | {c['tool']} | cat={c['tool_category']} | "
              f"S={c['S']:.2f} | intent: {c['raw_request'][:80]}")

    # Escalate precision metrics
    tp = classifications["attacker_tool"]
    fp = classifications["user_tool"]
    other = classifications["high_risk_other"] + classifications["other_tool"]
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    print(f"\n=== Escalate Precision (ground truth) ===")
    print(f"  True positives (attacker tool escalated): {tp}")
    print(f"  False positives (user tool escalated): {fp}")
    print(f"  Other (high-risk/other): {other}")
    print(f"  Escalate precision (TP / (TP+FP)): {precision:.1%}")
    print(f"  False escalate rate (FP / total): {fp / len(all_escalated):.1%}")

    out_path = ROOT / "results/phase6/e21_escalate_precision.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "n_escalated_calls": len(all_escalated),
        "by_source": {k: dict(v) for k, v in by_source.items()},
        "by_split_setting": {k: dict(v) for k, v in by_split_setting.items()},
        "classifications": dict(classifications),
        "risk_distribution_mcptox": dict(risk_dist),
        "escalate_precision": round(precision, 4),
        "false_escalate_rate": round(fp / len(all_escalated), 4) if all_escalated else 0,
        "sample_attacker_tool": [
            {k: v for k, v in c.items() if k not in ("contract_goals", "side_effect_limits")}
            for c in attacker_esc[:20]
        ],
        "sample_user_tool": [
            {k: v for k, v in c.items() if k not in ("contract_goals", "side_effect_limits")}
            for c in user_esc[:20]
        ],
    }, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()