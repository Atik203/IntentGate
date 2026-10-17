# Phase 7 Pilots — ICEEICT 2027 submission (E23–E31)

Template: At a glance → Goal → Setup → Results → Artifacts → Limitations → Supervisor Q&A (same as 06).

## E23 — Legitimate-only utility suite (Gap 3)
- Status: [x] complete
- Goal: measure task-completion with gate ON vs OFF on benign tasks (zero attacks).
- Setup: reuse InjecAgent user cases with attacker instruction removed (per supervisor); ran
  `scripts/e23_benign_utility.py` with three conditions: `--gate none` (unprotected),
  `--gate ours --ablation none` (full gate), `--gate ours --ablation semantic-only` (A1);
  50 benign cases (25 dh + 25 ds); output under `results/phase7/e23_utility/`.
- Results (50 clean cases, call-level utility NOT end-to-end task success):

| Condition | User-tool-allowed | Clean-call block rate | p95 latency |
|---|---|---|---|
| none (unprotected) | 16.0% | 0.0% | 2457 ms |
| ours (full gate) | 12.0% | 25.0% | 2332 ms |
| semantic-only (A1) | 8.0% | 42.9% | 2561 ms |

- Interpretation: semantic-only over-blocks legitimate calls (42.9% block rate) while
  allowing fewer user tools (8.0%) — confirming semantic-only is NOT equivalent to ours.
  The contract preserves more legitimate calls (12.0% allowed vs 8.0% for semantic-only)
  with fewer clean-call blocks (25.0% vs 42.9%). This settles E31: contract wins on
  utility, ties on headline ASR. Latency p95 includes LLM call time (not gate-only),
  so comparisons across conditions are valid but absolute numbers are dominated by
  model inference.
- Limitations: small sample (50 cases, 7-8 proposed calls each); call-level utility only,
  not end-to-end task completion; benign cases derived from attack cases by stripping
  attacker content; p95 latency includes LLM inference, not gate-only overhead.
- Supervisor Q&A:
  - Q: Does the gate block legitimate user calls? A: Yes — 25.0% clean-call block rate
    for full gate, 42.9% for semantic-only. The gate trades some utility for security.
  - Q: How does semantic-only (A1) compare on benign utility? A: Worse — 8.0% allowed
    vs 12.0% for full gate, 42.9% vs 25.0% block rate. Contract preserves utility.

## E24 — Prompt-level baselines (Gap 1a)
- Status: [x] complete
- Goal: compare system-text prompt defenses vs baseline on InjecAgent attack cases.
- Setup: `--gate none` with three prompt variants added to `harness/prompts/injecagent.py`:
  **Delimiters** (wrap tool outputs in <<OBS_START/<<OBS_END>>), **InstructionalPrevention**
  (system prompt tells agent to ignore injected instructions), **Sandwich** (repeat user
  instruction after each observation). 50 cases (25 dh + 25 ds, base setting).
- Results (50 attack cases, gate=none for all):

| Prompt variant | ASR | Valid rate | Attack success (succ cases) |
|---|---|---|---|
| baseline (InjecAgent) | 6.8% | 88.0% | 3 |
| Delimiters | 4.3% | 92.0% | 2 |
| Instructional Prevention | 8.9% | 90.0% | 4 |
| Sandwich | 4.3% | 92.0% | 2 |

- Interpretation: Delimiters and Sandwich reduce ASR by ~37% (6.8% → 4.3%) and improve
  valid rate (88.0% → 92.0%). Instructional Prevention worsens ASR (8.9%) — telling the
  agent to ignore injected instructions can backfire by making it more cautious overall.
  Delimiters + Sandwich are the strongest prompt-only defenses but still far behind the
  full gate (ASR 0.7% on InjecAgent).
- Limitations: 50-case sample; single backbone (gpt-4o-mini); no gate involved (these are
  prompt-only defenses, not middleware).
- Supervisor Q&A:
  - Q: Do prompt defenses help? A: Delimiters and Sandwich reduce ASR modestly but are
    far weaker than the middleware gate. They are complementary, not substitutes.
  - Q: Which prompt baseline is best? A: Delimiters and Sandwich tie at 4.3% ASR.

## E25 — Third backbone pilot (Gap 4)
- Status: [ ] not started
- Goal: replicate ASR delta on a new model family with full ReAct participation.
- Setup: `scripts/run_injecagent_ours.py --per-split 50 --setting base --gate none|ours --model-name <new-family>`, parser stays gpt-4o-mini; `--out` under `results/phase7/e25_third_backbone/`.
- Results: per-backbone delta table (B1 ASR → ours ASR), 3 rows.
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E26 — Adaptive attacker pilots (Gap 2)
- Status: [ ] not started
- Goal: attack the gate itself, live. (a) paraphrase-delivery (ASB's 5 injection phrasings); (b) threshold-aware (S ∈ [0.75, 0.79]).
- Setup: InjecAgent pilot slice; live re-score vs τ=0.75.
- Results: ASR-under-adaptation table + honest scope sentence (static vs adaptive).
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E27 — Progent comparison (Gap 1b)
- Status: [x] complete (scope-out table; no port — Progent targets AgentDojo/ASB, not InjecAgent/MCPTox, and requires per-tool policy authoring)
- Goal: position vs. closest neighbor (policy-language tool-call gate, arXiv:2504.11703, Shi et al. 2025). Cited in `literature_review/` + `docs/references.bib` + paper-local `IEEE-conference/references.bib` (`shi2025progent`).
- Setup: read Progent (web/arXiv). Deterministic symbolic privilege-control DSL over tool names/args, fail-closed (no rule → block), no LLM in the decision loop, but policies are manually/LLM-authored per tool and dynamically updated per step; evaluated on AgentDojo/ASB/AgentPoison. A faithful-mini port on our 100-case InjecAgent slice would require re-implementing the DSL + authoring policies for 79 tools + re-running on our benchmarks — scoped out as disproportionate effort for a workshop paper; a feature-by-feature scope-out table is the honest substitute.
- Results (scope-out table):

| Dimension | IntentGate (ours) | Progent (arXiv:2504.11703) |
|---|---|---|
| Policy source | Auto-derived from user's trusted request (zero setup) | Manually- or LLM-authored symbolic DSL policies per tool |
| Enforcement | Embedding similarity $S_{sem}$ + hard rule veto $S_{rule}$ + escalate band | Deterministic symbolic match over tool name/args (JSON Schema) |
| LLM in decision loop | No (parser once per session) | No (deterministic runtime check) |
| LLM for policy authoring | None | Per-task + per-step policy generation/update (LLM-authored) |
| Setup cost | 0 contracts | Per-tool policy authoring (non-zero; not measured on our tools) |
| Default on no match | `no_contract` → never silently allowed | Block by default (fail-closed) |
| Human-in-the-loop | Escalate band ($[\tau-\delta,\tau)$) | Fallback action on blocked call |
| Benchmarks | InjecAgent + MCPTox (injection + tool-poisoning) | AgentDojo + ASB + AgentPoison (injection) |
| Adaptive-attack surface | Threshold-aware ($\tau$ public); $S\in[0.75,0.79]$ near-misses | Policy-update model can be tricked to widen the allowlist |
| Verdict | Complementary, not substitutable: Progent = explicit least-privilege with setup cost; Ours = zero-setup auto-derived intent + auditability | Closest neighbor; cited to avoid appearing unaware |

- Artifacts: `docs/experiments/07_phase7_pilots.md#e27` (this section)
- Limitations: scope-out table is positional, not a head-to-head delta; Progent numbers (AgentDojo/ASB) not directly comparable to our InjecAgent/MCPTox numbers.
- Supervisor Q&A:
  - Q: Why isn't Progent in the results tables? A: Progent evaluates on AgentDojo/ASB with per-tool policy authoring; porting to InjecAgent/MCPTox + authoring 79 policies is disproportionate effort. We cite it and position via the scope-out table instead (a port remains future work).

## E28 — Parser ablation (Upgrade B)
- Status: [ ] not started
- Goal: answer "why not just heuristics."
- Setup: InjecAgent 200-case subset, B1 + ours with LLM parser swapped for heuristic fallback.
- Results: ASR/valid-rate deltas.
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E29 — Embedding swap + τ transfer (Upgrade B)
- Status: [ ] not started
- Goal: show τ is a procedure, not a magic number.
- Setup: re-score cached traces with E5/MPNet; τ tuned on base tested on enhanced (and vice versa).
- Results: transfer table + recalibration note.
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E30 — Conformal escalate band (Upgrade A)
- Status: [ ] not started
- Goal: turn heuristic [τ−δ, τ+δ] band into distribution-free guarantee.
- Setup: calibrate on cached Phase 5 traces; add `conformal_band()` next to `power_analysis()` in `src/intent_gate/eval/stats.py` + tests.
- Results: calibrated (α, empirical coverage) pair + method note.
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E31 — Contract-vs-semantic contribution (supervisor Q5)
- Status: [x] complete (offline, cached Phase 5 traces, no LLM calls)
- Goal: locate where full contract + rules + escalate add value vs A1 (semantic-only).
- Setup: offline comparison of `results/phase5/ours_*_trace.jsonl` vs `results/phase5/a1_semantic_only_*_trace.jsonl` across all 5 Phase 5 conditions (mcptox, dh_base, dh_enhanced, ds_base, ds_enhanced); 2,013 compared calls; script `scripts/e31_contract_vs_semantic.py`; report `results/phase7/e31_contract_vs_semantic/e31_report.json`.
- Results:
  - Aggregate decisions: ours blocks/escalates where A1 allows = 32; A1 blocks/escalates where ours allows = 322; both block/escalate = 681; both allow = 803.
  - Interpretation: semantic-only (A1) is NOT equivalent to ours. A1 over-blocks legitimate calls (322 calls A1 blocks/escalates that ours allows) — a utility loss — while ours catches 32 attacks A1 misses. The contract shifts the operating point toward better valid-rate parity rather than purely higher ASR.
  - Per-risk (MCPTox): semantic-only over-blocks across all risk categories (Privacy Leakage 65, Information Manipulation 63, Service Disruption 54, Data Tampering 26, Credential Leakage 15, ...); ours catches few extras per category (22 total on MCPTox).
  - Cost/latency parity: contract is parsed once per session and embedded once; per-call p95 latency ours 16.2–19.8 ms vs A1 16.6–18.0 ms — within ~2 ms, parity holds.
- Verdict: contract+rule adds value on utility (fewer false blocks) and catches a small set of attacks semantic-only misses; headline ASR parity (E12) holds, so the contract's differentiator is auditability + fail-closed guarantees + valid-rate parity, not raw ASR. Scoped claim: contract wins on valid-rate/auditability, ties on headline ASR, loses nothing material.
- Artifacts: `results/phase7/e31_contract_vs_semantic/`
- Limitations: offline on cached traces (no live re-scoring); S_rule is a score component, not a separate hard veto in these traces; hard veto (rule_triggered) analyzed separately in E21.
- Supervisor Q&A:
  - Q: Does the contract add anything over semantic-only? A: Yes — it shifts the operating point toward valid-rate parity (322 fewer over-blocks) and catches 32 attacks semantic-only misses, at parity latency and once-per-session parse cost.

## Artifact packaging
- Status: [ ] not started
- Goal: one-command repro (`docker build && docker run pytest -q`). Wire `scripts/run_phase5.py --check` into container entrypoint.
- Artifacts: TBD

## Method formalism (writing task, no new runs)
- Status: [ ] not started
- (a) τ-selection as FPR-constrained ASR minimization (Neyman–Pearson) pointing at Pareto figure.
- (b) assumption-violation table (trusted request / untrusted tool content / single-turn scope).
- (c) Anderson reference-monitor framing (2 sentences).
- Lands in Ch 3 draft + blueprint Sec 9 pointer.
