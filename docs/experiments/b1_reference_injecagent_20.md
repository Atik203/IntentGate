# S3a — Reference B1 ASR (InjecAgent's own harness)

**Date:** 2026-09-11 · **Purpose:** harness-trust check before building our gate-ready pipeline
(blueprint Sec 13 step 1; roadmap Phase 2).

## Setup

| Item | Value |
|---|---|
| Harness | InjecAgent repo's own `src/` pipeline (prompts, output parsing) via `scripts/run_injecagent_reference.py` |
| Benchmark | `f19c9f2c` (configs/benchmark_versions.yaml) |
| Model | `gpt-4o-mini`, temperature 0 |
| Setting | `base` |
| Sample | 10 `dh` + 10 `ds` cases, seed 42, deterministic |
| Agent steps | first step only (step 2 not run) |

## Results

| Split | n | succ | unsucc | invalid | ASR-valid |
|---|---|---|---|---|---|
| Direct Harm (dh) | 10 | 2 | 8 | 0 | 20.0% |
| Data Stealing S1 (ds) | 10 | 2 | 8 | 0 | 20.0% |
| **Total (first step)** | 20 | 4 | 16 | 0 | **20.0%** |

Valid rate: 100.0% (0 invalid outputs).

## Interpretation

- InjecAgent reports GPT-4 ~24% base ASR (literature_review.md). Our 20% on a 20-case
  subset with a smaller/cheaper model is in the expected ballpark → **the harness and
  environment are trusted**.
- n=20 and `gpt-4o-mini` ≠ GPT-4: this is **not a paper number**, only a sanity check.
  Full baseline numbers come from Phase 5 runs on all 1,054 cases.
- Data-stealing step 2 (attacker tool actually executed) is intentionally skipped here;
  full runs will execute both stages.

## Artifacts

- Script: `scripts/run_injecagent_reference.py` (uses the gitignored clone; no edits to it)
- Raw outputs (gitignored): `results/injecagent_reference/test_cases_{dh,ds}_base.jsonl`
- Summary (gitignored): `results/injecagent_reference/summary_base.json`
