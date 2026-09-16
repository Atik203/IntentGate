"""Case-level tau sweep + ASR/FPR Pareto from cached gated traces (blueprint Sec 9).

Usage:
  python scripts/sweep_gated.py --b1 results/gated/none_dh50.jsonl results/gated/none_ds50.jsonl \
    --trace results/gated/ours_dh50_trace.jsonl results/gated/ours_ds50_trace.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_TAU_GRID = "0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80"


def _ground_truth(b1_paths: list[str]) -> dict:
    truth: dict = {}
    for path in b1_paths:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if "eval" in row:
                truth[row["case_id"]] = 1 if row["eval"] == "succ" else 0
            else:
                truth[row["case_id"]] = 1 if row.get("label") in ("success", "work_not_success") else 0
    return truth


def _pilot_fpr(pilot_rows: list[dict], tau: float) -> tuple[float | None, float | None]:
    hijack = [float(r["S"]) for r in pilot_rows if r["label"] == 1]
    legit = [float(r["S"]) for r in pilot_rows if r["label"] == 0]
    asr = sum(1 for s in hijack if s >= tau) / len(hijack) if hijack else None
    fpr = sum(1 for s in legit if s < tau) / len(legit) if legit else None
    return asr, fpr


def _table(case_sweep: dict, pilot_rows: list[dict]) -> list[dict]:
    table = []
    for tau, metrics in case_sweep.items():
        pilot_asr, pilot_fpr = _pilot_fpr(pilot_rows, tau)
        table.append(
            {
                "tau": tau,
                "observed_attacks": metrics.n_attacks,
                "trace_asr": round(metrics.asr, 4),
                "observed_non_attacks": metrics.n_legit,
                "trace_block_rate": round(metrics.fpr, 4),
                "pilot_hijack_asr": None if pilot_asr is None else round(pilot_asr, 4),
                "pilot_legit_fpr": None if pilot_fpr is None else round(pilot_fpr, 4),
            }
        )
    return table


def _print_table(title: str, table: list[dict]) -> None:
    print(f"--- {title} ---")
    print(f"{'tau':>5} {'attacks':>7} {'ASR':>6} {'nonAtt':>6} {'blkRate':>8} {'pilotASR':>9} {'pilotFPR':>9}")
    for row in table:
        pilot_asr = "-" if row["pilot_hijack_asr"] is None else f"{row['pilot_hijack_asr']:.2f}"
        pilot_fpr = "-" if row["pilot_legit_fpr"] is None else f"{row['pilot_legit_fpr']:.2f}"
        print(
            f"{row['tau']:>5.2f} {row['observed_attacks']:>7} {row['trace_asr']:>6.2f} "
            f"{row['observed_non_attacks']:>6} {row['trace_block_rate']:>8.2f} "
            f"{pilot_asr:>9} {pilot_fpr:>9}"
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b1", nargs="+", required=True, help="ungated JSONL run(s) for ground truth")
    ap.add_argument("--trace", nargs="+", required=True, help="gated gate-trace JSONL(s), paired with --b1")
    ap.add_argument("--pilot", default="results/pilot_score_dist.json")
    ap.add_argument("--tau-grid", default=DEFAULT_TAU_GRID)
    ap.add_argument("--delta", type=float, default=0.1)
    ap.add_argument("--out", default="results/gated/pareto.json")
    args = ap.parse_args()
    if len(args.b1) != len(args.trace):
        raise SystemExit("--b1 and --trace must be given in pairs")

    from intent_gate.eval.sweep import load_trace, sweep_cases

    ground_truth = _ground_truth(args.b1)
    trace_rows = [row for path in args.trace for row in load_trace(path)]
    tau_grid = [float(part) for part in args.tau_grid.replace(":", ",").split(",") if part.strip()]

    pilot_path = ROOT / args.pilot
    pilot_rows = json.loads(pilot_path.read_text(encoding="utf-8"))["scored"] if pilot_path.exists() else []

    benchmarks = sorted({row["benchmark"] for row in trace_rows if "benchmark" in row})
    all_table = _table(sweep_cases(trace_rows, ground_truth, tau_grid, delta=args.delta), pilot_rows)
    by_benchmark = {
        bench: _table(
            sweep_cases(
                [row for row in trace_rows if row.get("benchmark") == bench],
                ground_truth,
                tau_grid,
                delta=args.delta,
            ),
            [],
        )
        for bench in benchmarks
    }

    _print_table("all benchmarks", all_table)
    for bench, table in by_benchmark.items():
        _print_table(bench, table)

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "delta": args.delta,
                "ground_truth_cases": len(ground_truth),
                "table": all_table,
                "by_benchmark": by_benchmark,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
