"""E30: request-grouped heldout checks for a score-coverage conformal band.

The covered object is a future case group's scores, never an attack outcome.
The calibrated symmetric interval is a diagnostic, not a middleware policy change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from intent_gate.eval.stats import conformal_band

from scripts.e29_embedding_transfer import digest, load_jsonl, output_directory, provenance


def grouped_scores(paths: list[Path], tau: float) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for path in paths:
        for row in load_jsonl(path):
            request = row["contract"]["raw_request"]
            group = hashlib.sha256(request.encode()).hexdigest()
            if group not in groups:
                groups[group] = {"case_ids": set(), "scores": [], "max_deviation": 0.0}
            groups[group]["case_ids"].add(row["case_id"])
            score = float(row["gate"]["S"])
            groups[group]["scores"].append(score)
            groups[group]["max_deviation"] = max(
                groups[group]["max_deviation"], abs(score - tau)
            )
    return groups


def evaluate_split(
    groups: dict[str, dict[str, Any]], tau: float, alpha: float, seed: int
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    names = sorted(groups)
    order = np.random.default_rng(seed).permutation(len(names))
    cut = len(names) // 2
    calibration = [names[i] for i in order[:cut]]
    test = [names[i] for i in order[cut:]]
    if not calibration or not test:
        raise ValueError("At least two distinct request groups are required")
    representatives = [
        tau - groups[name]["max_deviation"]
        if groups[name]["max_deviation"] <= tau
        else tau + groups[name]["max_deviation"]
        for name in calibration
    ]
    band = conformal_band(representatives, tau=tau, alpha=alpha)
    delta = band["delta"]
    heldout = [
        {
            "request_group": name,
            "case_ids": sorted(groups[name]["case_ids"]),
            "calls": len(groups[name]["scores"]),
            "max_deviation": groups[name]["max_deviation"],
            "covered": groups[name]["max_deviation"] <= delta,
        }
        for name in test
    ]
    scores = [score for name in test for score in groups[name]["scores"]]
    return {
        "seed": seed,
        "calibration_groups": len(calibration),
        "heldout_groups": len(test),
        "group_overlap": len(set(calibration) & set(test)),
        "band": band,
        "heldout_groups_covered": sum(row["covered"] for row in heldout),
        "heldout_group_coverage": float(np.mean([row["covered"] for row in heldout])),
        "heldout_calls": len(scores),
        "heldout_call_coverage_descriptive": float(np.mean([
            abs(score - tau) <= delta for score in scores
        ])),
        "heuristic_delta_0_1_group_coverage": float(np.mean([
            row["max_deviation"] <= 0.1 for row in heldout
        ])),
    }, heldout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "results/phase7/e30_conformal_band")
    parser.add_argument("--tau", type=float, default=0.75)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 0 < args.alpha < 1 or not 0 <= args.tau <= 1:
        parser.error("alpha must lie in (0, 1), tau in [0, 1]")
    paths = sorted((ROOT / "results/phase5").glob("ours_*_trace.jsonl"))
    out = output_directory(args.out)
    groups = grouped_scores(paths, args.tau)
    primary, heldout = evaluate_split(groups, args.tau, args.alpha, args.seed)
    sensitivity: list[dict[str, Any]] = []
    for seed in range(100):
        row, _ = evaluate_split(groups, args.tau, args.alpha, seed)
        sensitivity.append(row)
    report = {
        "experiment": "E30",
        "status": "complete_offline_pilot",
        "covered_object": "all cached S values in a fresh trusted-request group",
        "nonconformity": "group maximum of abs(S - fixed tau)",
        "unit": "SHA256(raw_request); all base/enhanced and repeated-task cases stay together",
        "target_coverage": 1 - args.alpha,
        "primary_split": primary,
        "total_request_groups": len(groups),
        "total_calls": sum(len(group["scores"]) for group in groups.values()),
        "sensitivity_100_splits": {
            "mean_heldout_group_coverage": float(np.mean([
                row["heldout_group_coverage"] for row in sensitivity
            ])),
            "min_heldout_group_coverage": min(
                row["heldout_group_coverage"] for row in sensitivity
            ),
            "max_heldout_group_coverage": max(
                row["heldout_group_coverage"] for row in sensitivity
            ),
            "splits": sensitivity,
        },
        "provenance": provenance(paths),
        "script_sha256": digest(Path(__file__)),
        "statistics_implementation_sha256": digest(ROOT / "src/intent_gate/eval/stats.py"),
        "shared_helpers_sha256": digest(ROOT / "scripts/e29_embedding_transfer.py"),
        "method_source": "https://arxiv.org/abs/2107.07511",
        "interpretation": [
            "The lower marginal coverage bound needs exchangeable calibration/test groups "
            "and tau fixed independently of them; the historical tau is treated as fixed.",
            "The heterogeneous benchmark census does not establish exchangeability for "
            "deployment; heldout empirical coverage is measured, not a universal guarantee.",
            "Coverage concerns score dispersion, not correct decisions or attack success.",
            "A wide or full-support interval is valid but uninformative for escalation.",
            "Production decide() uses [tau-delta,tau) for escalation; this symmetric "
            "coverage diagnostic changes neither that implementation nor frozen results.",
            "Repeated splits reuse observations and are sensitivity checks, not independent "
            "replications or a confidence interval.",
        ],
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out / "heldout_groups.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in heldout), encoding="utf-8"
    )
    print(json.dumps(primary, indent=2))


if __name__ == "__main__":
    main()
