"""E31 exact-call comparison and same-proposal semantic-only replay of frozen traces."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
Row = dict[str, Any]
CallKey = tuple[str, str, str]

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


def load(path: Path) -> list[Row]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def key(row: Row) -> CallKey:
    call = row.get("tool_call") or {}
    return (str(row.get("case_id", "")), str(call.get("name", "")),
            canonical(call.get("parameters", {})))


def load_meta(root: Path) -> dict[str, Row]:
    meta: dict[str, Row] = {}
    for path in sorted((root / "data/raw/InjecAgent/data").glob("test_cases_*.json")):
        split = "dh" if "_dh_" in path.name else "ds"
        setting = "enhanced" if "enhanced" in path.name else "base"
        for index, raw in enumerate(json.loads(path.read_text(encoding="utf-8"))):
            meta[f"{split}_{setting}_{index:04d}"] = {
                "user_tool": raw.get("User Tool", ""),
                "attacker_tools": raw.get("Attacker Tools") or [],
            }
    path = root / "data/raw/mcptox/response_all.json"
    if path.exists():
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        for server, value in (snapshot.get("servers") or {}).items():
            for index, raw in enumerate(value.get("malicious_instance") or []):
                match = re.search(r"^Tool:\s*(\S+)", raw.get("poisoned_tool", ""), re.M)
                if match:
                    meta[f"{server}_{index:03d}"] = {"attacker_tools": [match.group(1)]}
    return meta


def role(row: Row, meta: dict[str, Row]) -> str:
    info = meta.get(str(row.get("case_id", "")))
    if info is None:
        return "unknown"
    name = (row.get("tool_call") or {}).get("name")
    if name in info.get("attacker_tools", []):
        return "attacker_tool"
    if name and name == info.get("user_tool"):
        return "designated_user_tool"
    return "other_tool"


def outcome(full_allows: bool, semantic_allows: bool) -> str:
    if full_allows:
        return "both_allow" if semantic_allows else "semantic_prevents_full_allows"
    return "full_prevents_semantic_allows" if semantic_allows else "both_prevent"


def prevents(gate: Row) -> bool:
    decision = gate.get("decision")
    if decision not in {"allow", "block", "escalate"}:
        raise ValueError(f"Unknown recorded decision: {decision!r}")
    return decision != "allow"


def p95(values: list[float]) -> float | None:
    return round(sorted(values)[math.ceil(0.95 * len(values)) - 1], 4) if values else None


def configurations(rows: list[Row]) -> list[Row]:
    unique: dict[str, Row] = {}
    for row in rows:
        run = row.get("run") or {}
        config = {
            "agent_model_id": run.get("model_id"),
            "parser_backend": row.get("parser_backend"),
            "embedding": row.get("embedding") or run.get("embedding"),
            "tau": run.get("tau"), "delta": run.get("delta"), "alpha": run.get("alpha"),
        }
        unique[canonical(config)] = config
    return [unique[k] for k in sorted(unique)]


def compare(ours: list[Row], semantic: list[Row], meta: dict[str, Row]) -> Row:
    by_key: dict[CallKey, deque[Row]] = defaultdict(deque)
    for row in semantic:
        by_key[key(row)].append(row)
    matched: Counter[str] = Counter()
    replay: Counter[str] = Counter()
    matched_roles: dict[str, Counter[str]] = defaultdict(Counter)
    replay_roles: dict[str, Counter[str]] = defaultdict(Counter)
    replay_risks: dict[str, Counter[str]] = defaultdict(Counter)
    contract_identical = 0
    critical_veto = 0
    critical_veto_semantic_allows = 0
    replay_escalations = 0
    ours_latency: list[float] = []
    semantic_latency: list[float] = []
    for row in ours:
        gate = row["gate"]
        tau = float((row.get("run") or {}).get("tau", 0.75))
        sem_score = float(gate["S_sem"])
        full_allows = not prevents(gate)
        semantic_allows = sem_score >= tau
        which = role(row, meta)
        result = outcome(full_allows, semantic_allows)
        replay[result] += 1
        replay_roles[which][result] += 1
        replay_risks[str(row.get("risk") or "unknown")][result] += 1
        if gate.get("rule_triggered") is True and gate.get("S_rule") == 0:
            critical_veto += 1
            critical_veto_semantic_allows += int(semantic_allows)
        replay_escalations += int(gate["decision"] == "escalate")
        if gate.get("latency_ms") is not None:
            ours_latency.append(float(gate["latency_ms"]))
        if by_key[key(row)]:
            other = by_key[key(row)].popleft()
            other_gate = other["gate"]
            matched_result = outcome(full_allows, not prevents(other_gate))
            matched[matched_result] += 1
            matched_roles[which][matched_result] += 1
            contract_identical += int(canonical(row.get("contract")) ==
                                      canonical(other.get("contract")))
    for row in semantic:
        latency = row["gate"].get("latency_ms")
        if latency is not None:
            semantic_latency.append(float(latency))
    matched_count = matched.total()
    return {
        "full_trace_calls": len(ours),
        "semantic_trace_calls": len(semantic),
        "recorded_configurations": {
            "full": configurations(ours), "semantic_only": configurations(semantic),
        },
        "exact_call_comparison": {
            "matched_calls": matched_count,
            "unmatched_full_calls": len(ours) - matched_count,
            "unmatched_semantic_calls": len(semantic) - matched_count,
            "identical_contract_calls": contract_identical,
            "outcomes": dict(matched),
            "by_tool_role": {k: dict(v) for k, v in sorted(matched_roles.items())},
        },
        "same_proposal_replay": {
            "calls": replay.total(),
            "outcomes": dict(replay),
            "by_tool_role": {k: dict(v) for k, v in sorted(replay_roles.items())},
            "by_risk": {k: dict(v) for k, v in sorted(replay_risks.items())},
            "critical_veto_calls": critical_veto,
            "critical_veto_semantic_would_allow": critical_veto_semantic_allows,
            "full_escalations": replay_escalations,
        },
        "observed_per_call_p95_ms": {
            "full": p95(ours_latency), "semantic_only": p95(semantic_latency),
        },
    }


def aggregate(pairs: dict[str, Row]) -> Row:
    matched: Counter[str] = Counter()
    replay: Counter[str] = Counter()
    replay_roles: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    for pair in pairs.values():
        exact = pair["exact_call_comparison"]
        same = pair["same_proposal_replay"]
        matched.update(exact["outcomes"])
        replay.update(same["outcomes"])
        for which, counts in same["by_tool_role"].items():
            replay_roles[which].update(counts)
        for field in ("matched_calls", "unmatched_full_calls", "unmatched_semantic_calls",
                      "identical_contract_calls"):
            totals[field] += exact[field]
        for field in ("calls", "critical_veto_calls", "critical_veto_semantic_would_allow",
                      "full_escalations"):
            totals[field] += same[field]
    return {
        **dict(totals),
        "exact_call_outcomes": dict(matched),
        "same_proposal_outcomes": dict(replay),
        "same_proposal_by_tool_role": {k: dict(v) for k, v in sorted(replay_roles.items())},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "results/phase7/e31_contract_vs_semantic/"
                                       "e31_corrected_report.json")
    args = parser.parse_args()
    meta = load_meta(ROOT)
    pairs: dict[str, Row] = {}
    source_hashes: dict[str, str] = {}
    sources = [ROOT / "configs/benchmark_versions.yaml", Path(__file__)]
    sources.extend(sorted((ROOT / "data/raw/InjecAgent/data").glob("test_cases_*.json")))
    for label, ours_name, semantic_name in PAIRS:
        ours_path = ROOT / "results/phase5" / ours_name
        semantic_path = ROOT / "results/phase5" / semantic_name
        pairs[label] = compare(load(ours_path), load(semantic_path), meta)
        sources.extend([ours_path, semantic_path])
    snapshot = ROOT / "data/raw/mcptox/response_all.json"
    if snapshot.exists():
        sources.append(snapshot)
    for source in sources:
        source_hashes[source.relative_to(ROOT).as_posix()] = hashlib.sha256(
            source.read_bytes()).hexdigest()
    report = {
        "experiment": "E31 corrected offline comparison",
        "supersedes_analysis": "e31_report.json (original preserved)",
        "seed": 42,
        "source_sha256": source_hashes,
        "benchmark_pins": {
            "InjecAgent": "f19c9f2c79a41046eb13c03c51a24c567a8ffa07",
            "MCPTox": "static snapshot downloaded 2026-09-11",
        },
        "method": {
            "match": "case_id, tool name, canonical JSON parameters; occurrence-preserving",
            "replay": "Full recorded proposals and contracts; S_sem >= recorded tau is A1",
            "execution": "No tools executed and no LLM calls; escalate prevents execution",
            "labels": "Tool-role proxies from available pinned metadata; no argument labels",
            "limitations": [
                "Exact matches across independent runs may still have different contracts",
                "Repeated exact calls are paired in trace order",
                "Designated user-tool calls are not proof of benign arguments",
                "Replay estimates call-level decisions, not end-to-end task ASR or FPR",
                "Missing MCPTox snapshot metadata yields unknown tool roles",
                "Observed latency excludes parser and first contract embedding costs",
            ],
        },
        "pairs": pairs,
        "aggregate": aggregate(pairs),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["aggregate"], indent=2))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
