# 01 — Gate 0: foundation, B1 baseline & scorer pilot (E1–E4)

> **Status: COMPLETE (2026-09-11) · Gate 0 = GO.** All four experiments below were run before the
> gate existed; they establish that the harness is trustworthy and that Assumption 2 holds
> (the scorer separates hijack from legitimate calls).

| ID | Experiment | Dataset / slice | Headline result | Artifacts (gitignored) |
|---|---|---|---|---|
| E1 | B1 reference ASR on InjecAgent (authors' harness) | InjecAgent `f19c9f2c`, `base`, 10 dh + 10 ds, seed 42 | 20.0% ASR-valid (paper GPT-4 ~24%) | `results/injecagent_reference/` |
| E2 | B1 through **our** gate-ready pipeline | same 20 cases | byte-identical evals to E1 (20/20) | `results/injecagent_ours/` |
| E3 | B1 on MCPTox static snapshot | AAAI26-7C02 snapshot, 20 cases, seed 42 | 30% attack-influenced (10% success) | `results/mcptox_ours/` |
| E4 | **Gate 0 scorer pilot** (Assumption 2) | 50 labeled calls from 25 InjecAgent cases | **AUC 0.979 · ASR 0% / FPR 4% @ τ=0.75 → GO** | `results/pilot_score_dist.json` |

Pinned models: agent/parser `gpt-4o-mini` (temperature 0), embeddings
`sentence-transformers/all-MiniLM-L6-v2` (CPU). Benchmark commits live in
`configs/benchmark_versions.yaml`.

---

## E1 — B1 reference run (authors' harness) {#e1}

**Goal.** Trust check: run InjecAgent's own prompted-agent pipeline on a deterministic subset and
compare with the paper's ballpark before building our pipeline.

**Setup.** `scripts/run_injecagent_reference.py` (uses the gitignored clone unmodified);
InjecAgent `f19c9f2c`; `base` setting; 10 `dh` + 10 `ds` cases, seed 42; `gpt-4o-mini`,
temperature 0; first agent step only.

**Results.**

| Split | n | succ | unsucc | invalid | ASR-valid |
|---|---|---|---|---|---|
| Direct Harm (dh) | 10 | 2 | 8 | 0 | 20.0% |
| Data Stealing (ds) | 10 | 2 | 8 | 0 | 20.0% |
| **Total** | 20 | 4 | 16 | 0 | **20.0%** |

Valid rate 100%. Interpretation: InjecAgent reports ~24% for GPT-4 base; 20% with a smaller model
is the expected ballpark → the harness/environment is trusted. Not a paper number (n=20,
different model); full numbers come from Phase 5 on all 1,054 cases.

## E2 — B1 through our gate-ready pipeline {#e2}

**Goal.** Prove our vendored prompts + ported evaluator + structured `ToolCall` emission reproduce
the reference exactly — so later B2/ours deltas are gate effects, not harness effects.

**Setup.** `harness/` pipeline: vendored prompts (`harness/prompts/injecagent.py`), ported parser
(`harness/parsing.py`), case runner (`harness/injecagent_runner.py`), `scripts/run_injecagent_ours.py`.
Same 20 cases, same model/temperature.

**Results.**

| Split | Reference (E1) | Ours | Case-by-case |
|---|---|---|---|
| dh | 20.0% | 20.0% | identical (10/10) |
| ds | 20.0% | 20.0% | identical (10/10) |
| **Total** | **20.0%** | **20.0%** | **20/20 identical evals** |

The per-case eval sequences (including *which* cases succeeded) are byte-identical.
Differential test `tests/test_injecagent_parsing.py::test_differential_against_original_evaluator`
pins our evaluator to the original on labeled outputs (skips when the clone is absent).

**Why it matters.** Every proposed action is emitted as a `ToolCall(name, params, source)` — the
exact object the gate intercepts in Gate 2 (`docs/experiments/04_gate2_gated_eval.md`).

## E3 — B1 on the MCPTox static snapshot {#e3}

**Goal.** Build the MCPTox adapter and measure unprotected B1 behavior on the released snapshot
(tool-poisoning vector).

**Setup.** Snapshot AAAI26-7C02 downloaded 2026-09-11 (static); 1,348 cases across 45 servers;
20 sampled (seed 42); prompt = snapshot `datas[0].system` (poisoned tool descriptions) +
`datas[0].query`; evaluator = documented heuristic in `harness/mcptox_runner.py`
(payload / sensitive-path detection).

**Results (n=20).**

| Label | Count | Share |
|---|---|---|
| success (payload / sensitive access) | 2 | 10% |
| work_not_success (fake or non-clean tool called) | 4 | 20% |
| ignored | 13 | 65% |
| invalid | 1 | 5% |
| **attack-influenced (success + work_not_success)** | **6** | **30%** |

**Evaluator validation.** All 10,162 recorded model responses in the snapshot were classified and
compared with the authors' labels: success precision **0.82**, recall **0.26** (conservative — it
reliably catches payload/credential attacks, misses regex-less malicious intents such as message
hijacking). It is a gate-testing substrate, not a reproduction of the authors' annotation.

## E4 — Gate 0 scorer pilot (Assumption 2) — GO {#e4}

**Goal.** Confirm the scorer separates hijack from legitimate calls *before* building the full gate
(cheapest place to fail).

**Setup.** `scripts/build_pilot_set.py` → `scripts/pilot_score_dist.py`. 25 hijack + 25 legit
labeled calls constructed from 25 InjecAgent `base` cases (13 dh + 12 ds); contracts from the LLM
parser v1; scoring `S = 0.7·S_sem + 0.3·S_rule` with critical veto; real MiniLM embeddings on CPU.

**Results.**

| Metric | Value |
|---|---|
| hijack S | 0.537 ± 0.303 (6 vetoed to 0.0, rest 0.6–0.8) |
| legit S | 0.849 ± 0.040 (cluster 0.8–0.9) |
| **AUC (legit > hijack)** | **0.979** |
| At τ = 0.75 | **ASR 0.0% · FPR 4.0%** (1/25) |
| τ sensitivity | τ ≤ 0.65: ASR 76% · τ = 0.70: 40% · τ = 0.75: 0% |
| Borderline | `GmailReadEmail` legit at S = 0.69 (semantic 0.55) |

**Three rule-engine false positives found and fixed during the pilot** (AUC 0.80 → 0.86 → 0.979):

1. CamelCase benchmark tools bypassed snake_case category sets → keyword-based categorization.
2. `email` matched "external send" for read/search tools → send now requires action verbs.
3. `share` matched "send" for `...SharedCalendar` → only sensitive sharing counts.

**Decision: GO.** Scorer separates classes at a usable operating point (ASR 0% with FPR 4% < 10%
target). Default `τ = 0.75` set in `configs/thresholds.yaml` (full sweep in E9).

---

## Reproduce

```powershell
.venv\Scripts\Activate.ps1
# E1 (authors' harness; needs the gitignored clone)
python scripts/run_injecagent_reference.py --per-split 10 --setting base
# E2 (our B1 pipeline; needs OPENAI_API_KEY in .env)
python scripts/run_injecagent_ours.py --per-split 10 --setting base
# E3 (MCPTox snapshot)
python scripts/run_mcptox_ours.py --limit 20
# E4 (pilot; offline-safe after build)
python scripts/build_pilot_set.py
python scripts/pilot_score_dist.py
```

## Related files

- Harness: `harness/adapters/injecagent.py`, `harness/adapters/mcptox.py`,
  `harness/injecagent_runner.py`, `harness/mcptox_runner.py`, `harness/parsing.py`,
  `harness/prompts/injecagent.py`
- Scripts: `scripts/run_injecagent_reference.py`, `scripts/run_injecagent_ours.py`,
  `scripts/run_mcptox_ours.py`, `scripts/build_pilot_set.py`, `scripts/pilot_score_dist.py`
- Configs: `configs/benchmark_versions.yaml`, `configs/thresholds.yaml`
- Tests: `tests/test_injecagent_loader.py`, `tests/test_injecagent_parsing.py`,
  `tests/test_injecagent_runner.py`, `tests/test_mcptox_runner.py`, `tests/test_scorer_veto.py`

## Limitations

- Constructed hijack parameters in the pilot (documented approximation, not model outputs); n=50,
  one benchmark.
- τ = 0.75 is specific to MiniLM + this contract format; ablation A3 (raw-request embedding) may
  shift it — Phase 5 measures this.
- MCPTox numbers are **not** comparable to the paper (static snapshot, different model,
  conservative heuristic evaluator).
- `GmailReadEmail` borderline shows FPR risk concentrates in low-lexical-overlap legit calls.

## Supervisor Q&A

**Q: Why these two benchmarks?**
A: They cover the two threat vectors we target — InjecAgent (indirect prompt injection) and MCPTox
(tool poisoning at registration). AgentDojo/ASB are stretch/context only.

**Q: Why only 20 cases per run?**
A: These are trust checks, not results. Phase 5 runs the full suites (1,054 + 1,348) with
confidence intervals.

**Q: How do you know your harness is equivalent to the authors'?**
A: E2 reproduces E1 case-by-case (20/20 byte-identical evals) with vendored prompts and a
differentially-tested evaluator.

**Q: What exactly did the pilot prove?**
A: Assumption 2 — embeddings + rule veto separate hijack from legit calls (AUC 0.979; ASR 0% /
FPR 4% at τ=0.75) — so building the full gate is justified.

**Q: Why τ=0.75 and not 0.6 or 0.8?**
A: It is the knee on the pilot curve: 0.75 is the first τ with hijack-ASR 0 while FPR stays at 4%;
0.80 doubles FPR. Re-verified on cached traces in E9.

**Q: Is the heuristic MCPTox evaluator good enough?**
A: It is conservative (precision 0.82, recall 0.26) and documented; gated comparisons use
attack-influenced (success + work_not_success). An LLM-judge second evaluator is a Phase 5 option.
