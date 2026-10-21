# 📄 Paper #5 — ToolGate

![Paper](https://img.shields.io/badge/Paper-%235-1f6feb?style=for-the-badge)
![Role](https://img.shields.io/badge/Role-Closest%20(System)-e57373?style=for-the-badge)
![Threat](https://img.shields.io/badge/Threat%20to%20Novelty-High-ff6b6b?style=for-the-badge)
![Venue](https://img.shields.io/badge/Venue-arXiv%202601.04688v1%20(AAAI%202026%20submission)-6e40c9?style=for-the-badge)
![Verified](https://img.shields.io/badge/Verified-2026--08--24-8957e5?style=for-the-badge)

> *Verified via full paper text (arXiv html 2601.04688v1, 52k chars + Appendix G formal derivations).*

> **Historical v1 review (2026-08-24):** Its original novelty and future-work language is superseded
> by the Phase 8 literature audit. Do not reuse claims that ToolGate is the only action gate, that
> related work has no request-derived policy, or that this project is the first adversarial test.

Paper Title:
ToolGate: Contract-Grounded and Verified Tool Execution for LLMs

Authors & Year:
Liu et al. — 2026 (arXiv 2601.04688v1, Jan 2026)

Link:
arXiv: https://arxiv.org/abs/2601.04688
Code: https://github.com/OceannTwT/ToolGate

Summary:
ToolGate is a forward-execution framework that replaces natural-language reasoning about *when to call tools* with formal Hoare-style contracts. It maintains an explicit typed symbolic state *S = {(k,v,type)}* representing trusted world information, and formalizes each tool as `{P} T {Q}` where precondition *P* gates invocation (is *S ⊨ P*?) and postcondition *Q* gates commitment (does tool result *r* satisfy *Q* and type-correctly update *S* via deterministic update operator?). A retrieval-reranking front end (Qwen3-embedding-0.6B + Qwen3-Reranker-0.6B, Top-k) shrinks thousands of tools to candidates, then contracts filter candidates to a logically valid policy (renormalized) and verification gates state updates — unverified results are discarded, not propagated. Trajectory-level safety is proved (if all contracts sound and *S₀ ⊨ Inv*, every reachable trajectory is safe, Eq 21). Evaluated on ToolBench (16,464 APIs, 49 categories, G1/G2/G3) and MCP-Universe (231 tasks on 11 real MCP servers, 6 domains with Format/Static/Dynamic evaluators), ToolGate is best across 4 LLM backbones (Qwen3-235B, DeepSeek V3.2, GPT-5.2, Gemini 3 Pro) — e.g., GPT-5.2 G1 85.5/83.5 (Pass/Win) vs ToolChain* 82.8/80, MCP-Universe avg 57.0 vs 51.5 — with more concise trajectories. Ablations show Hoare is the driver: w/o Hoare 37.6% MCP-Avg vs DFSDT 38.3% (worse), removing pre-check −10.8% vs post-check −4.5%; fine-grained rejection is 29.4% (17.6% pre: 8.4% hallucination, 5.1% schema, 4.1% dependency; 11.8% post: 6.3% empty, 3.7% semantic, 1.8% state). The paper does not evaluate on any adversarial benchmark (InjecAgent, MCPTox, AgentDojo, ASB) and requires hand-authored logical predicates per tool.

Relevant to Our Idea:
ToolGate is a **closest system and the B2 baseline** — a contract-grounded gate that sits before tool execution. It is the direct precedent reimplemented per Appendix G. Its use of hand-authored Hoare contracts and its reported evaluation differ from the tested IntentGate v1 setup, but those differences alone do not establish a novel contribution. The earlier statement that this project would be the first to test contract-style gating on InjecAgent and MCPTox is superseded: the journal study must update the comparison against task-derived and runtime authorization systems, then describe only the measured benchmark coverage and distinctions.

Gap / Limitation Noted in Paper:
Per §6/Limitations: scope is text/structured only (no multimodal, no long-chain multi-step collaborative tasks); static evaluation that does not capture live API dynamics (latency, rate limits, fluctuating data); metrics are quantitative only (need qualitative reasoning assessment); prompt-based bias may not generalize across LLMs. From our perspective, the unaddressed gaps are the critical ones: (1) no adversarial evaluation at all — vulnerability to injection/poisoning is never measured, (2) no setup-cost metric — hand-authoring cost per tool is not quantified, and (3) no FPR/latency reporting at the gate level — only aggregate Pass/Win. Appendix G's formal derivations are provided but the repository at verification time is minimal (2 commits, no README) — fidelity of any reimplementation must be validated on ToolBench subset before adversarial runs, which we explicitly plan in Weeks 3–4.

---

## Section 2 — Expert Detailed Analysis

### Q1–Q9 Quick Reference

| # | Question | Short Answer |
|---|---|---|
| Q1 | What problem and why important? | Tool-augmented LLMs rely on implicit natural-language reasoning to decide when to call tools and whether to trust results — no formal guarantees. Leads to calling with wrong/insufficient params, committing invalid/hallucinated results, corrupting world state, and error propagation over long tool chains. Importance grows as tool counts reach thousands (retrieval challenge) and agents act on real systems. |
| Q2 | What data (source, size, splits, ethics)? | ToolBench (ToolLLM): 16,464 RapidAPI APIs, 49 categories, 126k instruction–solution pairs via DFSDT, classic set 8 envs × ~100 manually verified tasks each (7–15 tools each). MCP-Universe: 231 tasks on 11 real MCP servers across 6 domains (Web Search 55, Location Nav 45, Financial 40, Browser Auto 39, Repo Mgmt 33, 3D Design 19) with 84 evaluators (Format, Static, Dynamic). No train/test for ToolGate — evaluation-only. No human data. Ethics: public APIs/sandboxes, no PII, sandbox execution with licenses followed. |
| Q3 | What features/inputs, how engineered? | Typed symbolic state *S = {(k,v,type)}* (trusted world info). Per-tool Hoare contract `{P} T {Q}`: *P(S)* = minimal state predicate for legal call, *Q(S,r)* = structural/typing/semantic postcondition on result *r* plus how verified *r* updates *S*. Tool requirement representation *q_t* from (query, dialogue history, *S*, trajectory) → embedding retrieval (Qwen3-embedding-0.6B) → Top-k → reranker (Qwen3-Reranker-0.6B) → contract-filtered policy. No learned features beyond embeddings; contracts are hand-authored FOL predicates. |
| Q4 | What methods/models, overall pipeline? | Forward execution with probabilistic reasoning constrained by Hoare logic. Steps: (1) LLM decides to emit `TOOL_CALL` marker via *p(trigger\|query,history,S,trajectory)*, (2) build *q_t*, (3) retrieve Top-k, (4) rerank → *p_rank*, (5) precondition filter: keep only *T* where *S ⊨ P_T*, renormalize → logically valid policy, sample *T**, (6) execute → *r*, (7) postcondition acceptance *accept = 1[S⊨Q(S,r)]* (structural/typing/semantic), (8) if accept, *S' = update(S,r)* and inject `<tool_result>` into trajectory; else discard and backtrack, (9) trajectory marginalization, with global constraint that any precondition/postcondition violation → trajectory probability 0 (Eq 14). Formal derivations in Appendix G (weakest precondition, Hoare triples, soundness theorem). |
| Q5 | What baselines and why chosen? | 5 tool-learning baselines covering planning paradigms: ReAct (thought↔action loop), DFSDT (depth-first search with failure-history replanning), LATS (look-ahead tree search), ToolChain* (A* over tool chains), Tool-Planner (external planner + retrieval/filtering). Covers linear vs. search vs. planner-based. Evaluated across 4 backbones (Qwen3-235B-A22B-Instruct-2507, DeepSeek V3.2, GPT-5.2, Gemini 3 Pro) to show model-agnostic gain. |
| Q6 | How evaluated (metrics, setup, tests)? | ToolBench: Pass Rate (task completed via ToolEval) + Win Rate (LLM judge compares vs. Qwen-3-235B-ReAct, better = win). MCP-Universe: Success Rate + stability per domain (Location, Repo, Financial) with 84 evaluators (Format/Static/Dynamic). Also: ablation (w/o Hoare, w/o pre, w/o post), tool-calling steps (efficiency), fine-grained rejection distribution (pre vs. post error taxonomy). All models temp 0.2, identical instructions/tool definitions/limits, Top-k default, sandboxed MCP execution with real latency/failure signals. |
| Q7 | Key results vs baselines? | Best across all models/domains: GPT-5.2 ToolGate 85.5/83.5 (G1), 93.0/90.5 (G2), 91.8/95.3 (G3), 57.0 MCP-Avg (35.52 Loc, 45.45 Repo, 90.0 Fin) vs. best baseline ToolChain* 82.8/80, 90.5/88.3, 88.5/92.5, 51.5 (30/39.39/85) — 5–6 point MCP-Avg gain. Similar gains on other backbones (DeepSeek 72.0 vs 68.8 G1). Ablation: w/o Hoare 37.6% MCP-Avg (< DFSDT 38.3% — Hoare is the driver; search without logic is worse than DFSDT); w/o pre −10.8%, w/o post −4.5% (pre more important for efficiency, post for correctness). Rejection 29.4% (17.6% pre, 11.8% post). Efficiency: fewest tool-calling steps, near-optimal path vs. ReAct/Tool-Planner trial-and-error loops. |
| Q8 | Limitations and biases? | Text/structured only, no multimodal/long-chain collaborative tasks; static evaluation not fully capturing live API dynamics (latency, rate limits, fluctuating data); quantitative-only metrics; prompt bias across LLMs; and critically, no adversarial evaluation (injection/poisoning never tested), no setup-cost (contracts per tool) or per-gate FPR/latency reporting. Repository minimal at last check (2 commits, no README). |
| Q9 | Code/data/artifacts available? | https://github.com/OceannTwT/ToolGate (minimal at verification: 2 commits, no README, but Appendix G provides formal algorithm); ToolBench (126k pairs, 8 classic envs) and MCP-Universe (231 tasks, 11 servers) are public; Qwen3-embedding-0.6B + Qwen3-Reranker-0.6B used for retrieval. Reimplementation effort: moderate-high — must author Hoare predicates per tool and symbolic state schema; we scope to evaluated tools only and validate on ToolBench subset first. |

### 1. Publication Status & Citation

| Field | Value |
|---|---|
| **Venue** | arXiv preprint 2601.04688v1 (Jan 2026) — not yet peer-reviewed at verification; AAAI 2026 submission per anonymized repo pattern |
| **arXiv** | 2601.04688v1 |
| **Last verified** | 2026-08-24 — full html (52,041 chars) + Appendix G + GitHub live |
| **Code** | https://github.com/OceannTwT/ToolGate |

**BibTeX:**
```bibtex
@misc{liu2026toolgate,
  title={{ToolGate}: Contract-Grounded and Verified Tool Execution for {LLMs}},
  author={Liu, et al.},
  year={2026},
  eprint={2601.04688},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2601.04688},
  note={Appendix G formal derivations; evaluated on ToolBench and MCP-Universe}
}
```

### 2. Core Contribution & Method

**State representation (Eq 2):** Trusted symbolic state *S = {(k,v,type)}* — typed key-value map of verified entities, intermediate results, validated tool outputs. Predicates over *S* express existence, type consistency, invariants; *S ⊨ φ* means state satisfies formula *φ*.

**Contracts (Eq 3):** Each tool *T* has `{P_T} T {Q_T}`. *P_T(S)* is the weakest precondition for legal call — *S ⊨ P_T* must hold or tool is not executable. *Q_T(S,r)* constrains result *r*'s structure, typing, value ranges, semantic consistency, and defines how verified *r* updates *S* via deterministic `update(S,r)`.

**Execution (Eq 9–14):** Retrieval builds *q_t = f(query, history, S, trajectory)* → Top-k via cosine → rerank → *p_rank*. Contract filter: *p_valid(T) ∝ p_rank(T)·1[S⊨P_T]*, renormalized — formally, requiring *S ⊨ wp(T, true)*. Sample *T* ~ p_valid*. Execute → *r*. Acceptance *accept = 1[S⊨Q_T(S,r) ∧ well_formed(r)]* (Eq 11). If accept, *S' = update(S,r)* (Eq 12); else discard entirely (prevents contamination) and backtrack. Full trajectory probability factorizes over trigger, retrieval, ranking, filtering, sampling, acceptance (Eq 13); any violation → trajectory prob 0 (Eq 14) — global safety.

**Formal guarantees (Appendix G):** Soundness obligation (*∀S,r: S⊨P_T ∧ r=exec_T(S) → S'⊨Inv ∧ well_typed(S')*, Eq 15), Hoare derivation rule for ToolGate step, weakest-precondition correspondence (*S⊨P_T ↔ S⊨wp(T, Q)*, Eq 16), postcondition acceptance event (Eq 17–18), trajectory safety (Eq 19–20), and soundness theorem by induction: if all contracts sound and *S₀⊨Inv*, every reachable trajectory is safe (Eq 21). Concrete example instantiates a repo tool with *cwd* and *fs* keys.

**Retrieval (Eq 6–8):** Tool requirement abstraction clarifies expected output; embedding search shrinks thousands of tools to Top-k (default unspecified, ablated), reranker jointly considers reasoning context + *S* + candidate semantics.

### 3. Key Results (Extracted)

| Backbone | G1 Pass/Win | G2 Pass/Win | G3 Pass/Win | MCP-Universe (Loc / Repo / Fin / Avg) |
|---|---|---|---|---|
| **Qwen3-235B + ToolGate** | 68.3/65.5 | 82.5/78.0 | 81.0/82.3 | 18.87/21.21/60.0 / — |
| Qwen3-235B best baseline ToolChain* | 65.0/62.8 | 79.3/72.5 | 78.0/83.5 | 16.65/18.18/55.0 |
| **DeepSeek V3.2 + ToolGate** | 72.0/70.3 | 85.5/80.0 | 85.3/81.3 | 22.20/24.24/67.5 / 38.0 |
| DeepSeek best baseline ToolChain* | 68.8/65.0 | 82.5/75.3 | 81.0/88.8 | 18.87/21.21/62.5 / 34.2 |
| **GPT-5.2 + ToolGate** | 85.5/83.5 | 93.0/90.5 | 91.8/95.3 | 35.52/45.45/90.0 / 57.0 |
| GPT-5.2 best baseline ToolChain* | 82.8/80.0 | 90.5/88.3 | 88.5/92.5 | 29.97/39.39/85.0 / 51.5 |
| **Gemini 3 Pro + ToolGate** | 83.0/80.5 | 91.3/88.0 | 90.0/93.5 | 33.30/42.42/87.5 |

**Ablation (MCP-Avg, DeepSeek/GPT-5.2):** Full 38.0/57.0 → w/o Hoare 27.2/37.6 (below DFSDT 27.8/38.3) → w/o post 34.5/52.5 → w/o pre 30.9/46.2. Pre more impactful (−10.8 avg) than post (−4.5) — pre prunes statically, post rectifies logically.

**Rejection distribution (MCP-Universe, all attempts):** Total 29.4% intercepted — Pre 17.6% (Value/Entity Hallucination 8.4%, Schema/Format Violation 5.1%, State Dependency Missing 4.1%), Post 11.8% (Empty/Null 6.3%, Semantic Constraint Mismatch 3.7%, State Update Inconsistency 1.8%). Pre = efficiency (prunes invalid branches), Post = correctness (catches vacuous but "successful" outputs).

**Efficiency:** Fewest average tool-calling steps across backbones; trajectory near-optimal vs. ReAct/Tool-Planner trial-and-error loops; Hoare pruning collapses logically invalid branches.

### 4. Paper's Self-Admitted Limitations

Per §6/Limitations: (1) text/structured only — no multimodal/long-chain collaborative tasks, (2) static evaluation not capturing live dynamics (latency, rate limits, fluctuating data), (3) quantitative-only metrics — need qualitative reasoning and proactive missing-info solicitation assessment, (4) prompt-based bias across LLMs. We add: (5) no adversarial evaluation, (6) no setup-cost metric, (7) minimal repository at verification time.

### 5. Direct Comparison to Our Idea

| Dimension | ToolGate | Our Idea |
|---|---|---|
| **Problem** | Invalid/hallucinated tool calls and result corruption in complex multi-step reasoning (task completion) | Hijacked tool calls via injection/poisoning (security) — same chokepoint, different threat |
| **Gate placement** | Pre (precondition filter) + Post (postcondition acceptance) — two gates framing execution | Pre only (allow/block/escalate before execution) — post is out of scope for hijack (malicious call should not execute at all) |
| **Policy source** | Hand-authored FOL/Hoare predicates per tool over symbolic world-state *S* (typed KV map) — formal, verifiable, but manual | Auto-derived intent contract from user's request (goals, tool categories, data scopes, side-effect limits) + embedding + hard rules — informal, no world-state, but zero per-tool authoring |
| **State** | Explicit trusted *S* that evolves only via verified commits; trajectory-level safety theorem | No persistent world-state — per-call stateless check against frozen intent contract (simpler, stateless, but cannot enforce cross-call invariants like "must read before write") |
| **Evaluation** | ToolBench + MCP-Universe task completion (Pass/Win/Success) — no adversarial | InjecAgent + MCPTox adversarial (ASR/FPR) + latency + setup cost — the evaluation ToolGate never did |
| **Overhead** | Retrieval (embedding+reranker) + FOL checks + symbolic updates | Embedding + rule lookup per call — lighter, no retrieval over thousands of tools, no symbolic state maintenance |
| **Failure mode** | Rejects 29.4% logically invalid calls (hallucinated IDs, missing dependencies, empty results) — catches *capability* errors | Aims to reject hijacked calls even when they are *logically valid* (correct params, existing IDs) but *intent-inconsistent* — catches *security* errors that ToolGate's logic would allow |

**Overlap with C1 (gate mechanism):** High — same placement, same concept of gating execution with a policy. But mechanism is opposite: formal vs. intent-derived, manual vs. automatic, stateful vs. stateless, capability vs. security. No direct duplication; we reimplement ToolGate as B2 to make the comparison head-to-head.

**Historical v1 overlap note:** The v1 study added adversarial benchmark results for its ToolGate
reimplementation. That finding is bounded to this implementation and protocol; it does not establish
that IntentGate is the first adversarial test of action gating or a current journal contribution.

### 6. Historical v1 Positioning Notes (superseded for journal work)

> The statements in this section were drafted before the Phase 8 related-work audit. Do not reuse
> claims of being first or of a unique gap. The journal positioning must be based on the updated
> matrix in `literature_review/index.md` and the feature-level comparison required by `roadmap.md`.

| Role | Detail |
|---|---|
| **In our paper** | Closest (System) — High threat to novelty; baseline B2 (ToolGate reimplementation per Appendix G) |
| **How we cite** | Describe ToolGate's verified contract mechanism, reported evaluation, and assumptions; avoid unverified exclusivity or novelty language |
| **Relationship** | One of several close systems. The v1 B2 implementation is a measured baseline; its comparisons do not substitute for a Phase 8 matched study |

**Pre-emptive rebuttal paragraph** (if reviewer asks "how is this different from ToolGate?"):
> Historical v1 comparison: ToolGate uses Hoare-style contracts over symbolic state; IntentGate v1 uses a request-derived contract scored per call. The frozen v1 study reports its ToolGate reimplementation results and limitations on InjecAgent and MCPTox. These implementation and benchmark differences describe that experiment, but do not establish the journal contribution. Phase 8 must compare ToolGate and other close systems under a shared threat model where faithful implementations and compatible artifacts permit.

### 7. Code & Reproducibility

| Field | Detail |
|---|---|
| **Repo** | https://github.com/OceannTwT/ToolGate |
| **Status at verification** | Minimal (2 commits, no README/description) — usable but under-documented; committed pipeline-output JSONs suggest runnable setup |
| **Language** | Python (Hoare predicates + Qwen3-embedding-0.6B + Qwen3-Reranker-0.6B, temp 0.2) |
| **Datasets** | ToolBench (16,464 APIs, 49 categories, 126k pairs, 8 classic envs) + MCP-Universe (231 tasks, 11 real MCP servers, 84 evaluators) |
| **LLMs used** | Qwen3-235B, DeepSeek V3.2, GPT-5.2, Gemini 3 Pro |
| **Compute** | No training; retrieval + verification per step |
| **License** | Not stated — assume research-use |
| **Reimplementation effort** | Moderate-high — must translate Appendix G per evaluated tool; we scope to InjecAgent+MCPTox tool subsets and validate on ToolBench subset before adversarial runs; Appendix G provides exact algorithm but predicate authoring is manual |
| **Key challenge** | Faithful FOL predicate authoring and symbolic state schema; Appendix G formal derivations are the spec |

### 8. Cross-References

| Paper in this review | Relationship |
|---|---|
| **AgentDojo (Debenedetti et al., 2024)** | Predecessor benchmark — AgentDojo's tool filter is an informal allowlist gate; ToolGate is its formal successor (Hoare contracts). Both are gates, but AgentDojo's is evaluated adversarially (7.5% ASR) while ToolGate's is not — we bridge this by evaluating ToolGate adversarially. |
| **InjecAgent (Zhan et al., 2024)** | Evaluation substrate ToolGate never used — we will report ToolGate's ASR on InjecAgent's 1,054 cases; InjecAgent's user-case content-freedom finding (high-freedom more vulnerable) maps to ToolGate's hallucination category (8.4% value hallucination) — different error types but same need for per-call validation. |
| **MCPTox (Wang et al., 2025)** | Evaluation substrate ToolGate never used — MCPTox is live MCP servers, which overlaps with ToolGate's MCP-Universe (11 real MCP servers) but tests poisoning vs. task completion; ToolGate's retrieval over thousands of tools is directly relevant to MCP scale, but its contracts would need authoring for MCPTox's 353 tools (setup cost we count). |
| **ASB (Zhang et al., 2025)** | Superset — ASB's 27-method, 13-backbone breadth shows ToolGate's task-completion SOTA does not imply security (ASB mixed 84% ASR); ASB's formalization in §3 mirrors ToolGate's Hoare formalization in Appendix G — both use FOL, but for different stages (ASB for attacks, ToolGate for defense). |

### 9. Relevance to Thesis

★★★★★ (Critical — closest system, High threat)

**Justification:** ToolGate is the *only* published system that gates at the same point we do, with a formal alternative to our informal approach and a precise algorithm (Appendix G) we can reimplement as a fair baseline. Its SOTA task-completion results establish credibility for the "gate at the tool" idea, while its lack of adversarial evaluation and its manual per-tool cost are the exact gaps our thesis exploits: zero-setup intent vs. hand-authored contracts, and adversarial ASR vs. Pass/Win. Every team member must read §3–4 and Appendix G before Week 3, and the gate implementer must be able to explain Eq 9–14. Mandatory in related work as "the contract-grounded alternative" and in evaluation as B2.

