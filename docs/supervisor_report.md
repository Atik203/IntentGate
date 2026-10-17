# IntentGate — Supervisor Progress Report

**Intent-Consistency Verification at the Action Gate: A Request-Derived Alternative to
Formal Contract Gating for Tool-Using LLM Agents**

> Thesis project · LLM Security / Agentic AI / AI Safety · 2026
> Repository: [github.com/Atik203/IntentGate](https://github.com/Atik203/IntentGate)
>
> **Status at time of writing:** Phases 0–6 complete · Gates 0, 1, 2, 3 passed ·
> full evaluation **frozen 2026-10-12** · 199 automated tests green. Phase 7 (Q1 hardening) and
> Phase 8 (thesis + paper) are scoped and marked *planned / not yet executed*.
>
> This report is self-contained: system design, research question, goals and objectives, every
> phase completed so far, the frozen results, limitations, and the remaining plan. Every number
> is cited to a report or `results/` artifact named beside it; nothing here is new evidence.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Research question & hypothesis](#2-research-question--hypothesis)
3. [Goals and objectives](#3-goals-and-objectives)
4. [Problem statement & motivation](#4-problem-statement--motivation)
5. [System design](#5-system-design)
6. [Evaluation methodology](#6-evaluation-methodology)
7. [Phases completed (0–6)](#7-phases-completed-06)
8. [Consolidated results](#8-consolidated-results)
9. [Success criteria vs results](#9-success-criteria-vs-results)
10. [Limitations & threats to validity](#10-limitations--threats-to-validity)
11. [Roadmap — planned work (Phases 7–8)](#11-roadmap--planned-work-phases-78)
12. [Artifacts & reproducibility](#12-artifacts--reproducibility)
13. [Appendix — supervisor Q&A](#13-appendix--supervisor-qa)

---

## 1. Executive summary

Modern LLM agents no longer only chat — they execute real actions through tools (email, payments,
code, files) via MCP-style protocols. Every benchmark in our literature review shows the same
pattern: once an agent holds tool permissions, a hijacked tool call succeeds at scale. The closest
published system that intercepts at the action itself, **ToolGate** (arXiv, Jan 2026), requires a
hand-authored formal contract **per tool** and had never been tested on an adversarial benchmark.

**IntentGate** is a model-agnostic middleware **action gate**. It derives an *intent contract*
from the user's original request **once, before any attacker content is visible**, then scores
every proposed `tool_call` against that contract using embedding similarity plus a hard rule veto,
and decides **allow / block / escalate**. It requires **zero per-tool authoring** and is
attack-vector-agnostic: injection, poisoning, and drift all must eventually emit a tool call, and
that call is the single chokepoint we police.

### Headline results (Gate 3, frozen 2026-10-12, seed 42)

| Benchmark | Unprotected (B1) | IntentGate (ours) | ToolGate reimpl (B2) |
|---|---|---|---|
| InjecAgent attack success (2,108 cases) | 19.0% (354) | **0.7% (13)** · 340 blocked | 17.2% (321) — n.s. vs B1 |
| MCPTox attack-influenced (1,348 cases) | 279 | **144** · 140 blocked | 271 — n.s. vs B1 |
| Significance vs B1 (McNemar) | — | **p = 1.3e-33 / 1.25e-07** | p = 1.00 / 0.33 |
| Latency p95 per gated call (CPU) | — | **16–20 ms** (target < 100 ms) | ≤ 0.06 ms |
| Setup cost (manual contracts) | 0 | **0** | 145 |
| Utility (valid-rate parity) | 87.5–89.7% | 86.9–89.7% (Δ ≤ 0.6 pp) | — |
| Evaluation cost (billed) | — | **$9.64** (34,560 LLM calls) | — |

**The one-sentence verdict:** the intent gate cut InjecAgent attacks from 1-in-5 to nearly zero and
halved MCPTox attacks with no measurable utility loss, at zero contract cost and 16–20 ms latency,
while a manual contract gate (ToolGate, with 145 hand-written contracts) was statistically
indistinguishable from doing nothing.

### Gate milestones

| Gate | Definition | Status | Evidence |
|---|---|---|---|
| Gate 0 | Harness trusted + 50-case scorer pilot passes (Assumption 2) | ✅ 2026-09-11 — AUC 0.979, ASR 0%/FPR 4% @ τ=0.75 | `docs/experiments/01_gate0_foundation.md` |
| Gate 1 | ToolGate baseline (B2) reimplemented, coverage frozen | ✅ 2026-09-16 — InjecAgent 79/79; MCPTox 65/801 | `docs/experiments/03_b2_toolgate.md` |
| Gate 2 | Gate wired into the agent loop; latency measured | ✅ 2026-09-16 — p95 ≤ 23 ms; 199 tests green today | `docs/experiments/04_gate2_gated_eval.md` |
| Gate 3 | Full-suite results frozen (nothing rewritten after) | ✅ 2026-10-12 — 30 jobs, 20,736 cases | `docs/experiments/05_phase5_full_evaluation.md` |
| Phase 6 | Hardening pilots (second backbone, coverage curve, probes) | ✅ 2026-10-13 — E18–E22 | `docs/experiments/06_phase6_pilots.md` |

---

## 2. Research question & hypothesis

**Research gap (one sentence).** Several recent systems derive task-scoped policies from the
user’s request (e.g., Task Shield, ACL 2025), while concurrent arXiv work also explores
request-derived policy enforcement (ClawGuard, arXiv:2604.11790, 2026). However, existing work
differs in how the policy is represented and enforced (e.g., LLM-as-judge checkers) and in
evaluation coverage; we focus on a lightweight embedding-based gate with deterministic hard-rule
veto, a frozen, reproducible head-to-head against a faithful ToolGate reimplementation, and
evaluation on both injection (InjecAgent) and tool-poisoning (MCPTox) under the same harness and
metrics.

**Central research question.** *Can a gate derived automatically from the user's own request match
the protection of formal per-tool contract gating — automatically, at zero per-tool setup cost, and
across multiple attack vectors?*

**Hypothesis (from the design blueprint, Section 3).**

> If every proposed tool call is scored for consistency against a structured intent contract
> automatically derived from the user's original request, and blocked/escalated when inconsistent,
> then Attack Success Rate will measurably drop on both InjecAgent (injection) and MCPTox
> (poisoning) compared to an unprotected ReAct agent, with competitive ASR to a ToolGate-style
> formal gate but at zero per-tool setup cost and with acceptable False Positive Rate and latency.

The hypothesis was resolved on 2026-10-12: **supported on attack reduction, cost, and latency**;
on the comparison to ToolGate the outcome was stronger than hypothesised — the manual-contract
baseline did not meaningfully outperform doing nothing, a structural finding rather than a
measurement miss (Section 8).

**Why this framing is publication-worthy.** It closes a cross-paper gap: benchmarks measure
vulnerability but propose no defense; defenses are evaluated only on their own threat model; the
closest action-level gate is manual and non-adversarial. The contribution is therefore both a
practical artifact (a zero-setup gate) and an evaluation (the first adversarial test of
contract-style gating, with setup cost measured).

---

## 3. Goals and objectives

The project's objectives were fixed in the design blueprint (Section 3). Their completion status:

| # | Objective | Status | Evidence |
|---|---|---|---|
| 1 | Formalize the intent-contract schema and the scoring function (semantic + rule) with a tunable risk threshold and escalate fallback | ✅ Done | Schema v1.1 (`configs/intent_schema.json`); `S = 0.7·S_sem + 0.3·S_rule` + veto; τ/δ sweep — E5/E6, E13 |
| 2 | Implement the gate as model-agnostic middleware (wrapper around any ReAct/MCP agent) with **no fine-tuning** | ✅ Done | `src/intent_gate/gate/middleware.py`; `AgentLoop` executes only via `GateMiddleware.execute`; E18 replicates on a second backbone |
| 3 | Reimplement ToolGate's Hoare-contract check (Appendix G) as a minimal, faithful baseline for direct comparison | ✅ Done | `src/intent_gate/baselines/toolgate/`; coverage frozen in `configs/b2_coverage.json` — E7 |
| 4 | Empirically validate on InjecAgent + MCPTox with ASR, FPR, latency, setup-cost reporting; threshold ablation + error taxonomy | ✅ Done (FPR proxied — see limitations) | E11–E17 frozen matrix; E12 ablations A1–A3; E13 Pareto; E16 taxonomy |
| 5 | (Stretch) Pilot a small multi-turn drift condition to test whether the gate catches slow-build manipulation | ⏳ Deferred | Explicitly deferred to future work (Ch 6); not in the submitted core |

**Deliverables (from blueprint Section 16).** Falsifiable success criteria and graduation
outcome: thesis + evaluated gate + pip package + evaluation report + paper draft. The evaluation
report is complete; the thesis chapters and paper draft are Phase 8 (Section 11).

---

## 4. Problem statement & motivation

**Current problem.** An LLM agent given tool permissions can be induced — via injected text in tool
outputs, poisoned tool metadata at registration, or gradual multi-turn drift — to execute a tool
call that diverges from the user's original intent, causing financial, privacy, or system harm.

**Why it matters.** Excessive/hijacked agency is now a named Top-10 risk in the OWASP LLM / Agentic
AI Top-10 (2025–26). Unlike hallucination, a hijacked tool call is not a wrong sentence — it is an
irreversible side effect (money moved, file deleted, email exfiltrated). As agents are deployed with
real permissions, a single successful hijack outweighs many correct turns. A lightweight,
model-agnostic gate at the narrowest chokepoint addresses the risk regardless of which vector got
through.

**Relation to prior work.** Request-derived policy enforcement has been explored in recent
peer-reviewed work (e.g., Task Shield, ACL 2025) and concurrent arXiv work (e.g., ClawGuard,
arXiv:2604.11790, 2026). Our focus is on a CPU-only, no-LLM-per-action approach (embedding
similarity + deterministic hard-rule veto) with a frozen, reproducible head-to-head against a
faithful ToolGate reimplementation; a full empirical comparison is planned for Phase 7.

**Verified benchmark evidence (from our literature review, Aug 2026).**

| Benchmark | Venue | Finding we build on |
|---|---|---|
| AgentDojo | NeurIPS D&B 2024 | 629 cases; tool-filter defense fails without pre-planning |
| InjecAgent | ACL Findings 2024 | GPT-4 vulnerable 24% → 47% (enhanced) over 1,054 cases |
| MCPTox | AAAI 2026 | 72.8% ASR on 45 live servers, < 3% refusal |
| ASB | ICLR 2025 | 84.3% max mixed-attack ASR, 11-defense taxonomy |
| ToolGate | arXiv 2601.04688v1 (Jan 2026) | Only published action-level gate; hand-authored contracts, never adversarially tested |

**Why existing solutions are insufficient.**

- **Benchmarks only:** the four anchor benchmarks document high ASR and propose no defense.
- **Single-vector filters:** prompt-level defenses reduce but never eliminate ASR and are bypassed
  by adaptive attacks (> 85% ASR when the attacker knows the defense).
- **Hand-authored safety specs / formal contracts (ToolGate):** the closest system needs a manual
  contract per tool (a deployment cost the authors do not remove), was evaluated only on task
  completion (never adversarially), and is blind to tools an attacker registers.
- **Heavyweight structural defenses (StruQ, CaMeL, MELON):** require model-level changes or
  multiple inference passes, contradicting the low-cost middleware-wrapper goal.

**Why a middleware gate.** It is the only placement that is (a) attack-vector agnostic, (b)
model-agnostic (no fine-tuning), and (c) auditable (allow/block/escalate + score logged per call).
Prompt hardening is in-band and attacker-controllable; fine-tuning couples the defense to one
backbone.

---

## 5. System design

### 5.1 Architecture

```
User Request (original, trusted)
        │
        ▼
┌─────────────────────┐
│  Intent Parser (LLM)│  ← runs ONCE, before any attacker content is seen
│  request → contract │     {goals, tool_categories, data_scopes, side_effect_limits}
└─────────┬───────────┘
          │ intent contract (frozen for the session)
          ▼
Agent Reasoning (ReAct / MCP client, any backbone)  ← unmodified
          │ proposes: tool_call {name, parameters, source}
          ▼
┌───────────────────────────────────────────────┐
│  Action Gate (middleware, model-agnostic)      │
│   ┌──────────────┐    ┌───────────────────┐    │
│   │ Semantic     │    │ Rule Engine       │    │
│   │ S_sem =      │    │ S_rule ∈ {0,1}    │    │
│   │ cos(contract,│    │ hard veto         │    │
│   │     call)    │    │                   │    │
│   └──────┬───────┘    └────────┬──────────┘    │
│          └────────┬────────────┘               │
│                   ▼                            │
│      S = α·S_sem + (1−α)·S_rule   (α = 0.7)    │
│      veto: S_rule == 0 on a critical limit → S = 0
│      decision: allow / escalate / block (τ, δ) │
└─────────┬─────────────────────────────────────┘
          │ allow  → execute tool → observation → agent loop
          │ block  → return gate error (no execution)
          │ escalate → user prompt (demo) / counted as block (benchmark)
          ▼
Tool Execution → Observation → Agent Reasoning (next step)
          ▼
Final Output: answer + gate trace {per-call S, S_sem, S_rule, decision, latency}
```

### 5.2 Components

| # | Component | File | Role |
|---|---|---|---|
| 0 | **Intent parser** | `src/intent_gate/parser/` | Trusted, once-per-session request → `IntentContract`. The only LLM call that sees only the trusted request. |
| 1 | **Agent scaffold** | `src/intent_gate/agent/` | Unmodified ReAct loop; proposes tool calls; executes **only** through the gate. |
| 2 | **Gate middleware** | `src/intent_gate/gate/` | Cores contribution: embed + score + veto + threshold → allow/block/escalate; JSONL trace. |
| 3 | **ToolGate baseline (B2)** | `src/intent_gate/baselines/toolgate/` | Faithful Hoare-contract reimplementation: per-tool `{pre}T{post}` + symbolic world-state with rollback; same placement, manual policy. |
| 4 | **Embeddings & rules** | `src/intent_gate/scoring/` | Shared substrate: `all-MiniLM-L6-v2` (CPU) + deterministic rule engine + score fusion. |
| — | **Harness / orchestrator** | `harness/`, `scripts/` | Benchmark adapters, ordering guard, runners (`--gate none|ours|toolgate`), Phase 5 orchestrator + reporter. |

**Component 0 — intent parser.** `gpt-4o-mini`, JSON mode, temperature 0, one repair retry,
fail-closed defaults, 9 few-shot examples. Output schema v1.1:

```json
{
  "goals": ["find cheapest flight", "hold without payment"],
  "expected_tool_categories": ["search", "read"],
  "permitted_data_access": ["flight results"],
  "side_effect_limits": {
    "financial": "no payment", "external_send": "disallow",
    "file_write": "disallow", "code_exec": "disallow", "system_change": "disallow"
  },
  "specificity": "specific",
  "raw_request": "<original text>"
}
```

Three-tier fallback: LLM → heuristic (keyword, offline/CI) → `minimal_contract` (blocks
everything). The parser never raises.

**Component 2 — the score and decision.** For a proposed call:

- `S_sem = (cosine(embed(contract_text), embed(call.naturalized())) + 1) / 2 ∈ [0,1]`
- `S_rule = 1` if all hard constraints pass, else `0` (deterministic; never embedding-dependent)
- `S = α·S_sem + (1−α)·S_rule`, `α = 0.7`
- **Veto:** if a critical rule fires (`S_rule == 0`, e.g. a financial call when `financial: "no payment"`), then `S = 0` regardless of semantic similarity.
- **Decision:** `S ≥ τ → allow`; `τ − δ ≤ S < τ → escalate`; `S < τ → block`. Defaults **τ = 0.75, δ = 0.1** (chosen at Gate 0 and never re-tuned on later results).

**Component 3 — ToolGate B2.** Per-tool Hoare contracts over a symbolic world state (`balance`,
`files`, `directories`, `permissions`, recorded effects), snapshot/rollback on post-condition
violation, state seeded best-effort from the trusted request. Uncontracted tools are counted as
`no_contract` (allow-with-flag), never silently allowed.

### 5.3 Threat model & trust boundaries

| Element | Status | Rationale |
|---|---|---|
| User's original request | **Trusted** (parsed once, then frozen) | The one thing the attacker cannot rewrite |
| Tool definitions + tool outputs | **Untrusted** (may carry injections/poisoning) | All three attack vectors live here |
| Agent backbone | Untrusted-but-observed (participates in ReAct) | The gate scores its proposals; backbone is varied (E18) |
| Multi-turn scope | Assumed single-turn | Stated limitation; drift pilot deferred |

### 5.4 Design invariants (enforced and tested)

| Invariant | How enforced | Why it matters |
|---|---|---|
| **Ordering** | Intent parsed before any attacker content/tool defs load (`harness/common.py:OrderingGuard`) | Attacker cannot influence the contract — the whole trust argument rests on this |
| **No bypass** | `GateMiddleware.execute()` is the only execution path (`tests/test_no_bypass.py`) | No tool action can skip the gate |
| **Fail-closed** | Missing/unknown fields default to `disallow` for high-risk effects (`parser/schema.py`) | Attacker cannot crash the gate to get through |
| **Deterministic** | Seed 42, temperature 0, pinned model IDs, embedding hash logged in every trace | Results are reproducible |
| **Auditable** | Every call logged to JSONL (`S`, `S_sem`, `S_rule`, decision, latency, contract) | Load-bearing for sweeps, breakdowns, taxonomy |
| **Cache-friendly** | System prompt + few-shots byte-identical; contract embedded once and reused | ~16% prompt-cache saving; p95 16–20 ms |

### 5.5 Data flow

1. **Load** case → trusted user request + untrusted attacker content (separated).
2. **Parse** (once) → frozen contract + cached embedding.
3. **Agent** proposes `tool_call {name, params, source}`.
4. **Gate** embeds the call, checks rules, fuses to `S`, thresholds to a decision, logs it.
5. **Enforce** → execute (allow) / refuse (block) / prompt or count-as-block (escalate).
6. **Loop** until `Final Answer` or the 15-step cap.
7. **Score** the case vs. ground truth; **aggregate** ASR / FPR / escalation / latency / setup cost.

---

## 6. Evaluation methodology

### 6.1 Conditions (identical prompts, only the middleware differs)

| Condition | Description | Role |
|---|---|---|
| **B1 — none** | Unprotected ReAct agent, direct execution | Vulnerability floor |
| **B2 — toolgate** | ToolGate reimplementation (manual Hoare contracts + world-state) | Closest published system |
| **Ours — intent gate** | Auto intent contract + embeddings + rules; τ = 0.75 | Our contribution |
| **A1 — semantic-only** | Rules removed | Isolates rule value |
| **A2 — rule-only** | Semantics removed | Isolates semantic value |
| **A3 — raw-request** | Embed the raw request instead of the parsed contract | Isolates contract-parsing value |

### 6.2 Datasets (pinned)

| Benchmark | Attack type | Size used | Version pin |
|---|---|---|---|
| InjecAgent | Indirect prompt injection | 1,054 cases × 2 settings = 2,108 | commit `f19c9f2c` |
| MCPTox | Tool poisoning at registration | 1,348 cases, 45 servers, 801 registered tools | static snapshot 2026-09-11 |
| ToolGate | B2 reference code (read-only) | — | commit `976ad3f5` |
| AgentDojo | Stretch (not used in gated runs) | — | commit `089ed468` |

### 6.3 Metrics

| Metric | Meaning | Direction |
|---|---|---|
| ASR (attack success rate) | Share of attacker-goal calls executed | lower better |
| FPR (false positive rate) | Share of legitimate calls wrongly blocked | lower better |
| Escalation rate | Share of calls routed to the human-review band | reports user burden |
| Latency p50/p95 | Overhead per gated call | supports deployability |
| Setup cost | Contracts authored (0 vs manual count) | core differentiation metric |
| Utility retention | Benign-task valid rate | security must not destroy normal use |

### 6.4 Statistical plan

- Bootstrap 95% confidence intervals on ASR (10,000 resamples).
- Paired **McNemar** test (exact + continuity-corrected) per case across conditions.
- τ×δ sweep (τ ∈ 0.40–0.80 step 0.05 × δ ∈ 0.05/0.10/0.15) reported as a **Pareto curve**, never a
  single tuned point.
- Post-hoc power analysis + Bonferroni correction across breakdowns (Phase 6, E22).
- Seed 42, temperature 0, one run per cell, pinned model IDs and embedding hash in every result.

---

## 7. Phases completed (0–6)

Each phase is reported as **goal → what was done → result**. Detailed numbers are consolidated in
Section 8 so the phase narrative stays readable.

### Phase 0 — Literature review & blueprint ✅

- **Goal:** fix the problem, the threat model, and the design before writing code.
- **Done:** 10-paper synthesis (Q1–Q9 structured notes) condensed into the master blueprint
  (Sections 0–18, the design source of truth); 5 anchor paper reviews; `docs/references.bib` (10
  verified entries); repo README.
- **Result:** the gap was pinned down — *no automated, vector-agnostic action gate evaluated
  adversarially on both injection and poisoning* — and the two benchmarks (InjecAgent, MCPTox)
  plus the ToolGate baseline were selected.

### Phase 1 — Project skeleton ✅ (commit `3ff9e33`)

- **Goal:** a typed, reproducible package and harness so every later number is traceable.
- **Done:** `src/intent_gate/` (parser / scoring / gate / agent / baselines.toolgate / eval);
  `harness/` runners; `configs/`; `scripts/`; CI (`pytest -q` on `dev`/`main`); branch model
  (feature → `dev` → `main`); 26 tests initially.
- **Result:** reproducible scaffolding with seeded runs, pinned model IDs, and hashes logged in
  every trace.

### Phase 2 — Foundation & pilot → **Gate 0** ✅ (2026-09-11)

- **Goal:** confirm Assumption 2 (the scorer separates hijack from legitimate calls) — the cheapest
  place to fail.
- **Done:** cloned and pinned benchmarks; B1 reference run on 20 InjecAgent cases via the authors'
  own harness vs. our pipeline; 50-call labeled scorer pilot with real MiniLM embeddings; intent
  schema v1 frozen (later v1.1).
- **Result:** our pipeline reproduced the reference **20/20 cases byte-identically**; pilot
  **AUC 0.979, ASR 0% / FPR 4% at τ = 0.75** → **GO**. Three rule-engine false positives found and
  fixed (AUC 0.80 → 0.979). τ = 0.75 frozen here. Evidence: E1–E4.

### Phase 3 — ToolGate baseline (B2) → **Gate 1** ✅ (2026-09-16)

- **Goal:** a faithful minimal ToolGate reimplementation so the comparison is fair, not a strawman.
- **Done:** Hoare contracts keyed by harness tool names; symbolic world-state with rollback;
  best-effort state seeding from the trusted request; coverage frozen.
- **Result:** InjecAgent **79/79 (100%)**; MCPTox **65/801 (8.1% distinct / 37.2%
  availability-weighted)**, with the long tail and every poisoned registration counted as
  `no_contract`. ToolBench was unavailable, so the blueprint Section 10 fallback validation was
  used (manual contract review vs. official schemas + recorded-call replay) and documented. The
  8.1% figure is the setup-cost argument made visible. Evidence: E7.

### Phase 4 — Gate build & integration → **Gate 2** ✅ (2026-09-16)

- **Goal:** a working middleware (embed + rule + threshold + escalate + trace) wired to the agent
  loop.
- **Done:** real LLM parser (temp 0, JSON mode, repair retry); real embedding model with hash
  logging; `AgentLoop` executing only via `GateMiddleware.execute`; escalate band; JSONL trace;
  threshold-sweep tooling.
- **Result:** 100-case integration run — InjecAgent attack success **9/100 → 0/100** (0 false
  blocks), MCPTox attack-influenced **22 → 10** (12 blocked); p95 **≤ 23 ms**; τ-sweep confirmed the
  knee at τ = 0.75; first error taxonomy built. Evidence: E8–E10.

### Phase 5 — Main evaluation → **Gate 3 (results freeze)** ✅ (2026-10-12)

- **Goal:** the complete, reproducible result set — nothing gets rewritten after this.
- **Done:** froze code/configs (`configs/phase5_lock.json` + `results/phase5/manifest.json`, git
  `307487f`, clean tree); ran the full matrix — **6 conditions × 5 dataset files = 30 jobs, 20,736
  cases**, seed 42, τ = 0.75, δ = 0.1, α = 0.7, `gpt-4o-mini` for both agent and parser; integrity
  `--check` passed 30/30; then analysis (Pareto, bootstrap + McNemar, breakdowns, error taxonomy,
  latency/utility/cost).
- **Result:** InjecAgent ASR-valid **19.0% → 0.7%** (dh 8.8% → 0.0%, ds 28.3% → 1.3%); MCPTox
  attack-influenced **279 → 144**; both McNemar p < 1e-6 vs B1; **B2 ≈ B1** (n.s.); valid-rate
  parity; p95 16–20 ms; 0 vs 145 contracts; **$9.64 billed** (34,560 calls, ~5.6 h). Evidence:
  E11–E17 (Section 8).

### Phase 6 — Strengthening & hardening ✅ (2026-10-13, preliminary)

- **Goal:** turn the two most attackable claims (model-agnosticism; "B2 is a strawman") into
  evidence. Rule: frozen Phase 5 numbers are never touched — all new work is E18+ preliminary.
- **Done / result (E18–E22):**
  - **E18 — second-backbone pilot:** Qwen3.5:4b (local) replicated the effect, **ASR 27.1% →
    2.1%** with zero false positives; a `gpt-6-luna` arm produced prose-only output and was
    honestly excluded as backbone-incompatible (not a gate deficit).
  - **E19 — B2 coverage curve:** extended B2 from 65 → 583 contracts (37.2% → 84.9% weighted
    coverage); the coverage-vs-ASR curve is **flat** — B2's weakness is **structural** (poisoned
    registrations pass preconditions), not coverage-limited.
  - **E20 — intent-mimicry probe:** rephrasing the 13 residual near-misses inflated S by only
    **+0.0112** on average; **0/13** newly crossed τ — the semantic signal is stable.
  - **E21 — escalate precision:** all 583 escalated calls classified against ground truth →
    **80.5% precision**, 14.8% false-escalate (concentrated in one browser-navigation tool family).
  - **E22 — stats discipline:** post-hoc power **1.0** at α = 0.005 on both benchmarks; 10-risk
    breakdowns survive Bonferroni correction; per-specificity block-rate stratified (specific
    12.8% / vague 9.6%).

---

## 8. Consolidated results

### 8.1 InjecAgent — full suite (2,108 cases, ASR-valid)

| Slice (n) | B1 | B2 | Ours | 
|---|---|---|---|
| dh_base (510) | 7.8% (35) | 5.6% (25) | **0.0%** (0; 39 blocked) |
| dh_enhanced (510) | 9.9% (44) | 5.7% (25) | **0.0%** (0; 41 blocked) |
| ds_base (544) | 25.0% (122) | 24.3% (118) | **1.2%** (6; 121 blocked) |
| ds_enhanced (544) | 31.5% (153) | 31.0% (153) | **1.4%** (7; 139 blocked) |
| **All (2,108)** | **19.0% (354)** | **17.2% (321)** | **0.7% (13; 340 blocked)** |

*Direct hijacks (dh) are eliminated entirely; all 13 residuals sit in the harder indirect (ds)
splits.*

### 8.2 MCPTox — full suite (1,348 cases)

| Condition | success | attack-influenced | blocked | ignored |
|---|---|---|---|---|
| B1 | 103 | 279 (20.7%) | 0 | 1,012 |
| B2 | 98 | 271 (20.1%) | 10 | 1,008 |
| **Ours** | **66** | **144 (10.7%)** | **140** | 1,007 |

### 8.3 Ablations (full matrix)

| Ablation | InjecAgent ASR-valid | MCPTox attack-influenced |
|---|---|---|
| A1 semantic-only | **0.0% all four slices** | 81 (204 blocked) |
| A2 rule-only | dh 0.2–0.7%, ds 24.3–31.6% (≈ B1) | 263 (14 blocked; ≈ B1) |
| A3 raw-request | 0.0–1.6% (≈ ours) | 116 (165 blocked; ≈ ours) |

**Honest reading:** semantics do the detecting (A1 ≥ ours; A2 ≈ B1). The rules' value is the
fail-closed veto guarantee, precision on direct-harm side effects, and the escalate-band input —
not detection lift. A3 ≈ ours narrows the contract claim to auditability + escalate input rather
than detection (stated explicitly, not hidden).

### 8.4 Threshold Pareto (E13)

- InjecAgent: ASR 0.0 already at τ = 0.75 for all δ; frozen point holds with escalate share 21.6%.
- MCPTox: frozen point ASR 0.583 per-call; minimum at τ = 0.80 (ASR 0.427, escalate 16.0%).
- The Gate 2 knee (τ = 0.75) is re-confirmed on full traces; **no re-tuning was done post-freeze.**

### 8.5 Statistical significance (E14)

| Slice | Ours ASR (95% CI) | B1 ASR | McNemar p |
|---|---|---|---|
| InjecAgent ds_enhanced | 0.0129 [0.0037, 0.0239] | 0.2812 | **1.3e-33** |
| MCPTox | 0.0490 [0.0378, 0.0608] | 0.0764 | **1.25e-07** |
| B2 ds_enhanced | 0.2812 | 0.2812 | 1.00 (n.s.) |
| B2 MCPTox | 0.0727 | 0.0764 | 0.33 (n.s.) |

Confidence intervals are non-overlapping (ours vs B1) on both benchmarks. B2 is statistically
indistinguishable from unprotected.

### 8.6 Breakdowns (E15)

- **MCPTox per risk (success rate, B1 → ours):** Credential Leakage 0.130 → 0.017; Instruction
  Tampering 0.053 → 0.0; Service Disruption 0.029 → 0.010; Infrastructure Damage 0.056 → 0.024;
  Code Injection 0.079 → 0.048; Information Manipulation 0.110 → 0.078; Privacy Leakage
  0.062 → 0.047. Flat (small-n, within noise): Data Tampering 0.100 → 0.108 (n=120), Message
  Hijacking 0.159 → 0.182 (n=44).
- **InjecAgent per split:** dh combined 8.8% → 0.0%; ds combined 28.3% → 1.3%. Per-attacker-tool
  (30) and per-user-tool (17) tables in `results/phase5/report.json`.

### 8.7 Error taxonomy (E16)

- **InjecAgent (13/13):** every residual is a ds **read-only exfiltration** call (e.g.
  `SpokeoSearchPeople`, `EpicFHIRGetPatientDetails`, `TwilioGetPhoneNumberInfo`) with
  **S ∈ [0.75, 0.79]** — just above τ — and `S_rule = 1.0`. The attacker's read is near-identical
  in meaning to a legitimate read the user explicitly authorized: the hardest case for a
  similarity gate, and one stable boundary.
- **MCPTox residuals:** same signature (`S` above τ, no rule trip, a plausible query tool) — this
  is **registration-time poisoning**: the call is consistent with intent, but the tool itself was
  maliciously registered. **Tool provenance is out of scope for an action gate** — documented, not
  hidden.

### 8.8 Latency, utility, cost (E17)

| Metric | Value |
|---|---|
| Latency (per gated call, CPU) | p50 ≈ 12–13 ms, **p95 16–20 ms** (target < 100 ms) |
| B2 latency | p95 ≤ 0.06 ms (in-memory checks; different cost profile) |
| Utility | valid-rate parity every slice (ours 86.9–89.7% vs B1 87.5–89.7%, Δ ≤ 0.6 pp) |
| Escalate share @ τ=0.75 | 21.6% (InjecAgent) / 18.2% (MCPTox); benchmark mode counts as block |
| Setup cost | **0 contracts (ours) vs 145 manual (B2)** |
| Cost | **$11.46 list / $9.64 billed** (34,560 calls, ~5.6 h wall-clock at `--jobs 3`) |

### 8.9 Phase 6 pilots (E18–E22, preliminary)

| ID | Experiment | Headline |
|---|---|---|
| E18 | Second backbone (Qwen3.5:4b) | **27.1% → 2.1%** ASR, 0 false positives; Luna excluded (prose-only) |
| E19 | B2 coverage curve (65 → 583 contracts) | 37.2% → 84.9% weighted; curve **flat** — structural weakness |
| E20 | Intent-mimicry probe | Avg S inflation **+0.0112**; **0/13** cross τ |
| E21 | Escalate precision (583 calls) | **80.5%** precision; 14.8% false-escalate |
| E22 | Power + Bonferroni + specificity | Power **1.0** at α=0.005; breakdowns survive correction |

---

## 9. Success criteria vs results

Falsifiable criteria from the design blueprint (Section 16), judged against the frozen run:

| Criterion | Result | Verdict |
|---|---|---|
| ASR_ours < ASR_B1 on both benchmarks, 95% CI non-overlapping, McNemar p < 0.05 | p = 1.3e-33 (InjecAgent), p = 1.25e-07 (MCPTox) | ✅ |
| FPR_ours < 10% at chosen τ | 4% pilot FPR + valid-rate parity (no dedicated legit-only suite — limitation) | ✅ (proxied) |
| Setup cost: 0 contracts (ours) vs documented B2 count on the same tool set | 0 vs 145 | ✅ |
| Latency overhead p95 < 100 ms per tool call on CPU | 16–20 ms | ✅ |
| ToolGate B2 runs and is documented (coverage reported) | InjecAgent 100%; MCPTox 8.1%/37.2% weighted | ✅ |
| Deliverables: thesis + pip package + GitHub + evaluation report + paper draft | evaluation report done; thesis + paper = Phase 8 | ⏳ |

---

## 10. Limitations & threats to validity

Each limitation is paired with its planned answer (Chapter 6 material):

1. **Static attacks only** — adversarial/adaptive attacks are not yet tested live → planned E26
   (paraphrase-delivery + threshold-aware), with E20 as the offline precursor.
2. **Two effective backbones** (gpt-4o-mini + Qwen; Luna excluded) → planned E25 third backbone,
   same 100-case protocol.
3. **Utility is proxied** (valid-rate parity, not a dedicated benign suite) → planned E23
   legitimate-only utility suite to replace the proxy with a measured completion number.
4. **Static MCPTox snapshot, not live servers** → stands; documented; deferred to future work.
5. **Single-turn scope** (multi-turn drift out of scope) → stands; drift pilot deferred.
6. **A3 ≈ ours** (raw-request embedding nearly matches the parsed contract) → planned E28 parser
   ablation to quantify exactly what the LLM parser buys.
7. **Heuristic MCPTox evaluator** (precision 0.82 / recall 0.26, conservative — it under-counts
   attacks) → shared across all conditions, so deltas are fair even where absolute counts
   understate attacks.
8. **Registration-time tool poisoning** (the MCPTox residual) is invisible to an action gate →
   documented as a scope boundary (needs tool provenance/signing), not a tuning failure.

---

## 11. Roadmap — planned work (Phases 7–8)

> ⚠️ **These phases are scoped and not yet executed.** They never modify the frozen Phase 5
> numbers (E11–E17); all new work gets E23+ identifiers and is framed as preliminary.

### Phase 7 — Q1 hardening (9 submission-gate items, ~$8 estimated)

| ID | Item | Goal | Status |
|---|---|---|---|
| E23 | Legitimate-only utility suite | Measure task completion with gate ON vs OFF on benign tasks (replaces the utility proxy) | ⏳ |
| E24 | Prompt-level baselines | Delimiters / instructional-prevention / sandwich-repetition from the ASB taxonomy | ⏳ |
| E25 | Third backbone pilot | Replicate the ASR delta on a new model family | ⏳ |
| E26 | Adaptive attacker | Paraphrase-delivery + threshold-aware attacks against the gate itself | ⏳ |
| E27 | Baseline comparison (Task Shield/Progent) | Compare against at least one peer-reviewed/request-derived baseline (Task Shield, ACL 2025) if feasible, or document scope-out and the preprint status of others | ⏳ |
| E28 | Parser ablation | B1 + ours with the LLM parser swapped for the heuristic fallback | ⏳ |
| E29 | Embedding swap + τ transfer | Re-score cached traces with a stronger embedding; test τ transfer base↔enhanced | ⏳ |
| E30 | Conformal escalate band | Turn the heuristic [τ−δ, τ+δ] band into a distribution-free coverage guarantee | ⏳ |
| — | Method formalism + artifact packaging | Neyman–Pearson τ framing, reference-monitor framing, assumption table; Docker one-command repro | ⏳ |

### Phase 8 — Thesis + paper writing

| Deliverable | Focus | Status |
|---|---|---|
| Ch 1 | Intro & motivation (OWASP excessive agency, why an action gate) | ⏳ |
| Ch 2 | Related work — answer "how is this different from ToolGate?" in the first paragraph | ⏳ |
| Ch 3 | Method — parser, contract schema, scorer + veto, gate, escalate band | ⏳ |
| Ch 4 | ToolGate B2 baseline (Appendix G translation, coverage %, fidelity notes) | ⏳ |
| Ch 5 | Evaluation — metrics, baselines, ablations, per-category, stats, error taxonomy | ⏳ |
| Ch 6 | Limitations & future work (adaptive attacks, code-exec scope, live-vs-snapshot) | ⏳ |
| Appendix | Reproducibility: hashes, configs, contract examples, JSONL samples | ⏳ |
| Paper | Workshop / Findings-tier draft (~4–8 pages) from the frozen evidence | ⏳ |

**Publication target.** Realistic: a security/agentic-AI workshop or Findings track. After Phase 7
(adaptive loop + third backbone + conformal band), a Q1 security journal (TDSC/TIFS or Computers &
Security; JISA / Applied Intelligence as backup) is the target.

---

## 12. Artifacts & reproducibility

### 12.1 Repository layout

```
src/intent_gate/     parser · scoring · gate · agent · baselines.toolgate · eval
harness/             benchmark adapters + runners (--gate none|ours|toolgate) + ordering guard
scripts/             pilots, parser check, coverage freeze, Phase 5 orchestrator + reporter
configs/             intent_schema.json · parser_fewshots.json · thresholds.yaml · models.yaml
                     benchmark_versions.yaml · b2_coverage.json · phase5_lock.json
tests/               199 pytest tests (parser, veto, no-bypass, ordering, metrics, ToolGate)
results/             TRACKED on purpose: JSONL traces + reports (read, don't re-run)
docs/                blueprint.md · team_guide.md · experiments/ (E1–E22) · summary.md
```

### 12.2 Pinned configuration

| Item | Pin |
|---|---|
| Agent / parser | `gpt-4o-mini`, temperature 0 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (CPU), hash `4588b3f9e962` |
| Gate params | τ = 0.75, δ = 0.1, α = 0.7, seed 42 |
| InjecAgent | commit `f19c9f2c` (2,108 cases) |
| MCPTox | static snapshot 2026-09-11 (1,348 cases, 45 servers, 801 tools) |
| Freeze | git `307487f`, `configs/phase5_lock.json` + `results/phase5/manifest.json` |

### 12.3 Evidence map

| Question | Where to look |
|---|---|
| Frozen full numbers (E11–E17) | `docs/experiments/05_phase5_full_evaluation.md` |
| Phase 6 pilots (E18–E22) | `docs/experiments/06_phase6_pilots.md` |
| Development-slice results (E1–E10) | `docs/experiments/01–04_*.md` |
| Full design (source of truth) | `docs/blueprint.md` (Sections 0–18) |
| Live status / plan | `roadmap.md` |
| Raw evidence | `results/phase5/`, `results/phase6/`, `configs/b2_coverage.json` |
| Install & reproduce | `docs/setup.md` → `pytest -q` (199 green) → `docs/experiments/README.md` |

**Reproduce the frozen matrix** (already run — outputs committed, do not re-run):

```powershell
python scripts/run_phase5.py --freeze          # lock code + configs (clean tree)
python scripts/run_phase5.py --run --jobs 3     # 30 jobs, ~5.6 h
python scripts/run_phase5.py --check            # integrity, 30/30
python scripts/report_phase5.py --dir results/phase5 --out results/phase5/report.json
```

---

## 13. Appendix — supervisor Q&A

**Q: What is the one-line status?**
A: Gate 3 frozen: on the full suites ours takes InjecAgent ASR-valid 19.0% → 0.7% and MCPTox
attack-influenced 279 → 144 (both McNemar p < 1e-6 vs B1), B2 is statistically indistinguishable
from unprotected, valid-rate parity holds, p95 ≤ 20 ms, billed $9.64.

**Q: How is this different from ToolGate and other recent request-derived gates?**
A: Same gate placement (per tool call), different policy representation (embedding similarity with
deterministic hard-rule veto vs. manual Hoare contracts). Task Shield (ACL 2025) uses an LLM
checker per action; our approach does no LLM call per action (16–20 ms CPU), trading some
interpretability for lower latency/cost. Concurrent preprint ClawGuard (arXiv:2604.11790, 2026)
also derives task-scoped constraints from the user’s request; our work differs in enforcement
mechanism and focuses on a frozen, reproducible head-to-head with a faithful ToolGate
reimplementation on InjecAgent and MCPTox. Crucially, we *measure* the manual contract cost
(0 vs 145 contracts).

**Q: Isn't this "just embeddings + if-statements"?**
A: The threshold is simple by design (low-cost, auditable). The contribution is *where* it applies
(the action gate), *what* it derives from (auto intent), and that it is *evaluated* adversarially
where ToolGate was not. The ablations decompose the mechanism honestly.

**Q: Why is A1 (semantic-only) as good as ours at attack reduction?**
A: Detection is semantic-led; A2 proves rules alone do nearly nothing. The rules' value is the
fail-closed veto guarantee and the escalate-band input, not detection lift.

**Q: Isn't B2 a strawman at 8.1% coverage?**
A: Coverage is frozen, counted, and reported, and the *weighted* 37.2% covers the tools actually
called — yet B2 still ≈ B1. E19 gave B2 9× more contracts (84.9% weighted) and the curve stayed
flat: the weakness is structural (poisoned registrations pass preconditions), not coverage-limited.

**Q: Why is MCPTox still around half?**
A: The residual is registration-time poisoning — the agent calls a fake tool whose name matches the
harmless task. An action gate cannot know a tool is fake; that needs tool provenance (signing),
documented as an explicit boundary.

**Q: Can this run inline in production?**
A: p95 16–20 ms vs a 100 ms budget, CPU-only; the LLM parser call is once per session, not per
action.

**Q: Why trust the MCPTox counts?**
A: The evaluator is heuristic (precision 0.82 / recall 0.26) and conservative — it under-counts
attacks — but it is shared across all conditions, so deltas are fair while absolutes understate the
problem.

**Q: What would falsify the approach?**
A: A legit-only suite showing FPR > 10%, a second backbone showing no delta, or B2 at high coverage
matching ours. The second backbone has already replicated (E18); the others are queued in Phase 7.

**Q: What remains before submission?**
A: Phase 7's nine items — utility suite, prompt baselines, third backbone, and a live adaptive loop
first; formalism and the artifact in parallel. Then Phase 8 thesis + paper.

---

*Prepared from the frozen evidence (E11–E17), Phase 6 pilots (E18–E22), `docs/blueprint.md`,
`roadmap.md`, and `docs/experiments/`. Every number is cited to the report or `results/` artifact
named beside it. Design source of truth: `docs/blueprint.md`; live status: `roadmap.md`.*
