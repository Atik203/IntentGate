# IntentGate System Design Summary

## Research Question
Can a middleware action gate that automatically derives an intent contract from the user's original request match the security of formal contract gating (ToolGate) without manual per‑tool authoring, and maintain low false‑positive rate and latency across injection (InjecAgent) and poisoning (MCPTox) attacks?

## Goals & Objectives
1. Formalize an intent contract schema (goals, tool categories, data scopes, side‑effect limits) and a scoring function S = α·S_sem + (1−α)·S_rule with a tunable risk threshold τ and escalate band [τ−δ, τ].
2. Implement the gate as model‑agnostic middleware (wrapper around any ReAct/MCP agent) requiring no fine‑tuning.
3. Produce a minimal, faithful reimplementation of ToolGate’s Hoare‑contract checker (Baseline B2) for direct comparison.
4. Empirically evaluate on the full InjecAgent (2,108 cases) and MCPTox (1,348 cases) benchmarks, reporting ASR, FPR, latency, setup‑cost, and performing ablations, threshold sweeps, and error taxonomy.
5. (Stretch) Investigate multi‑turn drift and alternative backbones.

## System Overview
The gate sits between the agent’s reasoning and tool execution:

```
User Request (trusted) → Intent Parser (LLM, once) → Intent Contract (frozen)
                                                          │
Agent Reasoning (any backbone) → proposes tool_call → Gate Middleware
                                                          │
                 ┌─────────────────────┐   ┌─────────────────────┐
                 │ Semantic Similarity │   │ Rule Engine (hard)  │
                 │  (embed contract vs │   │  (financial, external │
                 │   embed tool_call)  │   │   send, file_write…) │
                 └─────────┬───────────┘   └────────┬────────────┘
                           │                        │
                           ▼                        ▼
                     Consistency Score S ∈ [0,1]  (veto: S_rule=0 → S=0)
                           │
                           ▼
               Decision: allow (S≥τ) / escalate (τ−δ≤S<τ) / block (S<τ)
                           │
         allow → execute → observation → agent
         block → return gate error → agent
         escalate → (benchmark: block+flag) / (interactive: user prompt)
```

All tool calls must pass through `GateMiddleware.execute()`; no bypass is permitted.

## Core Components
- **Intent Parser** (`src/intent_gate/parser/`): LLM (temp 0) with constrained JSON generation and schema validation; outputs a structured contract and caches its embedding.
- **Agent** (`src/intent_gate/agent/`): Unmodified ReAct/MCP client (LangChain or minimal MCP); receives observations from the gate.
- **Gate Middleware** (`src/intent_gate/gate/`): Computes semantic similarity (sentence‑transformer `all-MiniLM-L6-v2`), evaluates hard rules, fuses scores, applies threshold/escalate, logs trace (S, S_sem, S_rule, decision, latency).
- **ToolGate Baseline (B2)** (`src/intent_gate/baselines/toolgate/`): Manual Hoare contracts per tool, symbolic world‑state (`balance`, `files`, `permissions`, etc.), pre/post checks.
- **Embedding & Rule Infrastructure** (`src/intent_gate/scoring/`): Shared embedding model, rule engine, scoring utilities.
- **Orchestrator/Harness** (`harness/`): Scripts to load benchmarks, run agent‑gate loops, collect JSONL traces, and compute metrics.

## Phases Completed (per roadmap.md)

| Phase | Milestone (Gate) | Status | Key Deliverables |
|-------|------------------|--------|------------------|
| 0 | Literature Review & Blueprint | ✅ Done | `docs/blueprint.md`, `literature_review/`, `README.md` |
| 1 | Project Structure Initialization | ✅ Done | `pyproject.toml`, venv, pytest suite (26/26), repo skeleton, CI workflow |
| 2 | Foundation & Pilot (Gate 0) | ✅ Done | Benchmark clones, intent schema v1.1, 50‑case scorer pilot (AUC 0.979), parser validation |
| 3 | ToolGate B2 Baseline (Gate 1) | ✅ Done | Hoare contracts for evaluated subset (InjecAgent 79/79, MCPTox 65 contracts), symbolic world‑state, fidelity checks |
| 4 | Gate Build (Gate 2) | ✅ Done | Real LLM parser, embedding middleware, AgentLoop integration, escalate band, no‑bypass test, 100‑case integration run (ASR 9.0%→1.0%, p95 ≤23 ms) |
| 5 | Main Evaluation (Gate 3) | ✅ Done (2026‑10‑12) | Full matrix runs (B1/B2/Ours + ablations) on InjecAgent & MCPTox, τ×δ Pareto, bootstrap CIs, McNemar tests, error taxonomy, latency p95 16‑20 ms, cost ≈ $9.64 billed |
| 6 | Strengthening & Hardening | ✅ Done (2026‑10‑13) | Second‑backbone pilot (Qwen3.5, Luna), B2 coverage curve, mimicry & escalate precision probes, specificity FPR stratification |
| 7 | Q1 Hardening | In progress | Utility suite, prompt‑level baselines, third backbone, adaptive attacker, Progent comparison, method formalism, conformal band, parser ablation, embedding swap, artifact packaging |
| 8 | Thesis + Paper Writing | Not started | Chapters, workshop/Findings paper draft |

## Key Results (from Phase 5)
- **Attack Success Rate (ASR)**:
  - InjecAgent: B1 19.0% → Ours 0.7% (≈ 96 % reduction)
  - MCPTox:   B1 279 → Ours 144 (≈ 48 % reduction) *[note: raw counts shown; rates derived]*
- **False Positive Rate (FPR)**: ≈ 4 % in pilot; post‑stratification: specific 12.8 %, vague 9.6 %, overall 12.4 % (includes escalate candidates).
- **Setup Cost**: Ours 0 contracts vs. B2 145 contracts (InjecAgent 100 %, MCPTox 8.1 %/37.2 % weighted coverage).
- **Latency Overhead**: p95 16‑20 ms per tool call on CPU.
- **Statistical Significance**: McNemar p = 1.3e‑33 (InjecAgent) and p = 1.25e‑07 (MCPTox) for B1 vs. Ours.
- **Ablations**: Rule‑only and semantic‑only each degrade performance; structured intent parser (vs. raw‑request embedding) provides measurable gain.
- **Error Taxonomy**: Residual near‑misses (InjecAgent) are rule‑compliant read‑only exfiltrations; MCPTox failures stem from missing contracts (no_contract) and registration‑class poisoning.

## Conclusion
The intent‑derived middleware gate successfully reduces attack success on both injection and poisoning benchmarks while incurring negligible latency and zero manual contract authoring cost. The system satisfies the core thesis objectives and provides a solid foundation for further hardening (utility measurement, adaptive attacks, multi‑turn drift) and thesis/paper preparation.

---
*Generated from project state as of 2026‑10‑14.*