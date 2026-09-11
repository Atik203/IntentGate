# S3b — Our B1 pipeline (gate-ready) on InjecAgent

**Date:** 2026-09-11 · **Purpose:** validate our own harness against the authors' reference
before any gating is added (blueprint Sec 13 step 1; roadmap Phase 2).

## Setup

| Item | Value |
|---|---|
| Harness | `harness/` — vendored prompts + ported evaluator + adapter + runner |
| Benchmark | `f19c9f2c`, `base` setting, 10 `dh` + 10 `ds`, seed 42 |
| Model | `gpt-4o-mini`, temperature 0 |
| Gate | none (B1) |

## Results — exact agreement with the reference run

| Split | Reference (authors' harness) | Ours | Case-by-case |
|---|---|---|---|
| dh | 2 succ / 8 unsucc → 20.0% | 2 succ / 8 unsucc → 20.0% | identical (10/10) |
| ds | 2 succ / 8 unsucc → 20.0% | 2 succ / 8 unsucc → 20.0% | identical (10/10) |
| **Total** | **20.0%** | **20.0%** | **20/20 identical evals** |

Valid rate 100% in both. The per-case eval sequences (including which specific cases
succeeded) are byte-identical between the two implementations.

## Why this matters

- Our pipeline emits a structured `ToolCall` per proposed action
  (`harness/injecagent_runner.py`) — the exact input the gate will score in Phase 4.
- Differential test `tests/test_injecagent_parsing.py::test_differential_against_original_evaluator`
  pins our evaluator to the original on labeled outputs (runs only when the clone exists).
- Divergence risk between B1/B2/ours is now low: same prompts (vendored), same parse
  semantics (differential-tested), same model/temperature.

**Conclusion: Gate 0's B1-side prerequisite is satisfied for InjecAgent.** MCPTox (S4)
and the 50-case scorer pilot (S6) remain.

## Artifacts

- Raw outputs (gitignored): `results/injecagent_ours/test_cases_{dh,ds}_base.jsonl`
- Summary (gitignored): `results/injecagent_ours/summary_base.json`
