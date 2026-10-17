"""E31: contract-vs-semantic contribution (supervisor Q5), offline on cached Phase 5 traces.

Compares Ours (contract + rule veto + escalate) vs A1 (semantic-only ablation) on cached
Phase 5 traces, no LLM calls:
  (a) per-category/per-risk outcome flips — ours blocks/escalates where A1 allows, and vice versa
  (b) escalate-band ablation — calls where S_rule veto fires but S_sem alone would allow
  (c) cost/latency parity — contract parse once per session, per-call latency comparison
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PAIRS = [
    ("mcptox", "ours_mcptox_trace.jsonl", "a1_semantic_only_mcptox_trace.jsonl"),
    ("dh_base", "ours_test_cases_dh_base_trace.jsonl",
     "a1_semantic_only_test_cases_dh_base_trace.jsonl"),
    ("dh_enhanced", "ours_test_cases_dh_enhanced_trace.jsonl",
     "a1_semantic_only_test_cases_dh_enhanced_trace.jsonl"),
    ("ds_base", "ours_test_cases_ds_base_trace.jsonl",
     "a1_semantic_only_test_cases_ds_base_trace.jsonl"),
    ("ds_enhanced", "ours_test_cases_ds_enhanced_trace.jsonl",
     "a1_semantic_only_test_cases_ds_enhanced_trace.jsonl"),
]


def load(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def key(r):
    tc = r.get("tool_call") or {}
    return (r.get("case_id"), tc.get("name"))


def main():
    out_dir = ROOT / "results/phase7/e31_contract_vs_semantic"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {"pairs": {}, "aggregate": {}}

    for label, ours_file, a1_file in PAIRS:
        ours_path = ROOT / "results/phase5" / ours_file
        a1_path = ROOT / "results/phase5" / a1_file
        ours = load(ours_path)
        a1 = load(a1_path)
        a1_by_key = {key(r): r for r in a1}

        stats = defaultdict(int)
        total = 0
        risk_flips = defaultdict(lambda: {"ours_block_a1_allow": 0, "a1_block_ours_allow": 0, "total": 0})
        ours_lat, a1_lat = [], []
        veto_saves = 0

        for r in ours:
            k = key(r)
            total += 1
            g = r.get("gate") or {}
            dec = g.get("decision")
            s_sem = g.get("S_sem")
            s_rule = g.get("S_rule")
            risk = r.get("risk") or "unknown"
            risk_flips[risk]["total"] += 1
            lat = g.get("latency_ms")
            if lat is not None:
                ours_lat.append(lat)

            if k in a1_by_key:
                ag = a1_by_key[k].get("gate") or {}
                a1_dec = ag.get("decision")
                a1_lat_ms = ag.get("latency_ms")
                if a1_lat_ms is not None:
                    a1_lat.append(a1_lat_ms)

                ours_block = dec in ("block", "escalate")
                a1_block = a1_dec in ("block", "escalate")
                if ours_block and not a1_block:
                    stats["ours_block_a1_allow"] += 1
                    risk_flips[risk]["ours_block_a1_allow"] += 1
                elif a1_block and not ours_block:
                    stats["a1_block_ours_allow"] += 1
                    risk_flips[risk]["a1_block_ours_allow"] += 1
                elif ours_block and a1_block:
                    stats["ours_block_a1_block"] += 1
                else:
                    stats["both_allow"] += 1

                if s_rule == 1 and (s_sem is not None) and s_sem >= 0.75:
                    veto_saves += 1
                    stats["veto_saves"] += 1

        def p95(lst):
            if not lst:
                return None
            return round(sorted(lst)[int(0.95 * len(lst)) - 1], 2)

        report["pairs"][label] = {
            "total": total,
            "stats": dict(stats),
            "veto_saves": veto_saves,
            "risk_flips": {rk: dict(rv) for rk, rv in risk_flips.items()},
            "ours_p95_latency_ms": p95(ours_lat),
            "a1_p95_latency_ms": p95(a1_lat),
        }

    # aggregate
    agg = defaultdict(int)
    for v in report["pairs"].values():
        for kk, vv in v["stats"].items():
            agg[kk] += vv
        agg["total"] += v["total"]
        agg["veto_saves"] += v["veto_saves"]
    report["aggregate"] = dict(agg)

    report_file = out_dir / "e31_report.json"
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    A = report["aggregate"]
    print("E31 contract-vs-semantic (aggregate over all Phase 5 cached traces):")
    print(f"  total compared calls: {A['total']}")
    print(f"  ours blocks/escalates where A1 allows: {A['ours_block_a1_allow']}")
    print(f"  A1 blocks/escalates where ours allows: {A['a1_block_ours_allow']}")
    print(f"  both block/escalate: {A['ours_block_a1_block']}")
    print(f"  both allow: {A['both_allow']}")
    print(f"  rule-veto saves (S_rule=1 but S_sem>=0.75, semantic alone would allow): {A['veto_saves']}")
    print(f"  -> contract+rule adds value on {A['ours_block_a1_allow'] + A['veto_saves']} calls semantic-only misses")
    print(f"  wrote {report_file}")


if __name__ == "__main__":
    main()
