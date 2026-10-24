# Contribution Statement — IntentGate Phase 8 Journal Extension

**Status:** DRAFT v3 — PROVISIONAL. **Not approved.** Silence is not approval. Roadmap task T2 stays open
until a supervisor signs §9.
**Date:** 2026-10-24
**Inputs:** `literature_review/phase8_related_work_matrix.md` (T1 v2), `docs/experiments/08_phase8_protocol.md`
(T3 draft), `docs/experiments/09_paper_code_audit.md` (T4), `results/phase5/report.json` (frozen Gate 3),
`results/phase6/*`, `results/phase7/*`, `docs/blueprint.md` Sec 19, `roadmap.md` Phase 8.
**Wording rule:** no "first", "novel", "state of the art", or superiority wording is used as an assertion
anywhere in this document. Such wording appears only in §5, where the corresponding claims are explicitly
withdrawn, and in §7, where they are listed as prohibited.
**Structure:** §§1, 4, 5, 7 and 9 are the one-page statement required by roadmap T2. §§2, 3, 6 and 8 are an
evidence annex that supports it and is not part of the one-page text.

---

## 1. Study framing

This study compares policy representation and policy-update lifecycle across action-gate designs for
tool-using LLM agents under one task-level threat model: indirect prompt injection, tool poisoning at
registration, and multi-step argument substitution. The arms are no gate, a frozen request-derived intent
policy (IntentGate v1), a typed argument-aware extension (v2, only if justified), a prompt-only defense,
ToolGate (manual Hoare contracts, implemented as B2), and one close request-derived competitor if a
faithful implementation is affordable. The primary outcome is task-level unauthorized side effect. The
secondary outcomes are benign end-to-end completion, false block and false escalation, escalation burden,
refusal rate, latency, and cost. Comparable arms use identical agent prompts, tool definitions, task order,
model settings, and seeds. The frozen Phase 5 and Phase 7 artifacts stay immutable; new arms use run IDs
from E32 onward under `results/phase8/`.

The contribution is a controlled comparison, not a new gate. The v1 design is treated as one arm of that
comparison, and the study is designed to be able to conclude that v1 is not the best arm.

---

## 2. Annex A — Established evidence (frozen Phase 5, Gate 3, reproducible)

Every number below is traceable to `results/phase5/report.json` (30 headline rows, 10 statistical rows),
`configs/b2_coverage.json`, `results/phase6/e15_per_specificity_fpr.json`,
`results/phase6/e21_escalate_precision.json`, and `results/phase6/e19_coverage_curve.json`.
`valid` denotes valid agent outputs (the `decided` count in the report), not permitted calls.

| Established result | Value | Numerator ÷ denominator | Scope limit |
|---|---|---|---|
| InjecAgent attack success (ASR-valid) | 19.0% → 0.7% | B1 354 / 1,867 valid; ours 13 / 1,866 valid | 2,108 cases (4 slices), gpt-4o-mini, call-level, seed 42 |
| InjecAgent, ToolGate B2 | 17.2% | 321 / 1,867 valid | not distinguishable from B1: p = 1.0 (544 pairs) |
| MCPTox attack-influenced calls | 20.7% → 10.7% | B1 279 / 1,348; ours 144 / 1,348 | heuristic label, static snapshot |
| MCPTox strict attack success | 7.64% → 4.90% | B1 103 / 1,348; ours 66 / 1,348 | McNemar p = 1.25e-07 (1,348 pairs) |
| InjecAgent significance | p = 1.30e-33 | 544 paired cases (`injecagent:ds:enhanced` slice) | computed on strict success in that slice, not on the pooled 2,108 |
| Gate overhead | p95 16.3–19.8 ms, p50 12.4–12.9 ms | per-slice gated-call counts 116–1,291 (ours) | **p99 was not recorded**; gate-only, excludes parser and inference |
| Setup cost | 0 vs 145 contracts | InjecAgent 79/79 tools, MCPTox 65/801 (8.11% distinct, 37.19% availability-weighted) | extending to 583 contracts (60.9% / 84.9%) leaves attack success flat |
| Escalation mix | 60.7% attacker-tool, 14.8% user-tool, 24.5% other | 354 / 86 / 143 of 583 escalations | escalate counted as block in benchmark mode |
| Escalation precision | 80.5% | 354 / 440 classifiable escalations | different denominator from the 14.8% share |
| Block-or-escalate rate | 12.4% | 250 / 2,013 gated calls (specific 230/1,804; vague 20/209) | over **all** gated calls, not legitimate ones |
| User-tool intervention rate | 31.0% | 87 / 281 user-tool calls blocked or escalated (InjecAgent matrix) | measured in the attack matrix; a call-level rate |
| Matched user-tool proposals (E31 replay) | 35.7% vs 39.7% | full gate 71 / 199; semantic-only 79 / 199 | 0 discordant in the other direction; all 8 discordant calls sit in the band $S_{sem}\in[0.643,0.75)$ where the rule term alone lifts the fused score over $\tau$, so the gap is threshold arithmetic rather than better intent modelling. The 8 calls are one tool and two score values across 8 case rows, so no significance test is defensible |
| Semantic-only comparison | A1 0.0% InjecAgent ASR (0/1,876), 81 MCPTox attack-influenced, 102/279 = 36.6% user-tool blocks | independent runs | the full gate is **not** safer than semantic-only on these metrics |

## 3. Annex B — Preliminary evidence (Phase 6/7 pilots)

Pilot results are labeled preliminary and are not promoted to established evidence. The unit of analysis is
stated for each row because several pilots use far smaller denominators than their case counts suggest.

| Pilot | Actual scope and unit | What it does **not** establish |
|---|---|---|
| E18 second backbone (qwen3.5:4b) | 100 cases per condition (50 dh + 50 ds), base setting; B1 26/96 valid = 27.1%, ours 2/96 = 2.1%, valid 96% | not a protocol-consistent replication of the 2,108-case matrix; one model family, one metric |
| E25 third backbone (DeepSeek-V4.1-Flash) | 100 cases per condition; 0/100 attacker successes in both conditions, **0 gate blocks**, valid 96% / 97% | the gate was never exercised; a refusal ceiling, so no gate delta exists; raw rows not yet re-adjudicated |
| E23 benign utility | 50 cases per arm; only 8, 8 and 7 produced any tool call; user tool allowed in 8, 6 and 4 of 50 cases; calls blocked 0/8, 2/8, 3/7 | no end-to-end benign task completion; no utility difference can be inferred from 7–8 calls |
| E24 prompt baselines | 50 attack cases per arm; ASR 6.8% / 4.3% / 4.3% / 8.9% | prompt-only defenses, no gate, single backbone |
| E26 adaptive delivery (live) | 5 phrasings × 100 cases; gated ASR 0.0–2.2%; 2 successes total | call-level outcomes, not end-to-end; two successes establish no effect |
| E26b/E26c offline probes | 262 prevented attacker calls replayed; 34/34 free-text calls cross τ (11 templates); 6-token guard blocks 34/34 with 0 new blocks among 194 allowed user calls | an offline decision counterfactual, not execution; the guard is not wired into the gate |
| E28 parser ablation | 200 cases per condition; B1 30/168 = 17.9%; heuristic 0/169 (29 blocks); LLM 0/171 (32 blocks) | underpowered for a <1% ASR difference; establishes no parser advantage |
| E29 embedding transfer | 722 cached calls, 17 request groups (11 calibration / 6 held-out); MiniLM τ=0.70 → 39.8% / 34.9% held-out attacker pass; MPNet τ=0.76 / 0.77 → 2.3% / 0.9% | call-level replay, not end-to-end; thresholds are encoder- and direction-specific |
| E30 conformal band | 408 request groups / 2,013 calls, 204/204 split; band [0,1], coverage 1.0; heuristic δ=0.1 covers 43.1% of groups | a vacuous interval; score coverage is not a safety bound |
| E31 contract vs semantic-only | 2,013 proposals replayed; 1,712 exactly matched; 240 critical vetoes of which 28 semantic-only would allow; 332 relaxations (22 designated user-tool, 14 attacker-tool, 296 unknown-role) | call-level decision analysis, not end-to-end safety or utility |
| E14/E22 power analysis | n = 2,108 and 1,348 with the observed effect size (p1 = 0.19, p2 = 0.007), α = 0.005 → power 1.0 | a **post-hoc** calculation; it cannot justify an a-priori sample size for Phase 8 |

---

## 4. Candidate contributions (falsifiable)

### C1 — Controlled task-level comparison of policy representation and update lifecycle

**Claim (to be tested).** Under one threat model and matched tasks, tools, prompts, model settings, and
seeds, an immutable request-derived policy differs from user-confirmed and dynamically updated policies in
task-level unauthorized side effects and in benign safe completion.

**Independent variable.** Policy-update lifecycle, three arms: immutable after trusted-request parsing
(v1), user-confirmed rules induced from the request (ClawGuard-style), and runtime update with approval for
expansion (Progent-style). Plus no gate and ToolGate where coverage permits.

**Primary outcome.** Task-level unauthorized side effect per case, denominator = cases with at least one
valid attack opportunity. Inference: paired McNemar on grouped cases with cluster bootstrap confidence
intervals by independent task group, and a pre-specified family with multiple-comparison correction.

**Required evidence.** Shared-protocol runs on the same case list with human-blinded labels, at least one
model family that produces enough baseline opportunities, and grouped splits that prevent template leakage.

**Main confounders.** The approval-queue user experience differs by arm (deny-by-default in benchmark mode
versus interactive), so lifecycle and interaction are confounded unless both arms use the same policy;
per-arm latency and cost differ; rule expressiveness differs between rule-based and semantic policies.

**Falsified if.** The three lifecycle arms are not distinguishable on the primary outcome, or the ordering
reverses on more than one dataset.

**Null hypothesis.** No statistically significant difference in task-level unauthorized side effects between
immutable and dynamically updated policies under matched tasks.

**A1 fallback (fixed before unblinding).** If the lifecycle comparison is null on the confirmatory split,
the headline pivots to the measurement study, the formal boundary, and the released artifact (C3). The pivot
is decided before unblinding and never after.

### C2 — Argument-aware authorization prototype (conditional, withdrawable)

**Claim (to be tested).** A typed argument-policy layer (tool identity, operation, resource,
destination/recipient, and argument values checked against the frozen contract) reduces task-level
unauthorized side effects relative to v1 on the same tasks, at an acceptable benign completion cost.

**Withdrawal condition (binding).** C2 proceeds only if the T1 matrix identifies a specific value-level
capability that existing rule sets do not cover — for example recipient/destination value checks,
multi-action decomposition, or schema-drift handling. If the matrix does not demonstrate such a gap, C2 is
withdrawn and the implementation is reported as a comparative baseline rather than as a contribution. The
T1 matrix currently leaves this open: ClawGuard applies deterministic rules over commands, paths, and
destinations, so the candidate gaps are not yet shown to be uncovered.

**Guardrail.** The semantic score may only downgrade or abstain; it never authorizes a side effect. Unknown
consequential actions fail closed or escalate.

**Falsified if.** The typed layer does not change the primary outcome on the held-out tasks, or it does so
at a benign completion cost that exceeds the pre-registered non-inferiority margin.

### C3 — Reproducible evaluation package

**Claim (to be tested).** A named, citable benchmark artifact (GitHub release and Zenodo DOI) containing
adjudicated labels, paired per-task traces, pinned benchmark and model versions, metric definitions,
uncertainty, cost, and latency is released, and a second team member reproduces the principal tables
without the original author's machine or secrets. This contribution is independent of method novelty and is
presented as a first-class contribution, not an appendix.

**Falsified if.** The offline reproduction path fails to regenerate the principal tables, or the artifact
cannot be released under license-compatible terms.

---

## 5. Closest-work overlap and the comparability rule

ClawGuard (arXiv:2604.11790v2, revised 2026-05-11) is the nearest competitor. It already derives
task-specific constraints from the user's stated objective before any external call, enforces them
deterministically at the tool-call boundary, requires user confirmation, normalizes obfuscated arguments,
sanitizes secrets, and covers three injection channels. Task Shield (ACL 2025) reframes defense as task
alignment with a per-action LLM judge and reports ASR 2.07% at 69.79% utility on AgentDojo with GPT-4o;
its cost profile (one defender LLM call per assistant response and per tool output) is qualitatively
different from IntentGate's embedding-only gate. Progent (arXiv:2504.11703v3) derives symbolic task
policies and updates them during execution with approval for expansion. ToolGate (arXiv:2601.04688v1)
uses hand-authored Hoare contracts and is the only closest work implemented in this repository (B2).
CaMeL (arXiv:2503.18813) separates control and data flow with capability policies and reports on
AgentDojo only. AgentSpec (ICSE 2026) applies a runtime constraint DSL across agent domains (code,
embodied, autonomous driving) with a 5-part rule model; its trusted input, lifecycle, datasets, and
metrics are not recoverable from the fetched abstract alone. MELON (ICML 2025) is a re-execution
defense that compares tool calls between the original trajectory and a prompt-masked re-run; it is
evaluated on AgentDojo only and adds one model pass per action.

**Consequence.** Any claim of a first request-derived policy, a first adversarially evaluated action gate,
or novelty in middleware placement is indefensible and is withdrawn. The remaining difference is narrow and
measurable: the comparison of immutable, user-confirmed, and dynamically updated policies under one
protocol, at task level, with a released artifact. Representation (structured contract plus semantic score
plus deterministic veto) and cost (no per-action LLM, zero per-tool authoring) are descriptive differences
until shared-protocol numbers exist.

**Comparability rule.** The five-model results reported for ClawGuard are contextual related work and are
never placed in the same table as this study's numbers. They differ in model set, benchmark subsets (their
InjecAgent 544 scenarios and MCPTox 438 against this study's pinned 2,108 and 1,348), agent framework
(OpenClaw), judge (a GPT-5.4 trace judge versus benchmark evaluators), metric (defense-success and
attack-success rates versus ASR-valid and attack-influenced counts), and approval policy (deny-by-default
versus auto-block in benchmark mode). The same rule applies to Task Shield (AgentDojo only) and CaMeL
(AgentDojo only). A numerical comparison is possible only as a same-protocol arm built and run on this
study's cases, and only if a fair-comparison design and supervisor approval justify the effort.

---

## 6. Annex C — Model coverage, opportunity versus effectiveness, eligibility

**Opportunity is not effectiveness.** An *attack opportunity* is a case in which the attacker could cause an
unauthorized action. *Defense effectiveness* is the reduction in task-level unauthorized side effects among
eligible opportunities. The two are reported separately; a low attack-success number caused by refusals or
invalid outputs is not a defense result.

**Eligibility rule — PROPOSED, NOT APPROVED.** An arm qualifies for an effectiveness comparison only if, on
the same evaluation subset in the unprotected arm, there are at least 30 valid attack opportunities, at
least 10 expected attacker successes, and an invalid-plus-error rate at or below 20%. These thresholds are a
proposal, not an established standard. They require supervisor approval plus a sensitivity analysis over
alternative thresholds before they bind, because the only existing power artifact is post-hoc (§3, E14/E22).

**Refusal handling.** A model that refuses or produces invalid output is reported as a boundary result with
raw counts and no gate delta. E25 is the current example: 0/100 attacker successes in both conditions with 0
gate blocks means the gate was never exercised. Refusal rate is a reported outcome, not a safety metric.

**Qwen3.5:4B stays preliminary** unless a protocol-consistent run on the same cases, tools, prompts, order,
and seeds satisfies the eligibility rule and yields a paired interval on the primary outcome that excludes
zero. The current 27.1% → 2.1% result over 100 cases per condition is reported as preliminary and
backbone-specific.

**An additional capable model is a candidate, not a commitment.** Selection criteria, all of which must be
checked before any model is named: an independent provider family not already used; reliable ReAct tool use
with a smoke-test invalid rate at or below 10%; no systematic refusal on the benchmark; a pinned model ID
and a reachable endpoint; a cost inside the per-arm budget cap. Budget for a 200–300 case subset is
estimated at roughly $10–20 on a paid endpoint, or $0 if a local model of comparable capability is
available. No model, vendor, or price is asserted in this document.

**Uncertainty, cost, and latency reporting for every future arm.** Paired comparisons with cluster bootstrap
confidence intervals by task group; task-level safety and task-level benign completion; false block and
false escalation with explicit denominators; refusal rate; gate-only p50/p95/p99 latency; agent, parser, and
gate cost separated; per-arm budget caps with a kill rule; and a deviation log.

---

## 7. Blocked claims (must not be stated)

- First request-derived policy, action gate, or argument-constraint system.
- First adversarially tested action gate; novel middleware placement; novel embedding-plus-rule scoring.
- Universal robustness across attacks, benchmarks, or model families.
- Superiority over ClawGuard, Progent, Task Shield, ToolGate, AgentSpec, or CaMeL before shared-protocol
  results exist.
- Task-level utility parity, benign completion parity, or general defense effectiveness inferred from the
  Phase 7 call-level pilots.
- A general effectiveness claim resting on an arm with zero baseline attack opportunities.

---

## 8. Annex D — Assumptions, missing evidence, decisions required

**Assumptions.** The frozen Phase 5 protocol is a valid reference arm; AgentDojo can be licensed and
adapted; two annotators are available for blinded task-level labeling; the ClawGuard artifact can be
inspected if a faithful-lite arm is ever proposed.

**Missing evidence.** Task-level attack-success labels; end-to-end benign task completion; a
significance-tested user-tool intervention comparison (the matched replay shows the observed gap is
deterministic threshold arithmetic on two distinct call templates, so a p-value over it would be spurious —
an end-to-end benign study is the only honest substitute); powered multi-family runs; raw re-verification
of the E25 rows; full-text reviews of Task Shield, AgentSpec, and MELON (completed 2026-10-24, see
`literature_review/papers/`); a demonstrated value-level gap for C2.

**Decisions required from the supervisor.** All entries are open; none is approved.

| # | Decision | Proposed default (recommendation only) | Reason and evidence | Consequence of the alternative | Approval required |
|---|---|---|---|---|---|
| D1 | Eligibility thresholds (§6) | Keep as PROPOSED; run a sensitivity analysis over 20/30/50 opportunities before they bind | only power artifact is post-hoc at frozen scale | thresholds become a tunable knob that can hide or manufacture results | Yes |
| D2 | Whether heuristic MCPTox labels may support the primary outcome | Primary = human-adjudicated only; heuristic rates secondary with a stratified hand-audit (fraction PROPOSED) | MCPTox label is heuristic; attack calls look like legitimate queries (E19) | the primary metric inherits the weakness the journal study exists to remove | Yes |
| D3 | CaMeL handling [A5] | Principled non-comparability note; no faithful port | planner/executor split, restricted-Python interpreter, capability policies, AgentDojo only | a port consumes the sprint and still is not protocol-matched | Yes |
| D4 | ClawGuard: faithful-lite arm or contextual | Contextual for now | nearest competitor, already covers the same mechanisms; a partial arm may be neither fair nor affordable | a misleading comparison, or a delay to the upload | Yes |
| D5 | Qwen3.5:4B wording | Preliminary until a protocol-consistent, eligible run exists | 100 cases per condition, one 4B backbone, one metric | stronger wording overstates generality | Yes |
| D6 | Additional capable model | No commitment; verify access, model ID, pricing, endpoint behaviour, and smoke feasibility before naming any model | no in-repo evidence for any candidate | naming a model creates a budget and expectation that cannot be justified | Yes |
| D7 | A1 fallback framing and C1–C3 wording | Adopt as drafted; pivot fixed before unblinding | blueprint Sec 19 and roadmap 8.0 require a pre-registered pivot | post-hoc reframing invalidates the confirmatory claim | Yes |
| D8 | Unit of analysis, annotator count, agreement threshold, double-labeled fraction | Unit = trusted-request group; at least 2 annotators on at least 20% (PROPOSED); agreement threshold 0.7 (PROPOSED); third-annotator adjudication | E29 and E30 already group by hash of the raw request, so splits can align | a per-case unit reintroduces near-duplicate leakage | Yes |
| D9 | Schema v2 | Document-level design only; no `configs/intent_schema_v2.json` yet | T5 is blocked by the human gates; v1 stays frozen | a config with no consumer becomes an accidental specification | Yes |
| D10 | Fresh 2026 related-work search | **Completed 2026-10-24** — 6 searches run, 6 papers fetched and reviewed (Task Shield, AgentSpec, MELON, StruQ, TrustAgent, ClawGuard); T1 matrix updated to v2 | roadmap 8.0 required it; the T1 pending list is now closed | a novelty sentence written before the search was a retraction risk | No (completed) |

---

## 9. Sign-off

Supervisor approval line: ____________________  Date: __________

Claims remain PROVISIONAL and BLOCKED until this line is signed. Approval covers the wording of C1–C3 and
the decisions in §8; it does not authorize any confirmatory run, and the confirmatory split stays locked
until the protocol in `docs/experiments/08_phase8_protocol.md` is signed as well.
