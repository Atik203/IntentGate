"""Run B1/B2/ours on InjecAgent (blueprint Sec 6/13; README Quick Start).

Usage (Weeks 1-2 pilot): python harness/run_injecagent.py --cases data/raw/InjecAgent/cases.json
  --gate ours --threshold 0.6 --split enhanced --report results/injecagent.json
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from intent_gate.parser.parser import IntentParser
from intent_gate.scoring.embeddings import EmbeddingBackend


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--gate", choices=["none", "ours", "toolgate"], default="none")
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--split", default="enhanced")
    ap.add_argument("--report", default="results/injecagent.json")
    args = ap.parse_args()

    from harness.common import load_cases, set_seed

    set_seed(42)
    cases = load_cases(args.cases)
    backend = EmbeddingBackend()
    parser = IntentParser()
    t0 = time.perf_counter()
    per_case = []
    for case in cases:
        contract = parser.parse(case["user_request"])
        # TODO(Gate 2): wire AgentLoop with real executor; record per-case ASR ground truth.
        per_case.append({"case_id": case["case_id"], "contract": contract.to_dict(), "placeholder": True})
    report = {
        "benchmark": "InjecAgent",
        "gate": args.gate,
        "threshold": args.threshold,
        "split": args.split,
        "n_cases": len(cases),
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "embedding_model": backend.model_id,
        "embedding_hash": backend.model_hash,
        "cases": per_case,
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {args.report} ({len(cases)} cases)")


if __name__ == "__main__":
    main()
