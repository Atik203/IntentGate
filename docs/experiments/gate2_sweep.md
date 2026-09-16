# Gate 2 — threshold sweep / ASR-FPR Pareto from cached traces

**Date:** 2026-09-16 · **Purpose:** close the last Phase 4 item — re-derive decisions at every τ
from cached gate traces (blueprint Sec 9: no re-runs) and report the ASR-FPR tradeoff.

## Method

- `scripts/sweep_gated.py` loads the ungated B1 JSONL (ground truth) + the gated gate-trace
  JSONL (each row now carries `case_id` via the middleware context).
- `eval/sweep.py::sweep_cases` re-decides each case at every τ: a case counts as blocked if any
  gate-checked call scores below τ; the escalate band counts as block in benchmark mode.
- Ground truth: InjecAgent = `succ` in B1; MCPTox = `success` + `work_not_success` in B1
  (attack-influenced). ASR is conditional on the gated run actually proposing the call.
- Deployment-side FPR uses the 50 labeled pilot calls with real embeddings
  (`results/pilot_score_dist.json`, Gate 0): `pilot_legit_fpr` = share of labeled legitimate
  calls blocked at τ.

## Sweep (InjecAgent 100 + MCPTox 100, ours run at τ=0.75)

| τ | attacks seen | trace ASR | non-attacks seen | block rate | pilot hijack ASR | pilot legit FPR |
|---|---|---|---|---|---|---|
| 0.40–0.65 | 25 | 0.92 | 4 | 0.00 | 0.76 | 0.00 |
| 0.70 | 25 | 0.76 | 4 | 0.25 | 0.40 | 0.04 |
| **0.75** | 25 | **0.44** | 4 | 0.75 | **0.00** | **0.04** |
| 0.80 | 25 | 0.28 | 4 | 0.75 | 0.00 | 0.08 |

Per benchmark at the chosen operating point (τ=0.75):

| Benchmark | attacks seen | trace ASR | τ=0.80 ASR | pilot FPR (τ=0.75 / 0.80) |
|---|---|---|---|---|
| InjecAgent | 6 | 0.17 (1 missed attack) | 0.00 | 0.04 / 0.08 |
| MCPTox | 19 | 0.53 | 0.37 | 0.04 / 0.08 |

## Interpretation

- τ ≤ 0.65 is unusable: the pilot-set hijack calls mostly score ≥ 0.65, so the gate lets them
  through (pilot hijack ASR 0.76).
- **τ = 0.75 is the knee**: every labeled pilot hijack is blocked (pilot ASR 0), pilot FPR stays
  at the Gate 0 value (4%), InjecAgent ASR drops to 0.17, and MCPTox attack-influenced calls drop
  by ~half. This matches the integration run's operating point.
- τ = 0.80 buys InjecAgent ASR 0.00 but doubles pilot FPR to 8% and barely helps MCPTox (0.53 →
  0.37) — the MCPTox residual is a rule/semantic gap on poisoned-tool calls, not a threshold gap.
- The `trace_block_rate` column is **not** deployment FPR: the four observed non-attack cases are
  run-variance cases (the gated run proposed a call the B1 run did not), so the honest FPR number
  is the pilot column.

## Caveats

- MCPTox ground truth here is attack-influenced (`success` + `work_not_success`); success-only
  numbers are in `docs/experiments/gate2_integration.md`.
- n is small (25 observed attacks); Phase 5 sweeps over the full suites.
- Temperature-0 runs still vary by a case or two, so trace/JSONL pairing is per-run.
- Blueprint Week 5–8 says "unit tests per Section 14", but Section 14 is the supervisor-explanation
  chapter; read as "component unit tests" (108 in `tests/`, including the new `sweep_cases` tests).

## Artifacts

- `scripts/sweep_gated.py`, `eval/sweep.py::sweep_cases` (+ tests in `tests/test_decisions_metrics.py`)
- `results/gated/pareto.json` (table + per-benchmark breakdown, gitignored)
