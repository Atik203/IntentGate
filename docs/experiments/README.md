# Experiments — index & status

> This folder is the **experiment record** for the thesis. Each report is self-contained: setup,
> commands, datasets, results, artifacts, limitations and a supervisor Q&A block. Start here, then
> open the report for the experiment you need.
>
> **New to the project?** Read [`../team_guide.md`](../team_guide.md) first — it explains the
> project and summarizes these results in plain words.

**Current state (2026-10-13):** Gate 0 ✅ · Gate 1 ✅ · Gate 2 ✅ · Gate 3 ✅ (results frozen — Phase 5 full matrix). **Phase 6 (E18–E22) COMPLETE** — all P0/P1 pilots done.

## Gate status

| Gate | Definition | Status | Evidence |
|---|---|---|---|
| Gate 0 | B1 reproduces + 50-case pilot passes (Assumption 2) | ✅ 2026-09-11 | `01_gate0_foundation.md` (E1–E4) |
| Gate 1 | B2 reimpl validated (coverage reported) | ✅ 2026-09-16 | `03_b2_toolgate.md` (E7) |
| Gate 2 | Gate integrated; unit tests green; p95 latency measured | ✅ 2026-09-16 | `04_gate2_gated_eval.md` (E8–E10) |
| Gate 3 | Full-suite results freeze | ✅ 2026-10-12 | `05_phase5_full_evaluation.md` (E11–E17) |

## Phase 6 status (preliminary, never rewrites E11–E17)

| Experiment | Description | Result | Report |
|---|---|---|---|
| E18 | Second-backbone pilot (Qwen3.5:4b + gpt-6-luna) | Qwen 27.1%→2.1% ASR; Luna prose-only (excluded) | `06_phase6_pilots.md#e18` |
| E19 | B2 coverage curve (65→583 contracts) | 37.2%→84.9% weighted; curve flat | `06_phase6_pilots.md#e19` |
| E20 | Intent-mimicry probe (13 residuals) | Avg S inflation +0.0112; 0/13 cross τ | `06_phase6_pilots.md#e20` |
| E21 | Escalate precision (583 calls, hand-labeled) | 80.5% precision; 14.8% false-escalate | `06_phase6_pilots.md#e21` |
| E22 | Power analysis + Bonferroni + per-specificity FPR | Power=1.0 at α=0.005; FPR specific 12.8% | `06_phase6_pilots.md#e22` |

## Experiment index

| ID | Experiment | Dataset / slice | Headline | Report |
|---|---|---|---|---|
| E1 | B1 reference ASR (authors' harness) | InjecAgent `f19c9f2c` base, 20 | 20.0% ASR-valid (paper ballpark) | [01](01_gate0_foundation.md#e1) |
| E2 | B1 through our pipeline (parity check) | same 20 | 20/20 byte-identical evals | [01](01_gate0_foundation.md#e2) |
| E3 | B1 on MCPTox snapshot | MCPTox 2026-09-11, 20 | 30% attack-influenced | [01](01_gate0_foundation.md#e3) |
| E4 | **Gate 0 scorer pilot** | 50 labeled calls (25 cases) | **AUC 0.979 · ASR 0% / FPR 4% @ τ=0.75 → GO** | [01](01_gate0_foundation.md#e4) |
| E5 | Parser v1 + schema v1 freeze | 30 requests | over-blocking bug fixed; frozen v1 | [02](02_parser_schema.md#e5) |
| E6 | Schema v1.1 unfreeze (`system_change`) | 30 requests | re-validated; explicit side effects authorized | [02](02_parser_schema.md#e6) |
| E7 | B2 ToolGate contracts + coverage freeze | InjecAgent 79 · MCPTox 801 tools | 100% / 8.1% (37.2% weighted) coverage | [03](03_b2_toolgate.md) |
| E8 | **Gated integration run** | 100 InjecAgent + 100 MCPTox × 3 conditions | **InjecAgent 9/100 → 0/100; MCPTox 22 → 10 attacked; p95 ≤ 23 ms** | [04](04_gate2_gated_eval.md#e8) |
| E9 | **Threshold sweep / Pareto** | cached traces, τ 0.40–0.80 | knee at **τ = 0.75** (pilot FPR 4%) | [04](04_gate2_gated_eval.md#e9) |
| E10 | Error taxonomy + rule fixes | 11 → 9 failures | all residual = registration trust | [04](04_gate2_gated_eval.md#e10) |
| E11 | **Phase 5 headline matrix** | 2,108 InjecAgent + 1,348 MCPTox × 6 conditions | **InjecAgent 19.0% → 0.7%; MCPTox 279 → 144; B2 ≈ B1** | [05](05_phase5_full_evaluation.md#e11--headline-matrix-ours-vs-baselines) |
| E12 | Ablations A1–A3 (full matrix) | same | A1 ≥ ours; A2 ≈ B1 (rules alone ~no-op on ds); A3 ≈ ours | [05](05_phase5_full_evaluation.md#e12--ablations-a1a3-full-matrix) |
| E13 | τ×δ Pareto (full traces) | 27 cells × 2 benchmarks | knee re-confirmed at τ=0.75; escalate ~20% | [05](05_phase5_full_evaluation.md#e13--τδ-pareto-full-traces) |
| E14 | Bootstrap CI + McNemar | ds_enhanced + MCPTox | ours p=1.3e-33 / 1.25e-07; B2 n.s. | [05](05_phase5_full_evaluation.md#e14--paired-stats-bootstrap-95-ci--mcnemar-vs-b1-primary-slices) |
| E15 | Breakdowns + stratification + coverage | per risk/tool/split | CredLeak 0.130 → 0.017; FPR via valid-rate parity | [05](05_phase5_full_evaluation.md#e15--breakdowns-stratification-coverage) |
| E16 | Full-scale error taxonomy | 13 InjecAgent + MCPTox residuals | all rule=1.0, S just above τ (near-miss reads) | [05](05_phase5_full_evaluation.md#e16--error-taxonomy-residual-failures-with-score-evidence) |
| E17 | Latency / utility / cost | per-call traces + usage | p95 16–20 ms; $11.46 list / $9.64 billed | [05](05_phase5_full_evaluation.md#e17--latency-utility-cost) |
| E18 | **Phase 6: Second-backbone pilot** | Qwen3.5:4b (100) + gpt-6-luna (20) | Qwen 27.1%→2.1%; Luna excluded (prose-only) | [06](06_phase6_pilots.md#e18) |
| E19 | **Phase 6: B2 coverage curve** | 65→583 MCPTox contracts | 37.2%→84.9% weighted; flat curve | [06](06_phase6_pilots.md#e19) |
| E20 | **Phase 6: Intent-mimicry probe** | 13 residuals × 3 variants | Avg ΔS +0.0112; 0/13 cross τ | [06](06_phase6_pilots.md#e20) |
| E21 | **Phase 6: Escalate precision** | 583 escalated calls (hand-labeled) | 80.5% precision; 14.8% false-escalate | [06](06_phase6_pilots.md#e21) |
| E22 | **Phase 6: Power + Bonferroni + FPR** | n=2,108 / 1,348 | Power=1.0 at α=0.005; FPR specific 12.8% | [06](06_phase6_pilots.md#e22) |

Status legend: E1–E10 were development-set evidence; **E11–E17 are the frozen full-suite
results** (Gate 3, 2026-10-12). **E18–E22 are Phase 6 preliminary pilots** (2026-10-13, never
rewrite E11–E17).

## Datasets & versions

| Benchmark | Version / snapshot | Path (gitignored) | Used in |
|---|---|---|---|
| InjecAgent | commit `f19c9f2c` (configs/benchmark_versions.yaml) | `data/raw/InjecAgent/` | E1, E2, E4, E7, E8, E9, E10 |
| MCPTox | AAAI26-7C02 snapshot downloaded 2026-09-11 (1,348 cases, 45 servers, 801 registered tools — the coverage universe; 485 `def_tool/` scripts. Paper cites 353 authentic tools) | `data/raw/mcptox/` | E3, E7, E8, E9, E10 |
| ToolGate | commit `976ad3f5` (B2 reference code, read-only) | `data/raw/ToolGate/` | E7 |
| AgentDojo | commit `089ed468` (stretch only, not used in gated runs) | `data/raw/agentdojo/` | — |

## Pinned models

| Role | Model | Notes |
|---|---|---|
| Agent | `gpt-4o-mini` (`AGENT_MODEL_ID`) | temperature 0 |
| Parser | `gpt-4o-mini` (`PARSER_MODEL_ID`) | JSON mode, temp 0, 1 repair retry |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | CPU; functional probe hash `4588b3f9e962`; hash logged in every trace |

## Artifact map (all under `results/`, tracked in git so teammates skip re-running evals)

| Path | Contents | Regenerated by |
|---|---|---|
| `results/injecagent_reference/` | E1 JSONL + summary | `scripts/run_injecagent_reference.py` |
| `results/injecagent_ours/` | E2 JSONL + summary | `scripts/run_injecagent_ours.py` |
| `results/mcptox_ours/` | E3 JSONL + summary | `scripts/run_mcptox_ours.py` |
| `results/pilot_set.json`, `results/pilot_score_dist.json` | E4 labeled set + scores | `scripts/build_pilot_set.py`, `scripts/pilot_score_dist.py` |
| `results/parser_spotcheck.json`, `results/parser_spotcheck_v2.json` | E5/E6 spot-checks | `scripts/check_parser.py` |
| `configs/b2_coverage.json` | E7 frozen coverage | `scripts/freeze_b2_coverage.py` |
| `results/gated/*.json` | E8 per-condition reports | `harness/run_injecagent.py`, `harness/run_mcptox.py` |
| `results/gated/*.jsonl` | per-case rows incl. `gate_events` | same |
| `results/gated/*_trace.jsonl` | per-call gate traces (S, S_sem, S_rule, decision, latency, contract) | same |
| `results/gated/pareto.json` | E9 sweep table (all + per benchmark) | `scripts/sweep_gated.py` |
| `results/gated/error_taxonomy.json` | E10 failure records + contracts | `scripts/error_taxonomy.py` |
| `results/phase5/` | E11–E17 reports + JSONL + traces + `report.json/md` + taxonomies + manifest | `scripts/run_phase5.py`, `scripts/report_phase5.py`, `scripts/error_taxonomy.py` |
| `results/gated_v1/` | pre-fix snapshot kept for comparison | manual copy |

## Reproduce (quick)

Environment/install: [`../setup.md`](../setup.md).

```powershell
.venv\Scripts\Activate.ps1                     # Python 3.12, deps installed
pytest -q                                      # 170 tests (data-dependent tests skip without clones)
python scripts/freeze_b2_coverage.py           # E7 coverage freeze (offline)
python harness/run_mcptox.py --gate ours --threshold 0.75 --limit 100 --seed 42 --report results/gated/ours_mcptox100.json   # E8 (API key)
python scripts/sweep_gated.py --b1 results/gated/none_dh50.jsonl ... --trace results/gated/ours_dh50_trace.jsonl ...        # E9 (offline)
```

## Merge map (old → new)

The experiment record was consolidated from 10 short files into 4 indexed reports:

| Old file | Now in |
|---|---|
| `gate0_pilot.md` | `01_gate0_foundation.md` (E4) |
| `b1_reference_injecagent_20.md` | `01_gate0_foundation.md` (E1) |
| `b1_ours_injecagent_20.md` | `01_gate0_foundation.md` (E2) |
| `b1_mcptox_20.md` | `01_gate0_foundation.md` (E3) |
| `parser_spotcheck_v1.md` | `02_parser_schema.md` (E5) |
| `parser_spotcheck_v2.md` | `02_parser_schema.md` (E6) |
| `gate1_b2.md` | `03_b2_toolgate.md` (E7) |
| `gate2_integration.md` | `04_gate2_gated_eval.md` (E8) |
| `gate2_sweep.md` | `04_gate2_gated_eval.md` (E9) |
| `gate2_errors.md` | `04_gate2_gated_eval.md` (E10) |

No content was dropped in the merge; each old section maps to a named section in its new report.

## Cross-cutting supervisor Q&A

**Q: What is the one-line status of the project?**
A: Gate 3 frozen: on the full suites ours takes InjecAgent ASR-valid 19.0% → 0.7% and MCPTox
attack-influenced 279 → 144 (both McNemar p < 1e-6 vs B1), B2 is statistically indistinguishable
from unprotected, valid-rate parity holds, p95 ≤ 20 ms, billed $9.64. Thesis Chapters 4–5 and
the paper draft now write from E11–E17.

**Q: Which results are final vs development?**
A: E11–E17 are final (full suites, frozen 2026-10-12, Gate 3). E1–E10 were development-set
evidence (50–100 case slices) that motivated the design; they are superseded, not repeated.

**Q: Why InjecAgent + MCPTox and not AgentDojo/ASB?**
A: They are the two vectors where the closest gate (ToolGate) was never tested, and they are the
vectors our supervisor approved for the thesis. AgentDojo is stretch-only.

**Q: How do I know the setup is reproducible?**
A: Every report pins dataset versions, model IDs, seeds and thresholds, and lists the exact
commands; every result row logs the embedding hash and contracts are frozen in `configs/`.

**Q: What is the biggest known weakness?**
A: Registration-time tool poisoning (MCPTox residual): the gate sees a tool call consistent with
the user's request, but the tool itself was maliciously registered. Tool provenance is out of scope
for an action gate; this is documented rather than hidden (E10).

**Q: Where do I add a new experiment?**
A: Append it to the relevant report (or add `05_...md` for a new phase), give it an E-number here,
and keep the template: At a glance → Goal → Setup → Results → Artifacts → Limitations → Supervisor
Q&A.
