# Roadmap — Intent-Consistency Gate Thesis

> Tracker for the completed v1 study and planned journal extension. Single source of truth for progress: `docs/blueprint.md` (design), `roadmap.md` (status).
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
external validity. The ICEEICT manuscript completed its final pass on 2026-10-20; the active work is
the journal-strengthening study.

## Phase 8 — Journal-strengthening study (PLANNED; conference manuscript completed)

**Goal:** produce a substantially extended, independently reproducible study suitable for submission
to a reputable Q1 journal in the best-fitting category. “80%+” is an internal evidence-readiness
target, not a forecast or guarantee of acceptance; editorial fit, novelty, reviewer judgment, and
journal selectivity remain outside the team’s control. Select the journal only after checking its
current Scopus/SJR and JCR category quartiles, scope, article type, fees, and policy for extending a
conference paper.

**Study rule:** keep the published/frozen Phase 5 and Phase 7 artifacts immutable. Assign new run IDs
(E32 onward), save raw outputs and config/hash manifests under `results/phase8/`, and write each
completed experiment using the `docs/experiments/` template. Run only against benchmark fixtures and
sandboxed/simulated tools; do not send live email, modify real files, or perform external side effects.

**Provisional research questions (freeze after the related-work audit):**

- **RQ1 — Safety:** How do frozen request-derived policies compare with IntentGate v1, no gate,
  prompt-only defense, and faithful action-gate baselines on task-level unauthorized side effects
  across injection, tool poisoning, and multi-step attacks?
- **RQ2 — Utility:** How do request ambiguity, benign task complexity, and abstention/escalation
  affect end-to-end safe task completion and false intervention rates?
- **RQ3 — Policy lifecycle:** Under matched tasks, how do immutable, user-confirmed, and dynamically
  updated policies trade off safety and utility under adaptive attacks?
- **RQ4 — Generalization and cost:** How stable are the effects across model families, datasets, and
  tool schemas after accounting for refusal rates, latency, and inference cost?

**Candidate contributions (not claims until verified):** (C1) a controlled task-level comparison of
policy representation and update lifecycle under a common threat model; (C2) an argument-aware
authorization prototype evaluated against frozen v1, if the related-work audit identifies a specific
defensible difference; and (C3) a reproducible evaluation package with adjudicated labels, paired
traces, and full cost/latency reporting. Request-derived policies and argument constraints already
appear in related systems, so the project must not claim to invent either one.

**Strengthening additions A1–A7 (2026-10-22 expert review):** seven additions harden the study
toward the ~80% evidence-readiness target at a mid-tier Q1 venue. Items are tagged `[A#]` below and
priced in the model-strategy table at the end of this phase.

- **A1** — Pre-registered fallback framing if the RQ3 lifecycle comparison is null.
- **A2** — Named, released benchmark artifact (adjudicated labels + paired traces, GitHub + Zenodo DOI).
- **A3** — Formal security property plus contract-completeness measurement.
- **A4** — Optimization-based adaptive attacker (LLM hill-climb) with a local-first inner loop.
- **A5** — Explicit CaMeL handling (faithful subset arm or principled non-comparability note).
- **A6** — Venue selection bound as a hard gate before any confirmatory run.
- **A7** — Presentation package (threat-model figure, one results figure per RQ, artifact DOI on page 1).

### Sprint 0 (Oct 22–27) — run before 8.x: conference upload first, then agent-executable fast start

The manuscript is frozen and submission-ready (6 pages, both PDFs verified 2026-10-20). Nothing in
the journal study changes the conference outcome, so Part A outranks everything and takes under a
day of agent time. Part B starts Phase 8 with near-zero API spend. Human-gated items (supervisor
approval, blinded labels) are *prepared* by agents and *closed* by humans; agents must stop at the
gate and record what is pending. Suggested order: T1–T4 in parallel → T5 → T6 and T7 → T8.

**Part A — conference upload (owner: lead author; every other step agent-doable)**

- [ ] Verify the submission-system (CMT/easychair) account for all five authors; confirm the paper
  record (title/abstract/keywords) matches the PDF.
- [ ] Upload `IEEE-conference/IEEE-conference.pdf` (anonymous) as soon as the system accepts
  submissions; verify the rendered preview. Never wait for deadline day.
- [ ] Run the venue compliance check (PDF eXpress or equivalent); fix flags via patch-rebuild only.
- [ ] One non-author reads the anonymous PDF end-to-end; patch-rebuild only for blocking issues.
- [ ] Keep `IEEE-conference_authors.pdf` and the source for camera-ready; record the author build
  command.
- [ ] Record the upload receipt/screenshot under `results/phase8/conference_upload/`.
- **Done when:** the anonymous PDF is visible in the system ≥24h before the deadline.

**Part B — Phase 8 fast start (run IDs E32+ under `results/phase8/`; frozen Phase 5/7 artifacts
immutable; expected window cost ≈ $0–5)**

Global rules for every agent picking these up: activate `.venv`; keep `pytest -q` green (246
passing) before and after touching `src/` or `harness/`; keep `ruff` clean with lines ≤100; follow
the AGENTS.md cache discipline (stable prefixes, pinned model IDs, temperature 0, parser once per
session, batched embeddings); log seeds/model hashes per run; no live email, files, or side
effects. Verify every source with the web tools (hound/tavily) by fetching the real arXiv/DOI
page — never invent a title, DOI, number, or result.

- [ ] **T1 (drafts 8.0) — dated related-work matrix.** Input: `literature_review/index.md`,
  `docs/references.bib`. Create `literature_review/phase8_related_work_matrix.md`, one row per
  system (ClawGuard, CaMeL, AgentSpec, Task Shield, Progent, ToolGate + fresh 2026 search) with
  columns: trusted input / policy representation / decision point / argument and resource
  awareness / update lifecycle / user confirmation / threat model / datasets / model families /
  metrics / artifact availability / source + version + access date. Done when: every row cites a
  verified source with date and version and open gaps are listed. Cost: $0.
- [ ] **T2 (drafts 8.0) — one-page contribution statement.** Draft C1–C3 as falsifiable statements
  per Sec 19; mark claims blocked pending the audit. Done when: posted for supervisor approval —
  silence is not approval. [Human gate] Cost: $0.
- [ ] **T3 (drafts 8.1) — protocol package.** Create `docs/experiments/08_phase8_protocol.md`:
  threat model and exclusions, task-level attack-success definition, schema v2 field list (new
  file such as `configs/intent_schema_v2.json` — v1 is not mutated), annotator guide with a
  blinded labeling workflow, grouped split rules, preregistration skeleton including the A1
  fallback framing, and the analysis plan with primary/secondary outcomes. Done when: versioned;
  confirmatory runs stay blocked until human sign-off. [Human gate] Cost: $0.
- [ ] **T4 (starts 8.2) — paper-to-code audit.** Compare `IEEE-conference/IEEE-conference.tex`
  against `src/intent_gate/`: score normalization and equation, veto semantics, schema fields,
  escalate band, parser fallback, exact τ semantics. Write `docs/experiments/09_paper_code_audit.md`
  with a claim-to-code traceability table; fix discrepancies with tests or file them as issues.
  Done when: the table is complete and no mismatch is left marked must-fix. Cost: $0.
- [ ] **T5 (starts 8.2) — v2 typed argument-policy layer, feature-flagged.** Add
  `src/intent_gate/scoring/argument_policy.py`: check tool identity, operation, resource,
  destination/recipient, and argument values against the contract; the semantic score may only
  downgrade or abstain, never authorize a disallowed side effect; unknown consequential action
  fails closed or escalates. Wire as `--gate ours-v2` without changing v1 defaults; extend
  `types.py` only if required. Tests: benign paraphrase, implicit authorization, multi-action
  requests, missing fields, tool alias, schema drift, trusted-word echo, plus ordering and
  no-bypass. Done when: full `pytest -q` green including the new tests and an offline dev-slice
  replay shows a plausible safety/utility operating point. Cost: $0.
- [ ] **T6 (starts A4/8.4 prep) — E32a offline optimization-based attacker.** Add
  `scripts/e32a_adaptive_hillclimb.py`: an LLM-in-the-loop rewrite of free-text arguments that
  iteratively pushes S above τ and past the T5 checks; the inner loop runs entirely against the
  local CPU scorer (local model, or gpt-4o-mini attacker ≤$5); end-to-end verification of top-k
  survivors only if the anchor-family arm is approved. Report attacker success vs. v1 and v2 plus
  each defense's benign cost. Output: `results/phase8/e32a_adaptive/` + template write-up. Done
  when: per-case traces and the success/benign-cost table land; negative results kept. Cost: $0–5.
- [ ] **T7 (prepares RQ2) — E32b end-to-end utility on the local Qwen workhorse.** Run the deferred
  utility experiment end-to-end (task-level completion) on local Qwen across benign cases with
  arms none / v1 / v2 (v2 only if T5 is done). Numbers stay out of the conference PDF. Output:
  `results/phase8/e32b_utility/` + write-up. Done when: the task-level utility and
  false-intervention table land. Cost: $0.
- [ ] **T8 — manifests and write-ups.** Write a SHA-256 manifest plus config/hash pins for
  everything in `results/phase8/`; one `docs/experiments/` write-up per completed run; update
  `roadmap.md` checkboxes and `CHANGELOG.md` in the same commit. Done when: a teammate can
  reproduce the offline parts from the manifest alone.

**Sprint exit:** Part A uploaded ≥24h before the deadline; T1–T8 done with `pytest -q` green and
T2/T3 awaiting only human approval; no frozen artifact modified; window spend ≈ $0–5.

### 8.0 — Decide the journal claim and novelty boundary (Weeks 1–2; before new implementation)

- [ ] Build a dated related-work matrix around the closest request-derived action authorization,
  prompt-injection defense, tool-schema/contract, and agent-monitoring systems (including ClawGuard,
  CaMeL, AgentSpec, Task Shield, Progent, ToolGate, and AgentDojo) [A5]. Record each system's trusted input,
  policy representation, decision point, argument/resource awareness, threat model, datasets, and
  evaluation. Verify all sources and versions; do not treat an arXiv label or a different wording as
  novelty by itself.
- [ ] Decide whether a method contribution survives comparison with systems that already derive
  task-specific policies or check structured arguments. Prefer the lifecycle/comparative study in the
  RQs above unless the review demonstrates a concrete technical distinction. Do not treat a new schema
  or field list as novelty by itself.
- [ ] Select and bind 1–2 realistic journal candidates as a hard gate [A6]: no confirmatory run
  starts before this item is `[x]`. Verify current quartiles by the intended subject category,
  scope, article type, fees, and publication policies; record the evidence and article limits in
  the journal experiment plan. The ICEEICT paper alone is not the journal contribution: document
  the substantial new method, datasets, analyses, and results planned for the extension.
- **Exit gate:** supervisor/team approves a one-page contribution statement, closest-work table, and
  falsifiable research questions before coding or running the confirmatory test set.

### 8.1 — Lock the protocol, labels, and threat model (Weeks 2–4)

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
- [ ] Pre-register the fallback framing [A1]: if the RQ3 lifecycle comparison is null on the
  confirmatory split, the headline pivots to the measurement study + formal boundary + released
  benchmark artifact. Freeze this decision before unblinding; never choose the framing post hoc.
- **Exit gate:** protocol, annotation guide, schema, and analysis plan are versioned before any
  confirmatory test run; threshold selection is confined to development data.

### 8.2 — Implement and verify the stronger authorization method (Weeks 4–8)

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
- [ ] State and verify the formal property [A3]: under the documented observation boundary, any
  unauthorized consequential action requires either contract incompleteness or contract-internal
  ambiguity. Measure contract completeness and ambiguity on the labeled development data so the
  property has an empirical counterpart, not only a statement.
- **Exit gate:** security invariants and existing regression suite pass; blinded development results
  show the method has a plausible safety/utility operating point before confirmatory evaluation.

### 8.3 — Build a fair and useful evaluation matrix (Weeks 7–11)

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

### 8.4 — Measure end-to-end safety, utility, and cost (Weeks 10–16)

- [ ] Make task-level unauthorized side effect / attack success the primary outcome. Report both
  strict attack success and attack-influenced/tool-call rates where definitions differ, with
  hand-audited validation of any heuristic MCPTox success label.
- [ ] Report benign end-to-end task completion and safe completion, false block and false escalation
  rates, escalation precision/recall, attack-category results, coverage, and failures by tool and
  model. Call-level “allowed” rate is not a substitute for task utility.
- [ ] Evaluate adaptive attackers against the documented observation boundary: intent mimicry,
  argument substitution, destination changes, multi-turn drift, echoing trusted wording, and
  threshold-aware probing. Include both offline replay and end-to-end runs; measure the attacker's
  success and the benign cost of each defense.
- [ ] Add an optimization-based adaptive attacker [A4]: an LLM-in-the-loop hill-climb rewrites
  free-text arguments to push $S$ above $\tau$ and past the v2 typed checks. The inner loop runs
  against the local CPU scorer only ($0); top-k surviving candidates get end-to-end verification.
  Report offline and end-to-end results, the attacker's success, and each defense's benign cost.
- [ ] Measure p50/p95/p99 gate latency, end-to-end task latency, parser/agent token and monetary cost,
  throughput, memory/hardware, and setup effort. Separate model inference cost from gate overhead.
- [ ] Use paired confidence intervals clustered by independent task/request groups, appropriate paired
  tests, correction for planned multiple comparisons, and effect sizes. Report uncertainty and
  negative results; do not present a post-hoc power calculation as proof of adequate design.
- **Exit gate:** primary claim is supported on held-out tasks across datasets and meaningful model
  arms, without unacceptable benign task-completion loss. If it is not, narrow the claim and report
  the limitation rather than tuning on the test set.

### 8.5 — Reproducibility and artifact review (Weeks 15–19)

- [ ] Publish a clean artifact: pinned benchmark versions, schema/policy, configs, scripts, anonymized
  traces, metric definitions, hashes, environment/hardware details, and a one-command offline
  reproduction path. Ensure benchmark licenses and data handling permit redistribution; otherwise
  document bootstrap instructions and provide derived artifacts only.
- [ ] Package the adjudicated labels + paired traces as a named, citable benchmark artifact [A2]:
  GitHub release + Zenodo DOI, license-checked, with metric definitions and the one-command
  reproduction path. Present it as a first-class contribution, not an appendix.
- [ ] Add a clean-environment artifact check and independently reproduce a subset of the primary
  tables from saved traces. Record discrepancies and fix the artifact before manuscript submission.
- [ ] Log provider, endpoint type, exact model ID/revision, parameters, API date, retries/refusals,
  and token/cost data. Keep API keys out of traces and version control. Report unavailable models and
  failed runs rather than silently replacing them.
- **Exit gate:** a second team member can reproduce the principal tables without access to the
  original author’s machine or secrets.

### 8.6 — Write and submit the journal extension (Weeks 18–24)

- [ ] Write from the approved journal outline using `docs/prompt.md` and
  `docs/writing-guideline.md`. Include a clear threat model, formal policy/method, closest-work
  comparison, full protocol, task-level results, uncertainty, error analysis, limitations, ethics,
  and artifact availability. Keep the conference and journal claims/results traceable.
- [ ] Apply the presentation package [A7]: threat-model figure, one results figure per RQ, and the
  artifact DOI on page 1; combine with the non-implementer review below.
- [ ] Run a reviewer-style audit for claim/evidence alignment, paper/code consistency, baseline
  fairness, leakage, label validity, statistical reporting, reproducibility, and journal scope. Ask
  at least one reviewer who did not implement the gate to challenge the novelty and evaluation.
- [ ] Disclose and cite the ICEEICT version as required by the target journal; clearly identify the
  substantial new material and verify the journal’s extension and simultaneous-submission rules.
  Re-check quartile and submission requirements on the submission date.
- **Exit gate:** submit only when every primary claim has a reproducible artifact and the independent
  review has no unresolved validity or novelty blocker.

### Model strategy and cost guardrails (local-first; 2026-10-22)

Minimize API spend: local models wherever scientifically acceptable; the paid API only where frozen
comparability or attack strength requires it. Estimated budget: **minimum ~$25, expected ~$40–60,
worst case ~$100+** if the levers below are ignored. Cost basis: Gate 3 billed $9.64 for 30 jobs /
20,736 cases (~$0.47 per 1k cases).

| Arm | gpt-4o-mini (anchor, paid) | Qwen3.5:4b local (workhorse, $0) | DeepSeek (boundary, cheap) |
|---|---|---|---|
| B1 (no gate) | frozen Phase 5 reuse — no rerun | full rerun $0 | refusal/boundary doc only (~$2–5) |
| v1 (IntentGate) | frozen reuse — no rerun | full rerun $0 | skip (refuses; E25) |
| v2 (typed argument policy) | run (~$8–15) | run $0 | — |
| Prompt-only defense | run (~$5–10) | run $0 | — |
| ToolGate B2 | frozen reuse | rerun $0 | — |
| Close competitor (Progent/ClawGuard-lite) | subset run (~$5–10) | subset $0 | — |
| CaMeL [A5] | subset arm or non-comparability note ($0–10) | subset $0 | — |
| Adaptive attacker inner loop [A4] | attacker = gpt-4o-mini (~$10–20) | attacker = local $0 (weaker; report as lower bound) | attacker variant (~$2–5) if the paid attacker refuses |
| Adaptive end-to-end verification [A4] | top-k survivors only (~$5–15) | $0 | — |
| End-to-end utility | subset (~$5–10) | full $0 | — |
| Parser re-runs (contract completeness [A3]) | cached (~$1–3) | $0 | — |

Rules:

- Frozen B1/v1/B2 traces are reused, never rerun; new run IDs (E32+) only for new arms.
- Offline-first: every probe/hill-climb iteration runs against the local CPU scorer; the paid API is
  touched only by top-k end-to-end verification and anchor-family arms.
- AgentDojo: 200–300-task subset on paid families; the full set only on local Qwen.
- Qwen local is the replication/robustness workhorse ($0); headline numbers stay on the anchor
  family, and 4B results are labeled as such in every table.
- Per-arm budget caps are set before launch; billed tokens are logged in the run manifest. Kill
  rule: if an arm exceeds its cap by >50%, stop and re-scope (subset) instead of continuing.
- Existing cache discipline (AGENTS.md) applies: stable prefixes, pinned model IDs, batched
  embeddings, parser once per session, temperature 0, repair-retry only on parse failure.

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
- [x] Research deliverables: pip package + GitHub + frozen evaluation report + ICEEICT conference manuscript final pass (2026-10-20). Thesis completion is tracked separately; journal extension is Phase 8.

---

## Key Milestones (blueprint Sec 12/13)

| Gate | Definition | Status |
|---|---|---|
| Gate 0 | B1 reproduces + 50-case pilot passes (Assumption 2) | [x] 2026-09-11 — AUC 0.979, ASR 0/FPR 4% @ τ=0.75 |
| Gate 1 | B2 reimpl validated on ToolBench subset (coverage reported) | [x] 2026-09-16 — InjecAgent 79/79; MCPTox 65 contracts (37.2% availability-weighted); ToolBench not cloned → blueprint Sec 10 fallback validation (`docs/experiments/03_b2_toolgate.md`) |
| Gate 2 | Gate integrated; unit tests green; p95 latency measured | [x] 2026-09-16 — 130 tests green then (199 today); p95 ≤ 23 ms on gated calls; `docs/experiments/04_gate2_gated_eval.md` |
| Gate 3 | Results freeze (Phases 4–5 complete) | [x] 2026-10-12 — 30 jobs, 20,736 cases, InjecAgent 19.0%→0.7%, MCPTox 279→144, B2≈B1 (n.s.), p95 ≤20 ms, $9.64 billed |
| Submission | Thesis + paper draft complete | [~] paper draft final 2026-10-20; CMT upload tracked in the Phase 8 conference sprint; thesis completion separate |
