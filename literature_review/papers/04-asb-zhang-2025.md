# 📄 Paper #4 — Agent Security Bench (ASB)

![Paper](https://img.shields.io/badge/Paper-%234-1f6feb?style=for-the-badge)
![Role](https://img.shields.io/badge/Role-Anchor%20(Benchmark)-2ea043?style=for-the-badge)
![Threat](https://img.shields.io/badge/Threat%20to%20Novelty-Low-2ea043?style=for-the-badge)
![Venue](https://img.shields.io/badge/Venue-ICLR%202025-6e40c9?style=for-the-badge)
![Verified](https://img.shields.io/badge/Verified-2026--08--24-8957e5?style=for-the-badge)

> *Verified via full paper text (arXiv html 2410.02644v4).*

Paper Title:
Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents

Authors & Year:
Zhang, Huang, Mei, Yao, Wang, Zhan, Wang, Zhang — 2025 (arXiv 2410.02644v4, ICLR 2025)

Link:
arXiv: https://arxiv.org/abs/2410.02644
Code: https://github.com/agiresearch/ASB
Website: https://luckfort.github.io/ASBench/

Summary:
ASB is the first comprehensive benchmark that formalizes and jointly evaluates attacks and defenses across *all* operational stages of an LLM agent — system prompt, user prompt, tool usage, and memory retrieval — rather than isolating one vector. It defines 10 scenarios (e-commerce, autonomous driving, finance, etc.), 10 corresponding ReAct agents, 400+ tools (20 normal + 400 attack tools, no params for simplicity), 400 tasks (aggressive vs. non-aggressive), and 27 attack/defense methods with 7 metrics. Attack families are Direct Prompt Injection (DPI, 5 phrasings), Indirect Prompt Injection (IPI, same 5 via observation), Memory Poisoning (black-box RAG poisoning, no embedder internals), a novel training-free Plan-of-Thought (PoT) Backdoor (poisoned PoT demonstrations in system prompt + trigger in user query), and 4 Mixed attacks (DPI+IPI+Memory). 11 defenses are mapped per attack (Delimiters, Instructional Prevention, Sandwich Prevention, Paraphrasing, Dynamic Prompt Rewriting, Shuffle, PPL/LLM-based detection). Evaluated across 13 LLM backbones, the highest average ASR is 84.30% (Mixed Attack), DPI averages 72.68%, IPI 27.55%, Memory Poisoning 7.92%; defenses are largely inadequate (e.g., even the best DPI defense, Dynamic Prompt Rewriting, still leaves 44.45% ASR; IPI defenses leave ~25–28% ASR) and often hurt benign utility. The paper also shows a rise-then-fall utility-vs-ASR curve (capable models easier to hijack until refusals kick in), that agent PNA is generally < backbone leaderboard quality, and introduces Net Resilient Performance (NRP = PNA × (1 − ASR)) to balance utility and security — Claude 3.5 Sonnet (NRP 43.56) and Llama3-70B (30.03) rank highest. All formalizations are given as probabilistic definitions with explicit adversarial goals per attack.

Relevant to Our Idea:
ASB is our broadest anchor — it proves single-vector defenses are insufficient because mixed attacks (84.3% ASR) compound vectors we would otherwise handle separately. Our gate, at the tool-call chokepoint, is vector-agnostic across DPI/IPI (user prompt vs. observation) but ASB shows future work must also handle memory poisoning and PoT backdoors that corrupt *planning* before any tool is called — i.e., the gate is necessary but not sufficient for those stages. Practically, ASB's D/IPI formalization and 5 injection phrasings (Naive, Escape Characters, Context Ignoring, Fake Completion, Combined) give us a ready-made paraphrase set for our stretch adaptive pilot, and its defense taxonomy lets us position our gate vs. all 11 defenses in one table without reimplementing them (we cite their published ASR deltas). Crucially, ASB's NRP metric is the precedent for our own joint reporting (ASR + FPR + latency + setup cost) rather than ASR alone — a gate that reduces ASR but destroys utility is not a win, which is why we pair ASR with FPR/utility.

Gap / Limitation Noted in Paper:
The authors acknowledge scenarios/tools are still simulated (not live MCP servers like MCPTox), so the combinatorial scale (27 methods × 13 backbones × 10 scenarios) trades depth per pair for breadth. They list future work as improving defenses and expanding attack scenarios — exactly where per-vector studies on live MCPTox and on simulated AgentDojo would fit. No defense is proposed as a solution; all are benchmarked and found inadequate.

---

## Section 2 — Expert Detailed Analysis

### Q1–Q9 Quick Reference

| # | Question | Short Answer |
|---|---|---|
| Q1 | What problem and why important? | Prior agent security work isolated one stage/vector (e.g., InjecAgent only IPI). Real agents face *combined* threats across system prompt, user prompt, tool usage, and memory retrieval. Without a unified formalization, defenses are tested on incomparable slices. Matters because deployed agents use all stages together (system role + user task + RAG + tools). |
| Q2 | What data (source, size, splits, ethics)? | New synthetic benchmark. 10 scenarios (IT management, investment, legal, medicine, education, counseling, e-commerce, aerospace, research, autonomous driving) → 10 agents (one per scenario, GPT-4-generated description/role) → per agent 5 user tasks + standard plan (2-step tool sequence + expected achievement) + 2 tool types (normal vs. attack). Totals: 10 agents, 50 agent tasks, 20 normal tools, 400 attack tools, 400 attack tasks, 10 PoT demonstrations, 27 attack/defense methods, 7 metrics. 400 tasks split aggressive (risky instruction, should be refused) vs. non-aggressive. No human data, no train/test split — evaluation-only. GPT-4 used for agent/task/tool generation. |
| Q3 | What features/inputs, how engineered? | System prompt *P_sys* (with optional PoT demos), user prompt *I*, tool list *T* (normal + injected attack tools), retrieved memory *M* (from poisoned RAG), observation *O* from tool trajectory. Each tool has name, description, expected achievement (simulated API call checks achievement string), but *no parameters* (simplifies security vs. capability). Injected task defined as *T_inj = (I_inj, T_inj_tools, data_inj)*; compromised data *D_c = G(D, I_inj)* via 5 injection methods. |
| Q4 | What methods/models, overall pipeline? | Formalizes each attack with adversarial goal maximizing expected probability agent uses attack tools: DPI maximizes over *I⊕I_inj, T∪T_inj*; IPI over *O⊕I_inj*; Memory Poisoning over poisoned RAG *DB_p* (black-box, no embedder internals, poison via prior DPI/IPI that gets saved); PoT Backdoor (training-free) poisons system prompt demos *D_p = (task, plan_step_backdoor, action_adv)* + trigger in query *Q⊕trigger* → agent generates backdoored plan; Mixed combines DPI+IPI+Memory. Defenses formalized per attack: prevention-based (Delimiters, Instructional Prevention, Sandwich, DPR, Paraphrasing, Shuffle) vs. detection-based (PPL threshold, LLM-based detection). ReAct framework for all agents; retrieval via encoder similarity to RAG keys. |
| Q5 | What baselines and why chosen? | 13 LLM backbones as agents (Gemma2 9B/27B, Llama3 8B/70B, Llama3.1 8B/70B, Mixtral-8×7B, Qwen2 7B/72B, Claude 3.5 Sonnet, GPT-3.5 Turbo, GPT-4o/mini) to test capability vs. vulnerability; 5 DPI + 5 IPI phrasings + Combined; Memory Poisoning + PoT (non-word vs. phrase triggers) + 4 Mixed; 11 defenses (Delimiters, Dynamic Rewriting, Sandwich, Instructional, Paraphrasing, Shuffle, PPL, LLM detection). Covers all stages and same 5 injection phrasings reused across DPI/IPI/Memory for comparability. |
| Q6 | How evaluated (metrics, setup, tests)? | 7 metrics: ASR (attack tools used / attacked tasks), RR (Refuse Rate, judged by backbone LLM on aggressive tasks), PNA (Performance under No Attack = required tools used / tasks), BP (Benign Performance when backdoored but clean query), FNR/FPR (detection defenses), NRP = PNA × (1 − ASR) (joint utility-security). Per-attack, per-backbone, per-stage breakdown; rise-then-fall analysis (utility vs. ASR), PNA vs. leaderboard correlation, and PoT trigger-type ablation. 400 tasks × 13 backbones × 27 methods. |
| Q7 | Key results vs baselines? | Attacks effective: Mixed 84.30% avg ASR (highest), DPI 72.68%, IPI 27.55%, Memory Poisoning 7.92% (lowest, needs retrieval). Refusals partial (GPT-4o 20% DPI). Rise-then-fall: better PNA initially increases ASR (better instruction following → more hijackable) until refusals reduce ASR at top end (GPT-3.5 98.4% DPI vs GPT-4o 60.3%). NRP ranking: Claude 3.5 Sonnet 43.56 > Llama3-70B 30.03 > GPT-4o 28.12 > others. PNA generally < leaderboard quality (except 3 models). Defenses inadequate: DPI best defense DPR still 44.45% ASR (from 78.38% no-defense), Paraphrasing 56.87%; IPI defenses ~25–28% (from 27.98% — barely helps); many hurt PNA. PoT backdoor effective across both trigger types with unaffected BP. |
| Q8 | Limitations and biases? | Simulated tools/scenarios (not live, no params) — may miss real API quirks (MCPTox covers live); breadth trades depth per attack/defense pair; black-box memory poisoning is realistic but weaker than white-box; no multimodal, no long-horizon multi-task-without-reset. |
| Q9 | Code/data/artifacts available? | Fully open: https://github.com/agiresearch/ASB + https://luckfort.github.io/ASBench/ (interactive results). All attack/defense formalizations and prompts in Appendix A/C. Reimplementation effort: low to run benchmark, high to reimplement all 27 methods — but paper is useful as cite-only superset. License: open-source. |

### 1. Publication Status & Citation

| Field | Value |
|---|---|
| **Venue** | ICLR 2025 (International Conference on Learning Representations) |
| **arXiv** | 2410.02644v4 |
| **Last verified** | 2026-08-24 — full html + GitHub/website live |
| **Code** | https://github.com/agiresearch/ASB |

**BibTeX:**
```bibtex
@inproceedings{zhang2025asb,
  title={{Agent Security Bench (ASB)}: Formalizing and Benchmarking Attacks and Defenses in {LLM}-based Agents},
  author={Zhang, et al.},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2025},
  eprint={2410.02644},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2410.02644}
}
```

### 2. Core Contribution & Method

ASB's core is a **formal, stage-wise threat model** that unifies disparate attacks into one probabilistic framework, then instantiates it as a broad benchmark.

**Stage decomposition (Fig 1):** Agent operates as ReAct: System prompt (role + PoT demos) → User prompt → Memory retrieval (RAG) → Planning (thought) → Tool execution (observation) → loop. Each stage is an attack surface.

**Formal attack definitions (all maximize expected probability agent uses attack tool list *T_inj*):**
- **DPI (Def 1):** Compromise *I → I⊕I_inj* and *T → T∪T_inj*. 5 phrasings: Naive (append), Escape Characters (`\n`+append), Context Ignoring ("Ignore previous"), Fake Completion ("Task complete."), Combined (all three).
- **IPI (Def 2):** Compromise *O → O⊕I_inj* (any step's observation). Same 5 phrasings applied to tool output.
- **Memory Poisoning (Def 3):** Attacker provides poisoned RAG *DB_p = DB ∪ {(key_poison, plan_poison)}*. Black-box: no embedder internals, poison inserted via prior DPI/IPI that the agent saves to memory; next similar query retrieves poisoned plan as in-context example → agent replays poisoned tool call.
- **PoT Backdoor (Def 4, novel):** Training-free. Poison a subset of system-prompt PoT demos *D_p = (task, plan_step_backdoor→action_adv)* that encode "if trigger in query, then call *T_inj*". Inject non-word (`@_@`, `:)`) or phrase (LLM-optimized, weak semantic correlation, length-constrained) trigger into user query. Exploits ICL + LLM planning (BadChain-style) — the backdoor planning step *is* the link between trigger and action.
- **Mixed (A.1):** DPI + IPI + Memory poisoning combined (PoT excluded because system prompt not stored in DB). Joint adversarial goal over *I⊕I_inj, O⊕I_inj, DB_p*.

**Defenses (Tab 2, A.4):** Mapped per attack: DPI/IPI → Delimiters (`<start><end>` isolation), Instructional Prevention ("ignore all except user instruction"), Sandwich (repeat instruction after tool output), Paraphrasing (LLM paraphrases query to disrupt special chars), Dynamic Prompt Rewriting (rewrite query to security-aligned objective, stronger than paraphrase), Shuffle (randomly reorder PoT steps to break backdoor link). Memory → PPL detection (perplexity threshold on retrieved plan) and LLM-based detection (backbone judges if plan is compromised) — detection-based, evaluated via FNR/FPR. All formalized as inequalities lowering malicious-action probability.

**Benchmark construction (B.1–B.2):** GPT-4 generates per-agent description, 5 user tasks + 2-step standard plan + tools (normal + attack). Attack tools are simulated APIs that check Expected Achievement string in output to judge success — no params. 400 attack tasks aligned to attack tools.

### 3. Key Results (Extracted)

| Attack | Avg ASR (13 backbones) | Avg RR | Notes |
|---|---|---|---|
| Mixed (DPI+IPI+Memory) | **84.30%** | 3.22% | Highest; compounding vectors |
| DPI | 72.68% | 6.53% | Most effective single vector |
| IPI | 27.55% | 8.61% | Lower than DPI (needs observation injection) |
| Memory Poisoning | 7.92% | 4.63% | Needs retrieval to hit |
| PoT Backdoor | ~42–55% (varies, Tab 5) | ~5.7% | Both trigger types effective; BP ≈ PNA (utility preserved) |

**Per-backbone (Tab 5, Fig 2):** Gemma2-9B 48% / GPT-4o-mini 67.5% / GPT-4o 64.4% / Llama3-8B 20.2% (lowest, due to low PNA 1.5%) → rise-then-fall: PNA initially ↑ ASR (better follower → more hijackable) until refusals ↑ then ASR ↓ (GPT-3.5 98.4% DPI vs GPT-4o 60.3% with 20% refusal). **NRP = PNA×(1−ASR):** Claude 3.5 Sonnet 43.56 (PNA 100), Llama3-70B 30.03, GPT-4o 28.12, GPT-3.5 Turbo 3.67 (PNA 8) — shows leaderboard ≠ agent suitability.

**Defenses (Tab 7–8):** DPI: No defense 78.38% → Paraphrasing 56.87% (−21.5), DPR 44.45% (−33.9) — best but still high; Delimiters 79.08% (no help), Instructional 76.77%. IPI: No defense 27.98% → Delimiters 24.96% (−3), Instructional 26.31%, Sandwich 28.04% (+0.06) — essentially no help. All prevention defenses hurt PNA somewhat; detection defenses have FPR/FNR tradeoffs. PoT: Paraphrasing and Shuffle lower ASR but not to zero.

**Implication for us:** Prevention-based prompt defenses (delimiters, instructional, sandwich) that look plausible on one benchmark barely move ASR on a broader suite — and even the strongest (DPR −33.9) leaves 44% ASR. This is external evidence that *prompt-level* defenses are insufficient, which is why we gate at the *tool call* (not the prompt). Also, mixed 84% shows a gate that only handles DPI *or* IPI alone will be bypassed by the other vector in a mixed attack — our gate's vector-agnostic per-call check is the counter.

### 4. Paper's Self-Admitted Limitations

Per conclusion/future work: simulated (not live) tools/scenarios, no params (capability vs. security conflated), breadth trades depth per pair, no new defense proposed (benchmark only), and future work is "improving defenses and expanding attack scenarios." Also: no multimodal, no long-horizon stateful memory beyond RAG retrieval, and Paraphrasing/DPR defenses require LLM calls that add cost.

### 5. Direct Comparison to Our Idea

| Dimension | ASB | Our Idea |
|---|---|---|
| **Scope** | 10 scenarios, 5 attack families, 27 methods, 13 backbones — broadest single study | Focused gate: tool-call stage only, evaluated on InjecAgent (IPI) + MCPTox (TPA) — deeper on two vectors, not all five |
| **What it measures** | Utility-security tradeoff per stage; mixed attacks compound vectors | Whether a per-call intent gate reduces ASR across *different* vectors with zero per-tool setup |
| **Most relevant ASB finding for us** | Mixed 84% ASR > any single vector; DPI/IPI defenses leave 44%/26% ASR; NRP shows utility ≠ security | Our gate targets the one stage both DPI and IPI (and TPA) must pass: the tool call. ASB shows prompt-level defenses fail even there — our gate is not a prompt defense. |
| **What's missing in ASB that we provide** | ASB benchmarks defenses but proposes no gate; no live MCP servers; no setup-cost or latency reporting; no per-call parameter check | We propose a gate and measure setup cost (0 vs. ToolGate) + latency + FPR — the deployment metrics ASB does not report. Conversely, we do not cover memory poisoning/PoT backdoor — we scope those as future work and cite ASB's numbers as honest boundary. |

**Overlap with C1 (gate):** None — ASB is benchmark-only. But its defense results (all inadequate) are the external evidence we cite for "prompt defenses insufficient, gate needed."

**Overlap with C2 (evaluation):** Methodological overlap — ASB's 7-metric, 13-backbone, stage-wise evaluation is a model for comprehensive reporting, and its Mixed Attack is the strongest argument for why each vector must be evaluated as its own study (which we do via InjecAgent and MCPTox, reported independently).

### 6. Our Positioning Strategy

| Role | Detail |
|---|---|
| **In our paper** | Anchor benchmark A4 (broadest coverage, superset) + source of the "mixed 84% > single vector" and "defenses still leave 44%/26% ASR" citations |
| **How we cite** | As "the first holistic agent security benchmark (10 scenarios, 27 methods, 13 backbones; mixed attack 84.3% ASR, DPI 72.7%, IPI 27.6%, memory 7.9%; 11 defenses inadequate; NRP metric)" — we position our gate as the defense ASB is missing for the tool-call stage |
| **Relationship** | Superset/parent — we evaluate on a focused live+simulated pair (InjecAgent+MCPTox) that ASB's simulated-only design does not cover; we acknowledge ASB's memory/PoT vectors as out-of-scope but cite its numbers to show why future work must extend the gate to planning/memory |

**Pre-emptive rebuttal paragraph** (if reviewer asks "why not evaluate on ASB's full 400-task suite?"):
> ASB's value is its breadth — 10 scenarios × 27 methods × 13 backbones — which is why we cite its mixed-attack 84.3% and defense-residual 44.5% results as external evidence that single-vector prompt defenses are insufficient. For our 4-month thesis we evaluate deeply on the two vectors that both require a tool call (InjecAgent for output injection, MCPTox for description poisoning) — the stage our gate controls — including live MCP servers that ASB's simulated tools do not provide. ASB's memory-poisoning and PoT-backdoor vectors corrupt planning and retrieval *before* any tool is called, which is an acknowledged boundary for a tool-call gate and is cited via ASB's numbers rather than re-benchmarked. Expanding the gate to those pre-tool stages is named future work.

### 7. Code & Reproducibility

| Field | Detail |
|---|---|
| **Repo** | https://github.com/agiresearch/ASB |
| **Website** | https://luckfort.github.io/ASBench/ (interactive, per-model/per-attack breakdowns) |
| **Data** | 10 agents, 400 tasks, 400+ tools, 27 methods, formal prompts in Appendix C.2.4, attack examples in A.3.2 |
| **LLM used** | 13 backbones (Gemma2, Llama3/3.1, Mixtral, Qwen2, Claude 3.5, GPT-3.5/4o) — all via API, ReAct |
| **Metrics** | ASR, RR, PNA, BP, FNR/FPR, NRP — all defined with adversarial goals in §3 |
| **License** | Open-source |
| **Reimplementation effort** | Low to run (clone + config); high to reimplement all 27 methods — we use it as cite-only superset and for our stretch adaptive phrasing set (5 injection methods reused) |
| **Key caveat** | No tool parameters (security vs. capability conflated); simulated APIs check Expected Achievement string — not a live check |

### 8. Cross-References

| Paper in this review | Relationship |
|---|---|
| **AgentDojo (Debenedetti et al., 2024)** | Complementary — AgentDojo is deep & stateful on IPI (74 tools, 629 cases, formal state checks); ASB is broad & stage-wise (400+ tools, 400 tasks, 5 families). We use AgentDojo for stretch drift (stateful multi-step) and cite ASB for breadth (mixed 84% shows AgentDojo's single-vector ASR underestimates combined threat). |
| **InjecAgent (Zhan et al., 2024)** | Subset — InjecAgent's 17×62 IPI is more granular on IPI than ASB's 5-phrasing IPI, but ASB's DPI 72.7% vs. IPI 27.6% shows direct prompt manipulation is easier than observation injection — context for why MCPTox's description vector (neither DPI nor classic IPI) needs its own benchmark. |
| **MCPTox (Wang et al., 2025)** | Extension — ASB is simulated; MCPTox is live MCP servers and proves simulated-only misses real poisoning (IPI payloads 0% on MCPTox). We pair them to cover simulated breadth (ASB cited) + live depth (MCPTox evaluated). |
| **ToolGate (Liu et al., 2026)** | Predecessor gate — ToolGate is a *proposed* gate (formal Hoare) but evaluated only on task completion; ASB shows the *need* for a gate (84% mixed ASR, defenses fail) but proposes none. Our gate is the defense ASB is missing, and we evaluate it where ToolGate never did (adversarial). |

### 9. Relevance to Thesis

★★★★☆ (Important context + superset citation)

**Justification:** ASB is the broadest, most-cited superset in our review (27 methods, 13 backbones, 5 families) and the only paper that formalizes *all* stages and shows mixed attacks compound. It is the single best citation for "prompt defenses are inadequate" (DPR still 44% ASR) and "mixed > single vector" (84% vs. 27–73%). Every team member should read §3 (threat model) and §5.3–5.4 (attack/defense results) to understand why our gate is scoped to the tool-call stage and what is explicitly out of scope (memory/PoT). Not a primary evaluation substrate (we run InjecAgent+MCPTox for depth+live), but mandatory in related work as the holistic benchmark that frames our focused contribution.

