# Roadmap — Intent-Consistency Gate Thesis

> Tracker for the thesis + paper. Single source of truth for progress: `docs/blueprint.md` (design), `roadmap.md` (status).
> Legend: `[x]` done · `[ ]` todo · `[~]` in progress · `Gate N` = blueprint Sec 12/13 milestone.
> Update this file in the same commit that completes a task.

---

## Phase 0 — Literature Review & Blueprint — DONE

- [x] 10-paper Q1–Q9 synthesis (`literature_review.md` + `literature_review/index.md`)
- [x] 5 anchor reviews in `literature_review/papers/` (AgentDojo, InjecAgent, MCPTox, ASB, ToolGate)
- [x] Master blueprint Sec 0–18 (`docs/blueprint.md` — single source of truth)
- [x] Repo `README.md` (project overview, structure, evaluation plan, quick start)

## Phases 1–7 — Completed implementation and evaluation (DONE)

This compact status summary replaces the expanded phase checklists. The detailed protocols,
artifacts, and limitations remain in the linked experiment reports and `results/`; the frozen
Phase 5 matrix is not to be overwritten by future journal studies.

| Phase | Completed outcome and evidence |
|---|---|
| 1. Project structure | Python package, harness, configs, CI, tests, repo docs, and benchmark bootstrap established. |
| 2. Foundation and pilot / Gate 0 | Pinned benchmark snapshots and schema v1.1; scorer pilot AUC 0.979, with 0% ASR / 4% FPR at τ=0.75. See `docs/experiments/01_gate0_foundation.md` and `02_parser_schema.md`. |
| 3. ToolGate B2 / Gate 1 | Manual-contract baseline implemented and evaluated with measured evaluated-tool coverage and documented fidelity limits. See `docs/experiments/`. |
| 4. Gate build / Gate 2 | Parser, scorer, hard vetoes, middleware, trace, ReAct harness, ordering guard, and no-bypass coverage delivered; test suite and latency gate recorded. |
| 5. Frozen main evaluation / Gate 3 | 20,736 cases frozen. InjecAgent ASR 19.0% → 0.7%; MCPTox attack-influenced rate 20.7% → 10.7%; B2 and utility/latency results documented in `results/` and Phase 5 reports. |
| 6. Strengthening | Qwen3.5 replication, expanded B2 coverage analysis, intent-mimicry probe, escalation precision, and statistical utilities completed. See `docs/experiments/06_phase6_pilots.md`. |
| 7. Hardening | E23–E31 utility, prompt, backbone-boundary, adaptive-call/echo, parser, embedding-transfer, conformal, formalism, and artifact studies completed. Negative and limited findings are retained with their limitations; see `results/phase7/` and `docs/experiments/`. |

**Interpretation:** these phases establish a conference-paper prototype and a reproducible baseline.
They do not, by themselves, establish journal-level novelty, robust end-to-end safety, or broad
external validity. The next study must address the open risks below before a journal submission.

## Phase 8 — Thesis + Paper Writing (merged; old Phase 7 + old Phase 8)

**Goal: finish the thesis and prepare the ICEEICT conference paper from the frozen evidence and
reported pilots. A substantially extended journal study is tracked separately in Phase 9.**

### Thesis

- [ ] Ch 1: Intro & motivation (problem, OWASP excessive agency, why action gate)
- [ ] Ch 2: Related work — answer Reviewer #2 Q#1 in first paragraph ("not just embeddings + if-statements")
- [ ] Ch 3: Method — intent parser, contract schema, scorer + veto, gate middleware, escalate band
- [ ] Ch 4: ToolGate B2 baseline (Appendix G translation, coverage %, fidelity notes)
- [ ] Ch 5: Evaluation — metrics, baselines, ablations, per-category, stats, error taxonomy
- [ ] Ch 6: Limitations & future work (adaptive attacks, code-exec scope, live-vs-snapshot)
- [ ] Reproducibility appendix: hashes, configs, contract examples, JSONL sample
- [ ] Supervisor review rounds; final defence

### Paper (ICEEICT conference submission)

- [x] Outline (2-column short paper) → COMPLETE: `IEEE-conference/IEEE-conference.tex` drafted (abstract, intro, related work, method, ToolGate baseline, evaluation, results, limitations, conclusion, LLM-usage acknowledgment); double-blind anonymized; 5 pages, compiles via pdflatex+bibtex.
- [x] Related work: ToolGate "same gate, opposite policy source" framing (blueprint Sec 18) → COMPLETE: Progent (shi2025progent) added to references + cited.
- [x] Results section: ASR/FPR/latency/setup-cost tables + Pareto + error taxonomy → COMPLETE: Table I headline results (InjecAgent 19.0%→0.7%, MCPTox 20.7%→10.7%, McNemar p=1.3e-33 / p=1.25e-07), setup cost 0 vs 145 contracts, p95 16–20 ms, error taxonomy (13 residuals), E31 contract-vs-semantic flips.
- [x] Writing guides wired: `docs/prompt.md` + `docs/writing-guideline.md` adapted for the conference template (journal-only sections noted) and linked from `AGENTS.md`.
- [x] ICEEICT final pass to submission quality (≤6 pages incl. references, 30 verified refs, vector figures, cell-grid tables, no first-person pronouns): **DONE 2026-10-18** (steps A–D + expert-review pass): 6 pages, 254 KB, Type 1 fonts only, double-blind; title covers injection + poisoning. Remaining: co-author/supervisor info (placeholders in) + CMT upload.
- [ ] Reviewer #2 checklist (blueprint Sec 18) cleared item by item
- [ ] Reproducibility package: pip wrapper + contracts + logs + one-slide "ToolGate vs Ours" table
- [ ] Journal extension: complete the evidence and manuscript gates in Phase 9; verify each target journal's current quartile, scope, and prior-publication policy before selecting it.

### Paper final reviewer-risk fixes (2026-10-20)

- [x] Novelty paragraph vs ClawGuard / Task Shield / Progent / ToolGate
- [x] Offline adaptive-echo guard + evaluation
- [x] DeepSeek boundary clarification
- [x] Paper integration (novelty + echo + DeepSeek, strict 6 pages)
- [x] Rebuild anonymous + author PDFs (strict 6 pages)
- [x] Final QA, tests, CI, promote

---

## Phase 9 — Journal-strengthening study (PLANNED; start after conference evidence is frozen)

**Goal:** produce a substantially extended, independently reproducible study suitable for submission
to a reputable Q1 journal in the best-fitting category. “80%+” is an internal evidence-readiness
target, not a forecast or guarantee of acceptance; editorial fit, novelty, reviewer judgment, and
journal selectivity remain outside the team’s control. Select the journal only after checking its
current Scopus/SJR and JCR category quartiles, scope, article type, fees, and policy for extending a
conference paper.

**Study rule:** keep the published/frozen Phase 5 and Phase 7 artifacts immutable. Assign new run IDs
(E32 onward), save raw outputs and config/hash manifests under `results/phase9/`, and write each
completed experiment using the `docs/experiments/` template. Run only against benchmark fixtures and
sandboxed/simulated tools; do not send live email, modify real files, or perform external side effects.

### 9.0 — Decide the journal claim and novelty boundary (Weeks 1–2; before new implementation)

- [ ] Build a dated related-work matrix around the closest request-derived action authorization,
  prompt-injection defense, tool-schema/contract, and agent-monitoring systems (including ClawGuard,
  AgentSpec, Task Shield, Progent, ToolGate/CaMeL, and AgentDojo). Record each system’s trusted input,
  policy representation, decision point, argument/resource awareness, threat model, datasets, and
  evaluation. Verify all sources and versions; do not treat an arXiv label or a different wording as
  novelty by itself.
- [ ] Ask whether the proposed contribution remains distinct after the comparison. Prefer a narrow,
  testable claim: a model-agnostic, request-derived action authorization monitor with typed operation,
  resource, argument/destination, data-scope, and side-effect constraints, plus a measured abstain /
  escalation policy. If this distinction cannot be demonstrated, revise the contribution before
  expanding the implementation.
- [ ] Select 1–2 realistic journal candidates only after verifying their current quartiles by the
  intended subject category and publication policies. Record the evidence and article limits in the
  journal experiment plan. The ICEEICT paper alone is not the journal contribution: document the
  substantial new method, datasets, analyses, and results planned for the extension.
- **Exit gate:** supervisor/team approves a one-page contribution statement, closest-work table, and
  falsifiable research questions before coding or running the confirmatory test set.

### 9.1 — Lock the protocol, labels, and threat model (Weeks 2–4)

- [ ] Specify attacker capabilities and exclusions: malicious user text, retrieved/tool-returned
  content, poisoned tool descriptions, benign echoed text, multi-step requests, and proposed
  consequential actions. State the trusted boundary, when parsing occurs, what the gate can observe,
  and what “attack success” means at task level.
- [ ] Define typed intent fields and decision semantics before collecting final labels: authorized
  operations, resources, argument constraints, recipients/destinations, data access, side-effect
  limits, uncertainty, and escalation. Missing or contradictory authorization for a consequential
  action must block or escalate. Freeze a versioned schema and migration note.
- [ ] Create a human labeling guide and a blinded set of trusted requests, allowed actions, forbidden
  actions, and ambiguous cases. Use at least two independent annotators for a meaningful subset,
  report agreement and adjudication, and keep test labels hidden during tuning. Do not use an LLM as
  the sole judge of success or safety.
- [ ] Pre-register hypotheses, primary/secondary outcomes, split rules, exclusion rules, seeds,
  planned comparisons, and a power/sample-size analysis based on independent task groups and pilot
  paired discordance. Split by task/request or attack template to prevent near-duplicate leakage.
- **Exit gate:** protocol, annotation guide, schema, and analysis plan are versioned before any
  confirmatory test run; threshold selection is confined to development data.

### 9.2 — Implement and verify the stronger authorization method (Weeks 4–8)

- [ ] Audit the paper against the running code first. Resolve and document the score normalization
  and equation; align names and behavior for contract fields, hard vetoes, allow/block/escalate,
  parser fallback, and the exact threshold semantics. Add a paper-to-code traceability table.
- [ ] Implement a versioned argument-aware policy layer that checks tool identity, operation,
  resource, recipient/destination, and relevant argument values against the frozen intent contract.
  Keep semantic similarity as a relevance/ambiguity signal; it must not grant an otherwise
  unauthorized side effect. Unknown consequential actions fail closed or escalate.
- [ ] Test benign paraphrases, implicit authorization, multi-action requests, missing fields, tool
  aliases, schema drift, indirect injection, poisoned descriptions, and attacker text that echoes
  trusted words. Measure whether any echo or exact-match guard rejects legitimate echoed content.
- [ ] Add ablations isolating semantic score, each rule family, typed argument checks, parser quality,
  and escalation. Test deterministic decisions, malformed inputs, ordering, trace completeness, and
  the no-bypass invariant. Do not add provenance or other mechanisms unless the novelty review and
  threat model show they are needed for the central claim.
- **Exit gate:** security invariants and existing regression suite pass; blinded development results
  show the method has a plausible safety/utility operating point before confirmatory evaluation.

### 9.3 — Build a fair and useful evaluation matrix (Weeks 7–11)

- [ ] Retain pinned InjecAgent and MCPTox comparisons, and add a dynamic/multi-turn benchmark such
  as AgentDojo plus at most one additional compatible tool/MCP attack suite after checking license,
  task format, and label quality. Report each dataset’s limitations; do not combine incompatible
  metrics into one headline number.
- [ ] Compare B1 (no defense), current IntentGate (v1), proposed typed-policy method (v2), prompt-only
  defense, ToolGate where its contract coverage permits, and one close request-derived competitor
  where a faithful implementation or reproducible artifact exists. If a competitor cannot be run
  on the same cases/tools/prompts, present it as contextual related work rather than a direct
  numerical comparison.
- [ ] Use identical agent prompts, tool definitions, task order, model settings, and seeds across
  comparable arms; change only the defense under test. Report benchmark commits, tool universe,
  evaluated-tool coverage, omitted cases, and all exclusions. Retain a raw, per-task paired record.
- [ ] Run at least three independently hosted model families only where the unprotected arm produces
  enough valid attack opportunities to exercise the gate. OpenAI, DeepSeek, and Qwen3.5 are candidate
  families; a provider refusal/zero-attack baseline is a boundary result, not evidence of gate
  effectiveness. Pin exact model IDs and API dates/versions in every run.
- **Exit gate:** matrix and comparison fairness reviewed before the final test split is unlocked.

### 9.4 — Measure end-to-end safety, utility, and cost (Weeks 10–16)

- [ ] Make task-level unauthorized side effect / attack success the primary outcome. Report both
  strict attack success and attack-influenced/tool-call rates where definitions differ, with
  hand-audited validation of any heuristic MCPTox success label.
- [ ] Report benign end-to-end task completion and safe completion, false block and false escalation
  rates, escalation precision/recall, attack-category results, coverage, and failures by tool and
  model. Call-level “allowed” rate is not a substitute for task utility.
- [ ] Evaluate adaptive attackers against the documented observation boundary: intent mimicry,
  argument substitution, destination changes, multi-turn drift, echoing trusted wording, and
  threshold-aware probing. Include both offline replay and end-to-end runs; measure the attacker’s
  success and the benign cost of each defense.
- [ ] Measure p50/p95/p99 gate latency, end-to-end task latency, parser/agent token and monetary cost,
  throughput, memory/hardware, and setup effort. Separate model inference cost from gate overhead.
- [ ] Use paired confidence intervals clustered by independent task/request groups, appropriate paired
  tests, correction for planned multiple comparisons, and effect sizes. Report uncertainty and
  negative results; do not present a post-hoc power calculation as proof of adequate design.
- **Exit gate:** primary claim is supported on held-out tasks across datasets and meaningful model
  arms, without unacceptable benign task-completion loss. If it is not, narrow the claim and report
  the limitation rather than tuning on the test set.

### 9.5 — Reproducibility and artifact review (Weeks 15–19)

- [ ] Publish a clean artifact: pinned benchmark versions, schema/policy, configs, scripts, anonymized
  traces, metric definitions, hashes, environment/hardware details, and a one-command offline
  reproduction path. Ensure benchmark licenses and data handling permit redistribution; otherwise
  document bootstrap instructions and provide derived artifacts only.
- [ ] Add a clean-environment artifact check and independently reproduce a subset of the primary
  tables from saved traces. Record discrepancies and fix the artifact before manuscript submission.
- [ ] Log provider, endpoint type, exact model ID/revision, parameters, API date, retries/refusals,
  and token/cost data. Keep API keys out of traces and version control. Report unavailable models and
  failed runs rather than silently replacing them.
- **Exit gate:** a second team member can reproduce the principal tables without access to the
  original author’s machine or secrets.

### 9.6 — Write and submit the journal extension (Weeks 18–24)

- [ ] Write from the approved journal outline using `docs/prompt.md` and
  `docs/writing-guideline.md`. Include a clear threat model, formal policy/method, closest-work
  comparison, full protocol, task-level results, uncertainty, error analysis, limitations, ethics,
  and artifact availability. Keep the conference and journal claims/results traceable.
- [ ] Run a reviewer-style audit for claim/evidence alignment, paper/code consistency, baseline
  fairness, leakage, label validity, statistical reporting, reproducibility, and journal scope. Ask
  at least one reviewer who did not implement the gate to challenge the novelty and evaluation.
- [ ] Disclose and cite the ICEEICT version as required by the target journal; clearly identify the
  substantial new material and verify the journal’s extension and simultaneous-submission rules.
  Re-check quartile and submission requirements on the submission date.
- **Exit gate:** submit only when every primary claim has a reproducible artifact and the independent
  review has no unresolved validity or novelty blocker.

### Provider setup for controlled model comparisons

`.env.example` already exposes the generic agent/parser endpoint overrides, Qwen-compatible endpoint,
DeepSeek settings, and model IDs. Do not put provider keys in tracked configs or traces; never copy
secrets into this roadmap. Use one provider/model per experimental arm, pin the exact model ID, and
keep the parser endpoint fixed (or explicitly vary it as a separate factor). CLI values override
`.env` values. Leave the real `.env` unchanged until running an authorized experiment.

| Arm | `.env` setup | Run guidance |
|---|---|---|
| OpenAI | Set `OPENAI_API_KEY`; `AGENT_MODEL_ID` and `PARSER_MODEL_ID` to the exact supported model IDs. Leave endpoint overrides empty for the default OpenAI endpoint. | Run the same harness command/cases used for other arms; save resolved IDs and settings in the run manifest. |
| DeepSeek | Set `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, and `DEEPSEEK_MODEL` for the pinned model. For the general harness, route the agent with `AGENT_BASE_URL` / `AGENT_API_KEY` and the CLI model-name option; keep parser on OpenAI unless intentionally testing parser choice. | Use `--agent-reasoning-effort none` for the documented DeepSeek thinking-mode behavior. Confirm the actual endpoint and model in metadata; a DeepSeek arm that refuses every attack cannot estimate gate efficacy. |
| Qwen3.5 via Ollama/OpenAI-compatible server | Start the pinned Qwen3.5 model/server; set `QWEN_BASE_URL` to its `/v1` endpoint and `QWEN_API_KEY` as required by that server (often a local placeholder). Set the exact model/tag via `AGENT_MODEL_ID` or the CLI model-name option. | Use `--agent-reasoning-effort none` for the documented Qwen3.5 compatibility issue. Confirm context length, quantization, server version, and resolved model tag; keep parser separately pinned. |

For any provider, `AGENT_BASE_URL` / `AGENT_API_KEY` are the explicit agent overrides;
`PARSER_BASE_URL` / `PARSER_API_KEY` independently route the parser. The legacy `QWEN_*` endpoint is
an agent fallback only. `PARSER_MODEL_ID` sets the parser model ID. Run an inexpensive connectivity
and output-format smoke check on development cases, then use pinned settings on development data;
never change endpoint/model midway through a paired run. Add a new `.env.example` variable only if
an implementation gap is found; this plan does not require new secrets or a real `.env` edit.

---

## Success Criteria (blueprint Sec 16 — falsifiable)

- [x] ASR_ours < ASR_B1 on both InjecAgent and MCPTox, 95% CI non-overlapping (McNemar p < 0.05) — p=1.3e-33 / p=1.25e-07 (E14)
- [x] FPR_ours < 10% at chosen τ (or <5% hard-block, escalate counted separately) — proxy: 4% pilot FPR + valid-rate parity (E15)
- [x] Setup cost: 0 contracts for ours vs. documented manual count for B2 on same tool set — 0 vs 145
- [x] Latency overhead p95 < 100ms per tool call on CPU — 16–20 ms (E17)
- [x] ToolGate B2 runs and is documented (coverage % reported) — InjecAgent 100%, MCPTox 8.1%/37.2% (E11/E15)
- [ ] Deliverables: thesis + pip package + GitHub + evaluation report + paper draft

---

## Key Milestones (blueprint Sec 12/13)

| Gate | Definition | Status |
|---|---|---|
| Gate 0 | B1 reproduces + 50-case pilot passes (Assumption 2) | [x] 2026-09-11 — AUC 0.979, ASR 0/FPR 4% @ τ=0.75 |
| Gate 1 | B2 reimpl validated on ToolBench subset (coverage reported) | [x] 2026-09-16 — InjecAgent 79/79; MCPTox 65 contracts (37.2% availability-weighted); ToolBench not cloned → blueprint Sec 10 fallback validation (`docs/experiments/03_b2_toolgate.md`) |
| Gate 2 | Gate integrated; unit tests green; p95 latency measured | [x] 2026-09-16 — 130 tests green then (199 today); p95 ≤ 23 ms on gated calls; `docs/experiments/04_gate2_gated_eval.md` |
| Gate 3 | Results freeze (Phases 4–5 complete) | [x] 2026-10-12 — 30 jobs, 20,736 cases, InjecAgent 19.0%→0.7%, MCPTox 279→144, B2≈B1 (n.s.), p95 ≤20 ms, $9.64 billed |
| Submission | Thesis + paper draft complete | [ ] |
