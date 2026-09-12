# 📄 Paper #6 — TraceGrant

![Paper](https://img.shields.io/badge/Paper-%236-1f6feb?style=for-the-badge)
![Role](https://img.shields.io/badge/Role-Closest%20(System)-e57373?style=for-the-badge)
![Threat](https://img.shields.io/badge/Threat%20to%20Novelty-High-ff6b6b?style=for-the-badge)
![Venue](https://img.shields.io/badge/Venue-arXiv%202608.21126v1%20(journal%20submission)-6e40c9?style=for-the-badge)
![Verified](https://img.shields.io/badge/Verified-2026--09--12-8957e5?style=for-the-badge)

> *Verified via full paper text (arXiv 2608.21126v1, 21 Aug 2026; journal-style preprint with CRediT/funding). Local copy: `pdfs/2608.21126v1.pdf`.*

Paper Title:
TraceGrant: A Contract-Governed Security Framework for the Task-Effect Lifecycle of Networked LLM Agents

Authors & Year:
Liao et al. — 2026 (arXiv 2608.21126v1, Aug 2026)

Link:
arXiv: https://arxiv.org/abs/2608.21126

Summary:
TraceGrant is a security framework that governs the *task-effect lifecycle* of networked LLM agents through an explicit Contract. Before execution, a Semantic Contract Compiler derives a POEC Contract (**P**ermission, **O**bligation, **E**vidence, **C**ompletion) from the trusted user request and admitted tool schemas — MAY (permitted tools/operations, target scopes, argument constraints, call budgets), MUST (obligation graph over evidence acquisition, effects, output), BIND (provenance rules for authority-bearing arguments), and observable completion conditions. The candidate contract passes deterministic static analysis before becoming executable authority. During execution an Obligation Ledger tracks task state (obligations PENDING/ACTIVE/VERIFIED/WAIVED); runtime evidence is *admitted* only if it satisfies source+task-state constraints, then binds to authority-bearing arguments via typed proofs; the PDP issues a single-use Effect Certificate per authorized effect; the PEP mediates; and post-execution the Effect Receipt verifies the actual tool, canonical arguments, native result, postconditions, and provenance before an obligation closes. The Final-Answer Gate accepts the task only when every hard obligation is VERIFIED/WAIVED. Evaluated on AgentDojo (949 user/injection-task pairs) and ASB (400 attack cases) across 4 backbones (DeepSeek-V4-Flash, Gemini 3.6 Flash, Qwen3.7-Plus, GLM-5.2): **ASR 0.00% end-to-end on all four**, utility 70.57–77.32% (AgentDojo TSR) and 64.00–83.00% (ASB) — by far the strongest defense numbers we have seen in review. Also: stage ablations, targeted runtime/completion stress tests, a white-box defense-aware attack study (100 high-risk AgentDojo cases → 2.0% ASR; both success paths exploit poisoned *fields inside admitted objects*), Contract-quality analysis (reference contracts hand-built), and runtime overhead (AgentDojo mean 22.85 s→30.15 s, P95 49.4→68.4 s; ASB 24.98→35.10 s, P95 32.7→45.0 s; +1 LLM call and ~15–28% more tokens per task).

Relevant to Our Idea:
TraceGrant is the closest published system to ours — closer in *stance* than ToolGate, because it is purpose-built for indirect prompt injection (not task completion), derives its authority from the trusted user request *before* execution, and is adversarially evaluated. This is a **High-threat** paper: our old Gap Map row ("intent-consistency check at action gate → None, Novel") and our old C2 phrasing ("first adversarial evaluation of contract-style gating") are **no longer defensible** — TraceGrant already did contract-style gating on AgentDojo + ASB with 0% ASR. The surviving gap must be stated as: **TraceGrant covers AgentDojo + ASB; it never evaluates on InjecAgent or MCPTox (tool poisoning at MCP registration, 353 tools), and it uses a deterministic, stateful, provenance-bookkeeping mechanism with no graded semantic score, no threshold sweep, and no escalation band.** Our differentiators: (1) evaluation scope = two separate benchmark studies — InjecAgent (1,054 injection) and MCPTox (1,348 poisoning incl. registration-time), each reported independently, that TraceGrant does not touch; (2) continuous graded scorer S = α·S_sem + (1−α)·S_rule with τ×δ sweep → ASR–FPR Pareto and an explicit human-in-the-loop **escalate** band (TraceGrant routes nothing to a human; its resolution is exclusively deny/admit); (3) stateless per-call frozen-contract check, zero manual authoring, model-agnostic middleware vs. TraceGrant's task state, adapters, and static contract-verifier machinery; (4) we run the auto-vs-manual-contract head-to-head *on the same tool set* vs ToolGate (B2) — something TraceGrant does not do. Cost/state caveat against us: TraceGrant enforces cross-call invariants (read-before-write, budgets, completion) that our stateless check cannot; we must cite them as a stronger-but-heavier design and position our simplicity + coverage as the tradeoff.

Gap / Limitation Noted in Paper:
Self-admitted (§6.3): (1) evidence admission establishes *provenance and admissibility*, not *semantic authenticity of fields* — a poisoned object can satisfy source+BIND while containing misleading values (this is exactly the 2/100 white-box success paths: attacker IBAN/amount in a "trusted" bill/notice file); (2) BIND must cover *every* authority-bearing argument (an optional arg can still decide the effect target — rent-adjustment case); (3) evaluation limited to office/communication/travel/financial domains with structured dependencies; long-running/cross-session, multi-agent, concurrent/asynchronous execution out of scope. From our perspective: (a) no InjecAgent/MCPTox evaluation, so poisoning-at-registration and InjecAgent's tool-output injection are simply never tested; (b) contract *quality* was measured against **manually constructed reference contracts** — so not zero-setup, and the paper does not report a per-tool setup-cost metric; (c) overhead is real (~30% E2E latency, +1 LLM call/task); (d) preprint (journal submission), not yet peer-reviewed at verification.

---

## Section 2 — Expert Detailed Analysis

### Q1–Q9 Quick Reference

| # | Question | Short Answer |
|---|---|---|
| Q1 | What problem and why important? | Multistep networked tasks must read untrusted runtime content (email, docs, web) to complete, but the same content can carry indirect prompt injection that redirects tool use, substitutes recipients/accounts, expands scope, or triggers extra effects. Since the agent is a priori authorized, injected content can produce *persistent external effects*. Central question: runtime info may supply values needed by an authorized task without acquiring authority to redefine that task's effects. |
| Q2 | What data (source, size, splits, ethics)? | AgentDojo (949 user-task/injection-task pairs) + Agent Security Bench (400 attack cases), both public; plus 100-case white-box subset (53 banking, 26 workspace, 11 travel, 10 slack; 50 user tasks / 33 injection tasks) and 2,400-ASB-trajectory overall evaluation. No human-subject data; public benchmark environments. |
| Q3 | What features/inputs, how engineered? | From trusted request + admitted tool schemas: semantic contract compiler emits typed POEC Contract (MAY/MUST/BIND/completion). Authority-bearing vs. payload arguments separated. Evidence records carry source, expected type, constraints, permitted derivation. Contract statically validated before execution (deterministic normalization). |
| Q4 | What methods/models, overall pipeline? | Pre-run: Semantic Contract Compiler → static analysis → executable Contract. Runtime: evidence admission → BIND proof for each authority-bearing arg → PDP checks MAY/MUST/BIND/budget and issues **single-use Effect Certificate** → PEP invokes tool → Effect Receipt verifies (CertMatch ∧ ExecSuccess ∧ PostSatisfied ∧ ProvenanceValid) → obligation closes. Final-Answer Gate: task accepted only if all hard obligations VERIFIED/WAIVED. Four backbones (DeepSeek-V4-Flash, Gemini 3.6 Flash, Qwen3.7-Plus, GLM-5.2). No learned security model; deterministic policy. |
| Q5 | What baselines and why chosen? | NoDefense (ASR 85.28–84.00% / utility floor), Progent (programmable privilege), CaMeL (planner/executor separation), AgentSpec (behavioral specs), IsolateGPT (execution isolation), FIDES (information-flow), Task Shield (task alignment). Covers the three defense families: control-flow/isolation, policy enforcement, task alignment. |
| Q6 | How evaluated (metrics, setup, tests)? | ASR (end-to-end, native benchmark oracle), TSR/UUA (AgentDojo task-success under attack / under attack utility), plus FCR (false completion-claim rate). Stage ablations; runtime stress (fix adversarial candidate at boundary → 100% rejection, 88.6% at variant w/o completion gate); completion-integrity stress; Contract-quality eval (validity agreement vs. 97 hand-built reference contracts over all AgentDojo user tasks); white-box defense-aware attacks (100 cases, 5 targeted surfaces); runtime overhead (mean/P95 E2E latency, LLM calls, tokens). Each condition run 3×, state reset per case. |
| Q7 | Key results vs baselines? | **0.00% ASR end-to-end on both benchmarks across all 4 backbones** (baselines: NoDefense 85.28%/84.00%, Progent 73.62%/78.25%, CaMeL 75.30%/64.00%, AgentSpec 55.84%/44.25%, IsolateGPT 72.62%/57.00%, Task Shield 68.54%/63.00%). Utility: AgentDojo 77.32/73.20/73.68/70.57 (TSR) and 80.71/75.66/74.47/70.14 (UUA); ASB 83.00/70.45/64.00/82.93. Task Shield utility 57.00 (TSR); all others below TraceGrant. Stress: boundary-fixed adversarial candidates rejected 100% (88.6% without completion gate). White-box: 2/100 ASR (2.0%), both via poisoned object fields. Overhead: +32% mean E2E latency AgentDojo (22.85→30.15 s), +40% ASB (24.98→35.10 s); +1 LLM call/task. |
| Q8 | Limitations and biases? | Provenance ≠ semantic authenticity of object fields (2/100 white-box successes); BIND must cover all authority-bearing args; structured office/comm/travel/financial domains only; no multi-agent/concurrent/async/long-running; contract quality measured against manually built references (setup cost not zero, not reported as a metric). |
| Q9 | Code/data/artifacts available? | Benchmark data public; "implementation configurations and trajectory records available from corresponding author upon reasonable request" — no public repo, no pip package, no released comparator gate. |

### 1. Publication Status & Citation

| Field | Value |
|---|---|
| **Venue** | arXiv preprint 2608.21126v1 (21 Aug 2026), journal-style (CRediT authorship, funding, graphical implications) — not yet peer-reviewed at verification; no public code |
| **arXiv** | 2608.21126v1 |
| **Last verified** | 2026-09-12 — full PDF text |
| **Code** | None released |

**BibTeX:**
```bibtex
@misc{liao2026tracegrant,
  title={TraceGrant: A Contract-Governed Security Framework for the Task-Effect Lifecycle of Networked {LLM} Agents},
  author={Liao, Bohao and Wang, Jingchao and Song, Qipeng and Cao, Jin and Wang, Jieling and Deng, Boyu},
  year={2026},
  eprint={2608.21126},
  archivePrefix={arXiv},
  note={Preprint, journal submission; evaluated on AgentDojo (949) and ASB (400), ASR 0.00% across 4 backbones; no InjecAgent/MCPTox; no public code},
  url={https://arxiv.org/abs/2608.21126}
}
```

### 2. Core Contribution & Method

**POEC Contract (§4.2).** MAY = permitted tools/operations, target scope, argument constraints, call budgets. MUST = dependency-aware obligation graph (evidence acquisition, external effects, output). BIND = per authority-bearing argument: permitted source object, expected type, constraints, permitted derivation (direct/arithmetic/selection), scope. Completion conditions observable from tool results. Candidate contract is a typed IR validated by a Contract Verifier (deterministic static analysis) before becoming executable authority.

**Runtime authorization (§4.3).** Obligation Ledger holds PENDING/ACTIVE/VERIFIED/WAIVED states. Admitted Evidence Records must satisfy source + task-state + scope constraints. Each Effect Certificate is single-use and binds Contract + active obligation + canonical arguments + supporting evidence; PEP fully mediates execution. Post-execution Effect Receipt validity: `CertMatch(actual tool, canonical args) ∧ ExecSuccess ∧ PostSatisfied ∧ ProvenanceValid`. Final-Answer Gate: accept `⟺ ∀ hard obligations ∈ {VERIFIED, WAIVED}`.

**Security objectives (§3).** Task-effect confinement; evidence-constrained instantiation (runtime data fills args, never grows authority); task-state/ordering consistency; execution-backed completion. Formal threat model covers tool-selection, argument substitution, scope expansion, order violations, budget re-consumption, false success claims.

### 3. Key Results (Extracted)

| Benchmark | TraceGrant (4 backbones) | Best-utility baseline |
|---|---|---|
| AgentDojo TSR | 77.32 / 73.20 / 73.68 / 70.57 | AgentDojo best benign ~78% (Claude 3.5), Task Shield 57.00 |
| AgentDojo UUA | 80.71 / 75.66 / 74.47 / 70.14 | NoDefense 73.10 |
| AgentDojo ASR | 0.00 × 4 | NoDefense 85.28, Progent 73.62, CaMeL 75.30 |
| ASB UUA/TSR | 83.00/70.45/64.00/82.93 | Progent 68.50 (UUA), Task Shield 57.00 (TSR) |
| ASB ASR | 0.00 × 4 | NoDefense 84.00, Progent 78.25 |
| White-box (100 AgentDojo) | 2.0% ASR (2/100), resolved to constrained-execution/denial mostly | — |
| Runtime overhead | +32% mean (AgentDojo), +40% (ASB), +1 LLM call | NoDefense |

**Stress/ablations:** boundary-fixed adversarial candidates rejected 100% (88.6% without the completion gate → completion gate adds ~11 pts); FCR mechanism isolated via execution-drift and incomplete-closure fault injection.

### 4. Paper's Self-Admitted Limitations

(1) Evidence admission proves provenance/admissibility, not field-level semantic authenticity — poisoned objects can pass source+BIND with misleading values (both white-box successes). (2) BIND must cover every authority-bearing argument; optional args can still determine the effect target. (3) Evaluation limited to structured office/comm/travel/financial tasks; long-running/cross-session, multi-agent, concurrent/async out of scope. We add: (4) no InjecAgent/MCPTox; (5) contract-quality eval used manually constructed reference contracts (setup cost unmeasured); (6) no public code/repo; (7) journal-style preprint, unverified.

### 5. Direct Comparison to Our Idea

| Dimension | TraceGrant | Our Idea |
|---|---|---|
| **Problem** | Indirect prompt injection in *networked multistep* tasks; task-effect lifecycle (pre-run → runtime → completion) | Hijacked tool calls via injection *and* poisoning-at-registration — same chokepoint, narrower lifecycle (per-call gate only) |
| **Policy source** | Semantic Contract Compiler from trusted request + schemas (auto), but quality validated against *hand-built* reference contracts | Fully auto intent contract from trusted request (zero per-tool authoring), embedding + hard rules |
| **Mechanism** | Deterministic: evidence admission + BIND proof + single-use Effect Certificate + Receipt + Final-Answer Gate; stateful Obligation Ledger | Graded: S = α·S_sem + (1−α)·S_rule, τ×δ thresholding, allow/block/**escalate-to-human**; stateless frozen-contract per-call check |
| **Cross-call state** | Yes — budgets, ordering, completion (provable task closure) | No — stateless; cross-call invariants out of scope (named future work) |
| **Escalation / human-in-loop** | None — deny-or-admit only | Escalate band (δ) is a first-class decision with a user prompt in interactive mode; benchmark mode = block + `would_escalate` |
| **Evaluation** | AgentDojo (949) + ASB (400): 0.00% ASR, utility 70–83%, white-box 2.0% ASR | InjecAgent (1,054) + MCPTox (1,348, incl. 353-tool poisoning surface): ASR/FPR/latency/setup-cost, τ×δ Pareto; AgentDojo optional stretch for direct head-to-head |
| **Setup / artifacts** | Per-environment adapters + static contract verifier; manually built reference contracts for quality; no public code | Middleware pip wrapper; model-agnostic; no per-tool authoring; open-source harness |
| **Overhead** | +32–40% E2E latency, +1 LLM call/task, token-heavy | Target p95 <100 ms per tool call, CPU embedding, 0 extra LLM calls at runtime (contract cached) |

**Overlap with C1 (gate mechanism):** Very high in *stance* — TraceGrant is also "request-derived contract gates tool calls, adversarially evaluated." Differentiation is mechanism granularity (deterministic stateful provenance vs. graded stateless similarity+veto+escalate), scope (poisoning + InjecAgent coverage), and deployment (zero-setup middleware vs. ledger/adapters). We must cite TraceGrant as the strongest extant contract gate and state explicitly which benchmarks it owns.

**Overlap with C2 (evaluation):** TraceGrant owns AgentDojo + ASB. Our C2 must be narrowed to "first adversarial eval of *request-derived contract gating* as two separate benchmark studies — InjecAgent (injection) and MCPTox (incl. 353-tool registration poisoning) — with a graded scorer + escalation, each reported independently, and a head-to-head vs ToolGate on the same tool set." An optional AgentDojo-subset run would give a direct TraceGrant comparison point.

### 6. Our Positioning Strategy

| Role | Detail |
|---|---|
| **In our paper** | Closest (System) — High threat; the "contract from trusted request + adversarial eval" precedent that bounds our novelty claim |
| **How we cite** | As "the strongest published contract-governed defense (POEC contract, stateful obligation ledger, 0% ASR on AgentDojo/ASB) — but never evaluated on InjecAgent or MCPTox, denies-or-admits without any graded threshold or human-escalation band, keeps a full task-state ledger with per-environment adapters and hand-built reference contracts for quality validation, and reports 30–40% end-to-end latency overhead; our gate is the stateless, zero-setup, graded-scorer alternative that closes the poisoning + InjecAgent gap" |
| **Relationship** | Direct sibling on mechanism; complementary on evaluation set. We report on the two benchmarks where the intent-gate idea is *untested* — this is now the claim, and it must be worded as such everywhere (blueprint, roadmap, PROJECT_OVERVIEW, paper). |

**Pre-emptive rebuttal paragraph** (if reviewer asks "how is this different from TraceGrant?"):
> TraceGrant is the closest published system to ours: like ours, it derives authority from the trusted user request before execution and gates tool calls against the resulting contract, and it reports 0% ASR on AgentDojo and ASB. The difference is mechanism and coverage, not placement. TraceGrant is a deterministic, stateful provenance engine (obligation ledger, single-use effect certificates, completion gate) with per-environment adapters, static contract validation, and hand-built reference contracts for quality checks; it has no graded semantic score, no threshold sweep, and no human escalation band — every decision is a hard deny or admit. It was never evaluated on InjecAgent or on MCPTox, so tool-poisoning at MCP registration (353 tools) is outside its evidence. Our contribution is the stateless, zero-setup, graded-scorer gate (embedding + hard veto, allow/block/escalate, τ×δ ASR–FPR Pareto) evaluated head-to-head against a ToolGate reimplementation on exactly the two benchmarks TraceGrant does not cover. The two designs are complementary: TraceGrant's ledger adds cross-call guarantees at deployment cost; our gate adds graded risk scoring and human escalation at near-zero setup cost.

### 7. Code & Reproducibility

| Field | Detail |
|---|---|
| **Repo** | None released (artifacts by request) |
| **Benchmarks** | AgentDojo, Agent Security Bench (public) |
| **LLMs used** | DeepSeek-V4-Flash, Gemini 3.6 Flash, Qwen3.7-Plus, GLM-5.2 |
| **Compute** | Deterministic policy + LLM planning; no training |
| **Reimplementation effort** | High — POEC compiler, obligation ledger, PDP/PEP, receipt + completion gate, per-benchmark adapters, hand-built reference contracts. Not a realistic B3; we cite results and compete only on the shared AgentDojo space (optional stretch). |

### 8. Cross-References

| Paper in this review | Relationship |
|---|---|
| **AgentDojo (Debenedetti et al., 2024)** | TraceGrant owns AgentDojo (0% ASR). If we add an AgentDojo subset run (stretch), it is the direct TraceGrant-comparison point; otherwise we cede that benchmark explicitly. |
| **ASB (Zhang et al., 2025)** | TraceGrant owns ASB too. Same handling as AgentDojo. |
| **ToolGate (Liu et al., 2026)** | Complementary framing: ToolGate = *manual* contracts, task-completion eval only; TraceGrant = *auto* contract but stateful + AgentDojo/ASB only; ours = *auto* contract + stateless + InjecAgent/MCPTox. Three-way "same chokepoint, different policy source/state/eval" table is the related-work core. |
| **MCPTox (Wang et al., 2025)** | The poisoning surface neither TraceGrant nor ToolGate tests — our exclusive gap. |
| **InjecAgent (Zhan et al., 2024)** | The injection surface TraceGrant never touches — our second exclusive gap. |

### 9. Relevance to Thesis

★★★★★★★★★ (Critical — closest existing system, High threat, must reframe novel claim)

**Justification:** TraceGrant demonstrates the intent-contract-gating idea works adversarially with 0% ASR and good utility — validating our core thesis direction but **simultaneously eliminating our old "no one does this" claim** and demanding we narrow the novelty statement. The Gap Map row in `literature_review/index.md` and the framing in `blueprint.md` / README have already been revised (2026-09-12). Follow the TraceGrant-aware framing wherever "first"/"None"/"Novel" appears: *our gap = a graded, escalating, stateless zero-setup gate evaluated as separate studies on the two vectors TraceGrant never tests — InjecAgent and MCPTox (incl. registration-time tool poisoning) — head-to-head vs ToolGate on the same tools, each benchmark reported independently.* Mandatory reading for the whole team before Phase 3 contract authoring and before any related-work drafting.