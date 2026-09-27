"""Phase 5 reporter: headline tables, breakdowns, stats, Pareto, latency, utility, cost.

Usage:
  python scripts/report_phase5.py --dir results/phase5 --out results/phase5/report.json
  python scripts/report_phase5.py --dir results/gated --markdown results/phase5/report.md
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONDITION_ALIASES = {
    "none": "b1",
    "b1": "b1",
    "toolgate": "b2",
    "b2": "b2",
    "ours": "ours",
    "a1_semantic_only": "a1",
    "a2_rule_only": "a2",
    "a3_raw_request": "a3",
}
ATTACK_LABELS = {"succ", "success", "work_not_success"}


def parse_name(stem: str) -> tuple[str, str] | None:
    """'ours_test_cases_dh_base' -> ('ours', 'injecagent:dh:base'); aliases applied."""
    parts = stem.split("_")
    for size in (4, 3, 2, 1):
        candidate = "_".join(parts[:size])
        if candidate in CONDITION_ALIASES:
            condition = CONDITION_ALIASES[candidate]
            rest = "_".join(parts[size:])
            break
    else:
        return None
    if "mcptox" in stem:
        return condition, "mcptox"
    if "test_cases" in stem:
        split = next((p for p in parts if p in ("dh", "ds")), "?")
        setting = "enhanced" if "enhanced" in parts else "base"
        return condition, f"injecagent:{split}:{setting}"
    if rest:
        return condition, rest
    return None


def load_reports(directory: Path) -> dict[tuple[str, str], dict]:
    reports: dict[tuple[str, str], dict] = {}
    for path in sorted(directory.glob("*.json")):
        if path.name in {"manifest.json", "report.json", "pareto.json", "error_taxonomy.json"}:
            continue
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(report, dict) or "counts" not in report:
            continue
        parsed = parse_name(path.stem)
        if not parsed:
            continue
        report["_path"] = str(path)
        reports[parsed] = report
    return reports


def load_jsonl(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["case_id"]] = row
    return rows


def case_success(row: dict, benchmark: str) -> bool | None:
    if benchmark == "mcptox":
        label = row.get("label")
        return None if label is None else label in ATTACK_LABELS
    evaluation = row.get("eval")
    if evaluation is None:
        return None
    if evaluation == "error":
        return None
    return evaluation == "succ"


def success_label(row: dict, benchmark: str) -> bool | None:
    if benchmark == "mcptox":
        return row.get("label") == "success"
    return row.get("eval") == "succ"


def injecagent_meta() -> dict:
    meta: dict = {}
    base = ROOT / "data/raw/InjecAgent/data"
    for path in sorted(base.glob("test_cases_*.json")):
        split = "dh" if "_dh_" in path.name else "ds"
        setting = "enhanced" if "enhanced" in path.name else "base"
        for index, raw in enumerate(json.loads(path.read_text(encoding="utf-8"))):
            meta[f"{split}_{setting}_{index:04d}"] = {
                "benchmark": "injecagent",
                "split": split,
                "setting": setting,
                "user_tool": raw.get("User Tool", ""),
                "attacker_tool": (raw.get("Attacker Tools") or [""])[0],
                "attack_type": raw.get("Attack Type", ""),
                "risk": "",
            }
    return meta


def mcptox_meta() -> dict:
    from harness.adapters.mcptox import load_mcptox_cases

    meta: dict = {}
    for case in load_mcptox_cases(ROOT / "data/raw/mcptox/response_all.json"):
        meta[case.case_id] = {
            "benchmark": "mcptox",
            "split": "snapshot",
            "setting": "static",
            "user_tool": "",
            "attacker_tool": case.fake_tool,
            "attack_type": case.paradigm,
            "risk": case.risk,
        }
    return meta


def headline(reports: dict) -> list[dict]:
    rows = []
    for (condition, key), report in sorted(reports.items()):
        counts = report.get("counts", {})
        benchmark = "mcptox" if key == "mcptox" else "injecagent"
        if benchmark == "injecagent":
            decided = counts.get("succ", 0) + counts.get("unsucc", 0)
            rows.append(
                {
                    "condition": condition,
                    "benchmark": benchmark,
                    "slice": key,
                    "n": report.get("n"),
                    "succ": counts.get("succ", 0),
                    "asr_valid": report.get("asr_valid"),
                    "valid_rate": report.get("valid_rate"),
                    "blocked": report.get("gate_blocked"),
                    "cost_usd": report.get("estimated_cost_usd"),
                    "decided": decided,
                }
            )
        else:
            attack = counts.get("success", 0) + counts.get("work_not_success", 0)
            rows.append(
                {
                    "condition": condition,
                    "benchmark": benchmark,
                    "slice": key,
                    "n": report.get("n"),
                    "succ": counts.get("success", 0),
                    "attack_influenced": attack,
                    "blocked": counts.get("blocked", 0),
                    "ignored": counts.get("ignored", 0),
                    "cost_usd": report.get("estimated_cost_usd"),
                }
            )
    return rows


def print_headline(rows: list[dict]) -> None:
    print("== headline ==")
    for row in rows:
        if row["benchmark"] == "injecagent":
            print(
                f"  {row['condition']:<4} {row['slice']:<28} n={row['n']:<5} succ={row['succ']:<4} "
                f"ASR-valid={row['asr_valid']} valid={row['valid_rate']} blocked={row['blocked']} cost=${row['cost_usd']}"
            )
        else:
            print(
                f"  {row['condition']:<4} {row['slice']:<28} n={row['n']:<5} succ={row['succ']:<4} "
                f"attack-influenced={row['attack_influenced']:<4} blocked={row['blocked']:<4} "
                f"ignored={row['ignored']} cost=${row['cost_usd']}"
            )


def stats_for(directory: Path, reports: dict, benchmark: str) -> list[dict]:
    from intent_gate.eval.stats import bootstrap_ci, mcnemar

    b1 = None
    for (condition, key), report in reports.items():
        if condition == "b1" and ((benchmark == "mcptox") == (key == "mcptox")):
            b1 = report
    if b1 is None:
        return []
    b1_rows = load_jsonl(Path(b1["_path"]).with_suffix(".jsonl"))
    out = []
    for (condition, key), report in sorted(reports.items()):
        if condition == "b1" or ((benchmark == "mcptox") != (key == "mcptox")):
            continue
        other_rows = load_jsonl(Path(report["_path"]).with_suffix(".jsonl"))
        case_ids = [case_id for case_id in b1_rows if case_id in other_rows]
        if not case_ids:
            continue
        b1_flags = [success_label(b1_rows[cid], benchmark) for cid in case_ids]
        other_flags = [success_label(other_rows[cid], benchmark) for cid in case_ids]
        pair = [(a, b) for a, b in zip(b1_flags, other_flags) if a is not None and b is not None]
        if not pair:
            continue
        b1_bool = [a for a, _ in pair]
        other_bool = [b for _, b in pair]
        asr = sum(other_bool) / len(other_bool)
        lo, hi = bootstrap_ci([float(v) for v in other_bool])
        out.append(
            {
                "condition": condition,
                "slice": key,
                "n_pairs": len(pair),
                "asr": round(asr, 4),
                "asr_ci95": [round(lo, 4), round(hi, 4)],
                "b1_asr": round(sum(b1_bool) / len(b1_bool), 4),
                "mcnemar_vs_b1": mcnemar(b1_bool, other_bool),
            }
        )
    return out


def breakdown(directory: Path, reports: dict, meta: dict, benchmark: str, group_key: str) -> list[dict]:
    b1 = next((r for (c, k), r in reports.items() if c == "b1" and ((benchmark == "mcptox") == (k == "mcptox"))), None)
    ours = next((r for (c, k), r in reports.items() if c == "ours" and ((benchmark == "mcptox") == (k == "mcptox"))), None)
    if b1 is None or ours is None:
        return []
    b1_rows = load_jsonl(Path(b1["_path"]).with_suffix(".jsonl"))
    ours_rows = load_jsonl(Path(ours["_path"]).with_suffix(".jsonl"))
    groups: dict[str, dict] = {}
    for case_id, row in b1_rows.items():
        if case_id not in ours_rows or case_id not in meta:
            continue
        group = meta[case_id].get(group_key) or "unknown"
        entry = groups.setdefault(group, {"n": 0, "b1_succ": 0, "ours_succ": 0, "blocked": 0})
        entry["n"] += 1
        if success_label(row, benchmark):
            entry["b1_succ"] += 1
        if success_label(ours_rows[case_id], benchmark):
            entry["ours_succ"] += 1
        if ours_rows[case_id].get("gate_blocked"):
            entry["blocked"] += 1
    return [
        {
            "group": group,
            **values,
            "b1_asr": round(values["b1_succ"] / values["n"], 3) if values["n"] else None,
            "ours_asr": round(values["ours_succ"] / values["n"], 3) if values["n"] else None,
        }
        for group, values in sorted(groups.items(), key=lambda item: -item[1]["n"])
    ]


def pareto(directory: Path, reports: dict, tau_grid: list[float], delta_grid: list[float]) -> dict:
    from intent_gate.eval.sweep import load_trace, sweep_grid

    out: dict = {}
    for benchmark in ("injecagent", "mcptox"):
        trace_rows = []
        for (condition, key), report in reports.items():
            if condition != "ours":
                continue
            if (benchmark == "mcptox") != (key == "mcptox"):
                continue
            trace_path = Path(report["_path"]).with_name(Path(report["_path"]).stem + "_trace.jsonl")
            if trace_path.exists():
                trace_rows.extend(load_trace(trace_path))
        b1 = next((r for (c, k), r in reports.items() if c == "b1" and ((benchmark == "mcptox") == (k == "mcptox"))), None)
        if not trace_rows or b1 is None:
            continue
        truth = {}
        for case_id, row in load_jsonl(Path(b1["_path"]).with_suffix(".jsonl")).items():
            truth[case_id] = 1 if row.get("eval") == "succ" or row.get("label") == "success" else 0
        grid = sweep_grid(trace_rows, truth, tau_grid, delta_grid)
        out[benchmark] = [
            {
                "tau": tau,
                "delta": delta,
                "asr": round(cell["metrics"].asr, 4),
                "attacks": cell["metrics"].n_attacks,
                "escalate_share": round(cell["escalate_share"], 4),
            }
            for (tau, delta), cell in grid.items()
        ]
    return out


def latency(directory: Path, reports: dict) -> dict:
    out: dict = {}
    for (condition, key), report in sorted(reports.items()):
        if condition not in ("ours", "b2"):
            continue
        jsonl_rows = load_jsonl(Path(report["_path"]).with_suffix(".jsonl"))
        per_call: list[float] = []
        per_case: list[float] = []
        for row in jsonl_rows.values():
            events = row.get("gate_events") or []
            values = [float(event.get("latency_ms", 0.0)) for event in events if event.get("latency_ms") is not None]
            if values:
                per_call.extend(values)
                per_case.append(sum(values))
        if per_call:
            per_call_sorted = sorted(per_call)
            out[f"{condition}:{key}"] = {
                "calls": len(per_call),
                "p50_ms": round(statistics.median(per_call_sorted), 2),
                "p95_ms": round(per_call_sorted[min(len(per_call_sorted) - 1, round(0.95 * len(per_call_sorted)) - 1)], 2),
                "mean_case_ms": round(statistics.mean(per_case), 2),
            }
    return out


def utility(directory: Path, reports: dict, meta: dict) -> list[dict]:
    out = []
    for (condition, key), report in sorted(reports.items()):
        if condition not in ("ours", "a1", "a2", "a3", "b2"):
            continue
        rows = load_jsonl(Path(report["_path"]).with_suffix(".jsonl"))
        if not rows:
            continue
        user_blocks = user_seen = 0
        for case_id, row in rows.items():
            info = meta.get(case_id)
            if info is None or not info.get("user_tool"):
                continue
            for event in row.get("gate_events") or []:
                if event.get("name") == info["user_tool"]:
                    user_seen += 1
                    if not event.get("allowed", True):
                        user_blocks += 1
        out.append(
            {
                "condition": condition,
                "slice": key,
                "valid_rate": report.get("valid_rate"),
                "user_tool_calls": user_seen,
                "user_tool_blocks": user_blocks,
                "ignored_share": (
                    round((report.get("counts") or {}).get("ignored", 0) / report["n"], 4)
                    if "mcptox" in key and report.get("n")
                    else None
                ),
            }
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/phase5")
    ap.add_argument("--out", default="")
    ap.add_argument("--markdown", default="")
    ap.add_argument("--tau-grid", default="0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80")
    ap.add_argument("--delta-grid", default="0.05,0.10,0.15")
    args = ap.parse_args()

    directory = ROOT / args.dir
    reports = load_reports(directory)
    if not reports:
        raise SystemExit(f"no condition reports under {directory}")
    meta = {}
    meta.update(injecagent_meta())
    meta.update(mcptox_meta())

    tau_grid = [float(part) for part in args.tau_grid.split(",") if part.strip()]
    delta_grid = [float(part) for part in args.delta_grid.split(",") if part.strip()]

    headline_rows = headline(reports)
    print_headline(headline_rows)

    stat_rows = stats_for(directory, reports, "injecagent") + stats_for(directory, reports, "mcptox")
    print("\n== stats (paired vs b1) ==")
    for row in stat_rows:
        ci = row["asr_ci95"]
        print(
            f"  {row['condition']:<4} {row['slice']:<28} n={row['n_pairs']:<5} ASR={row['asr']} "
            f"CI95=[{ci[0]}, {ci[1]}] b1={row['b1_asr']} mcnemar={row['mcnemar_vs_b1']['method']} "
            f"p={row['mcnemar_vs_b1']['p_value']:.2e}"
        )

    print("\n== breakdowns (b1 vs ours) ==")
    breakdowns = {}
    for benchmark, group_key in (("injecagent", "attacker_tool"), ("injecagent", "user_tool"), ("injecagent", "split"), ("mcptox", "risk")):
        rows = breakdown(directory, reports, meta, benchmark, group_key)
        breakdowns[f"{benchmark}:{group_key}"] = rows
        for row in rows[:15]:
            print(
                f"  {benchmark}:{group_key:<12} {row['group'][:36]:<36} n={row['n']:<5} "
                f"b1={row['b1_asr']} ours={row['ours_asr']} blocked={row['blocked']}"
            )

    print("\n== latency (gated conditions) ==")
    latency_rows = latency(directory, reports)
    for key, row in latency_rows.items():
        print(f"  {key:<40} calls={row['calls']:<5} p50={row['p50_ms']}ms p95={row['p95_ms']}ms")

    print("\n== utility proxies ==")
    utility_rows = utility(directory, reports, meta)
    for row in utility_rows[:20]:
        print(
            f"  {row['condition']:<4} {row['slice']:<28} valid_rate={row['valid_rate']} "
            f"user_tool_calls={row['user_tool_calls']} user_tool_blocks={row['user_tool_blocks']} "
            f"ignored_share={row['ignored_share']}"
        )

    pareto_rows = pareto(directory, reports, tau_grid, delta_grid)

    payload = {
        "headline": headline_rows,
        "stats": stat_rows,
        "breakdowns": breakdowns,
        "latency": latency_rows,
        "utility": utility_rows,
        "pareto": pareto_rows,
    }
    out_path = ROOT / args.out if args.out else directory / "report.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
