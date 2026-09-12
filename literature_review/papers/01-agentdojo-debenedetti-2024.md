# 📄 Paper #1 — AgentDojo

![Paper](https://img.shields.io/badge/Paper-%231-1f6feb?style=for-the-badge)
![Role](https://img.shields.io/badge/Role-Anchor%20(Benchmark)-2ea043?style=for-the-badge)
![Threat](https://img.shields.io/badge/Threat%20to%20Novelty-Low-2ea043?style=for-the-badge)
![Venue](https://img.shields.io/badge/Venue-NeurIPS%202024%20(Datasets%20%26%20Benchmarks)-6e40c9?style=for-the-badge)
![Verified](https://img.shields.io/badge/Verified-2026--08--24-8957e5?style=for-the-badge)

> *Verified via full paper text (arXiv html 2406.13352v3 + GitHub/leaderboard).*

Paper Title:
AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

Authors & Year:
Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner, Marc Fischer, Florian Tramèr — 2024

Link:
arXiv: https://arxiv.org/abs/2406.13352 (v3)
Code: https://github.com/ethz-spylab/agentdojo
Leaderboard: https://agentdojo.spylab.ai
Proceedings: NeurIPS 2024 Datasets & Benchmarks Track (per literature_review.md verification)

Summary:
AgentDojo is not a static test set but an extensible, stateful execution environment for measuring LLM agents that interleave reasoning and tool calls over untrusted data. It provides 97 realistic user tasks and 629 security test cases across four environments (Workspace/email+calendar+drive, Slack, Travel, e-banking) with 74 tools. Each user task has a deterministic utility function over environment state (not an LLM judge), and each injection task has a security function checking whether the attacker's goal was executed. Attacks are injected via realistic placeholders in tool outputs (e.g., an email body, a webpage). The framework is built to be extensible — new tasks, attacks, and defenses are added by implementing a simple Python function (`attack()` / `query()`). Evaluation across frontier models (GPT-4o, Claude 3.5 Sonnet/Opus, Gemini, Llama 3 70B, Command R+) shows SOTA LLMs solve <66% of tasks even without attacks, that the strongest generic attack ("Important message") succeeds in ~46% of cases (up to 92% on Slack, 0% on the hardest Travel exfiltration task), and that existing defenses — especially a simple tool-filter that pre-restricts the allowed tool set — can drop ASR to 7.5% but fail on 17% of cases where the required tools overlap or cannot be planned in advance. The paper explicitly positions future work as needing adaptive, defense-aware attacks and more sophisticated isolation (planner/executor separation).

Relevant to Our Idea:
AgentDojo is one of our two primary anchor benchmarks for the "injection" vector (the other is InjecAgent). Unlike InjecAgent's single-turn simulated tool output, AgentDojo requires the agent to dynamically choose which of many tools to call in a stateful, multi-step trajectory — i.e., it tests the full ReAct loop, not just one tool call. This makes it the closest proxy to our gate's deployment setting (real MCP-style tool calling with interleaved reasoning). We will reuse its harness for our stretch multi-turn drift pilot (20-case sample). Crucially, AgentDojo's tool-filter defense is the simplest published "action-gate" — it blocks by tool-name allowlist, not by intent consistency — and its failure modes (cannot plan ahead, overlap between benign and malicious tool sets, "wait until right tools appear") are exactly the gaps our intent-derived scorer targets: we check *whether a proposed call matches the original request* rather than *whether its tool name was pre-approved*, so we do not need to pre-plan the tool sequence.

Gap / Limitation Noted in Paper:
The authors state the environment is simulated (dummy data generated via GPT-4o/Claude 3 Opus + manual inspection), not live APIs, so transfer to production is not directly demonstrated. Only four environments are covered. Attacks and defenses in the first version are generic and not explicitly optimized against the target model/defense — the authors call for adaptive attacks and more involved isolation (e.g., planner dispatching to isolated executors that communicate only symbolically) as future work. Tasks requiring up to 18 tool calls and contexts up to 7k tokens already stress frontier models, but multimodal and long-horizon multi-task-without-reset scenarios are not yet covered.

---

## Section 2 — Expert Detailed Analysis

### Q1–Q9 Quick Reference

| # | Question | Short Answer |
|---|---|---|
| Q1 | What problem and why important? | Agents that combine reasoning + tool calls are hijackable via indirect prompt injection in tool outputs (emails, webpages). Matters because agents now have real permissions (email, banking, travel) where a hijack has irreversible consequences. Existing agent benchmarks had no adversarial evaluation; prompt-injection benchmarks had no tool-calling. |
| Q2 | What data (source, size, splits, ethics)? | New benchmark, not reused. 97 user tasks × 27 injection tasks → 629 security test cases across 4 envs: Workspace (24 tools, 40 user, 6 inj), Slack (11,21,5), Travel (28,20,7), Banking (11,16,9). 74 tools total. Dummy data generated manually + GPT-4o/Claude 3 Opus, manually inspected. No human-subject data. No train/test split — benchmark is evaluation-only. Ethics: benign dummy data, injection tasks include sensitive actions (exfiltrate 2FA code) for measurement only. |
| Q3 | What features/inputs, how engineered? | Natural-language user instruction + tool definitions (in prompt) + stateful environment + tool outputs (some containing injected instructions at realistic placeholders). Ground truth is a sequence of expected tool calls per task. No numeric feature engineering — unit of analysis is the full tool-call trajectory. Injection placeholders are placed only where the ground-truth trajectory actually queries that data source, ensuring realism. |
| Q4 | What methods/models, overall pipeline? | Extensible harness: environment (mutable state objects) + tools (FastAPI-like Python functions, YAML-formatted outputs) + user task (utility function over before/after state) + injection task (security function) + agent pipeline (`query(user_prompt, tools, state) → tool calls`). Initial instantiation: ReAct-style agents via official function-calling APIs; generic "Important message" attack + variants; defenses as modular pipelines (data delimiters per Hines et al., BERT prompt-injection detector per ProtectAI, prompt sandwiching, tool filtering/isolation). Formal metrics over state, not LLM-as-judge. |
| Q5 | What baselines and why chosen? | No-attack utility baseline; no-defense-under-attack baseline; comparison across 9+ backbone LLMs (Gemini 1.5 Flash/Pro, Claude 3/3.5 Sonnet/Opus, GPT-3.5/4 Turbo/4o, Llama 3 70B, Command R+) to test inverse scaling; 4 attack phrasings (ignore previous instructions, InjecAgent injection, "TODO: {task}", Important message) + adaptive Max (best per task); 4 defenses (delimiters, detector, sandwiching, tool filter). Covers model capability → vulnerability and prompt phrasing → ASR. |
| Q6 | How evaluated (metrics, setup, tests)? | Benign Utility (fraction of 97 tasks solved without attack), Utility Under Attack (fraction of 629 cases where user task still solved without side effects), Targeted ASR (fraction where attacker goal executed), untargeted ASR (1 - Utility Under Attack). Also: Max adaptive ASR (any of 4 attacks succeeds). Evaluated on full 629 cases per model; ablations: attacker knowledge of victim/model name (±1.9% with correct vs -22% with wrong), injection position (end of tool output up to 70% vs earlier), suite/injection-task breakdown. No human study; deterministic utility checks. |
| Q7 | Key results vs baselines? | SOTA fails without attacks: <66% benign utility (Claude 3.5 Sonnet best, GPT-4o close). Inverse scaling: more capable models easier to attack (GPT-3.5 98% DPI? but on AgentDojo Important message baseline 45.8% → 47.7% with correct names; Max boosts +10%). Suite breakdown: Slack 92% ASR (attacker controls large fraction of outputs), hardest Travel exfiltration 0% (requires two unrelated hijacks). Position matters: end of tool message most effective (70% vs lower). Under attack utility drops 10–25% absolute. Defenses: tool filter best — 7.5% ASR — but fails on 17% overlap cases and when tool sequence cannot be planned ahead; data delimiters/detector/sandwiching largely ineffective or hurt utility (detector false positives). |
| Q8 | Limitations and biases? | Simulated, not live APIs (transfer gap); only 4 envs / 27 injection goals; generic attacks not defense-aware optimized (authors flag adaptive evaluation as required future work); tool-filter defense is simple allowlist, not intent-aware; no multimodal, no multi-task-without-reset, no constraint on injection length/format.  |
| Q9 | Code/data/artifacts available? | Fully open: https://github.com/ethz-spylab/agentdojo (+ pip package, FastAPI-like tool extension), leaderboard/docs at https://agentdojo.spylab.ai. Dummy data and task suites released. Reimplementation effort: low (clone + run); extending with new tasks/attacks is designed to be one function. License: open-source (MIT per repo). |

### 1. Publication Status & Citation

| Field | Value |
|---|---|
| **Venue** | NeurIPS 2024 Datasets & Benchmarks Track (per literature_review.md; arXiv preprint 2406.13352v3, June 2024) |
| **arXiv** | 2406.13352v3 |
| **Last verified** | 2026-08-24 — full html + GitHub/leaderboard live |
| **Code** | https://github.com/ethz-spylab/agentdojo |
| **Docs** | https://agentdojo.spylab.ai |

**BibTeX:**
```bibtex
@inproceedings{debenedetti2024agentdojo,
  title={{AgentDojo}: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for {LLM} Agents},
  author={Debenedetti, Edoardo and Zhang, Jie and Balunovi{\'c}, Mislav and Beurer-Kellner, Luca and Fischer, Marc and Tram{\`e}r, Florian},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS), Datasets and Benchmarks Track},
  year={2024},
  eprint={2406.13352},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2406.13352}
}
```

### 2. Core Contribution & Method

AgentDojo's contribution is a **dynamic, stateful, extensible evaluation framework** rather than a static dataset. Static benchmarks saturate and are easy to overfit with non-robust defenses; AgentDojo instead provides the environment, state, and interfaces so new adaptive attacks and defenses can be plugged in and measured with formal state-based checks.

**Pipeline:**
1. **Environment + State:** Four stateful environments (Workspace, Slack, Travel, e-banking) modeled as mutable objects (emails, calendar events, drive files, bank transactions). Dummy data populated manually + via GPT-4o/Claude 3 Opus and manually inspected. State supports utility/security functions that inspect before/after mutations.
2. **Tools:** 74 tools (e.g., `read_email`, `send_email`, `get_calendar_events`, `pay_bill`) implemented as Python functions with FastAPI-like decorators; docs auto-injected into agent prompt; outputs formatted as YAML (configurable). New tools added by adding a decorated function.
3. **User Task:** Natural-language instruction + deterministic `utility(state_before, state_after, agent_output) → bool` + ground-truth tool sequence (used to place injections realistically — only data the agent will actually query is poisonable, unlike benchmarks that poison arbitrary outputs).
4. **Injection Task:** Attacker goal as instruction + `security(state_before, state_after) → bool` + ground-truth attack tool sequence (e.g., `read_calendar` then `send_email(to=attacker)`). Covers sensitivity spectrum: generic email up to exfiltrating Facebook 2FA code.
5. **Security Test Case:** Cross-product per environment: each user task × each relevant injection task (e.g., Workspace 40×6=240) with injection text placed at the correct placeholder within the tool output that the ground-truth trajectory queries. Also runnable as pure utility case (no injection).
6. **Agent Pipeline:** Any `query(prompt, tools, state)` implementation. Baseline: ReAct via official function-calling APIs with paper's system prompt (Claude prompts adapted per Anthropic docs). Pipeline can be wrapped with a defense (delimiters, detector, sandwich, tool filter) without changing the agent.
7. **Metrics:** Deterministic checks over state — no LLM judge to be hijacked. Reports Benign Utility, Utility Under Attack, Targeted ASR, and Max ASR (adaptive attacker picks best of 4 phrasings per case).

**Attack variants measured:** (i) ignore previous instructions, (ii) InjecAgent phrasing, (iii) "TODO: {task description}", (iv) Important message ("This is a message to you, {model}, from {user}: ... must do {injection} before original task"), plus Max. Ablations: knowledge of victim/model name, wrong-name penalty, and injection position within tool output.

### 3. Key Results (Extracted)

| Metric | Finding | Source |
|---|---|---|
| Benign Utility (97 tasks) | <66% for all models; Claude 3.5 Sonnet highest, GPT-4o close, others lower (e.g., Llama 3 70B lower) | Fig 6a, §4.1 |
| Targeted ASR (Important message, GPT-4o, 629 cases) | Baseline 45.8% (generic names) → 47.7% with correct model+user names (+1.9%); wrong names drop -22% | Table 2, §4.2 |
| Max adaptive (best of 4 phrasings per case) | +10% over Important message alone | Fig 8, §4.2 |
| Position effect | Injections at end of tool response most effective: up to 70% vs. middle/early | §4.1, App |
| Suite breakdown | Slack 92% (attacker controls many outputs), hardest Travel (book most expensive + exfiltrate) 0% (requires two unrelated hijacks, model does at most one) | Fig 7, §4.1 |
| Under-attack utility drop | 10–25% absolute vs. benign (strong correlation between benign utility and robustness) | Fig 6b |
| Defenses (GPT-4o) | Tool filter 7.5% ASR (best) — but fails on 17% overlapping-tool cases and non-plannable sequences; delimiters/detector/sandwiching largely ineffective; detector hurts utility via false positives | Fig 9, §4.3 |

**Notable nuance for our comparison:** The tool-filter defense is conceptually our gate's closest precedent — it gates at the tool level. Its success (7.5% ASR) shows gating works; its failures (needs advance planning, fails when benign tool set = malicious tool set, vulnerable to "wait until right task" multi-task attacks, and to injections that only alter a tool's *result* not its *invocation*) show why a *per-call intent-consistency check* (our gate) is needed instead of a *pre-planned tool-name allowlist*.

**Baselines used (agents + attacks + defenses):**

| Category | Items |
|---|---|
| Agents | Gemini 1.5 Flash/Pro, Claude 3 Sonnet/Opus, Claude 3.5 Sonnet, GPT-3.5 Turbo, GPT-4 Turbo, GPT-4o, Llama 3 70B, Command R+ |
| Attacks | Ignore previous instructions, InjecAgent injection, TODO, Important message, Max (adaptive per case) |
| Defenses | Data delimiters (spotlighting), BERT injection detector (ProtectAI), prompt sandwiching (repeat user prompt after tool call), tool filtering/isolation |

### 4. Paper's Self-Admitted Limitations

1. Simulated environment with dummy data — not live APIs; may not capture network latency, rate limits, dynamic data.
2. Static set of generic attacks/defenses in v1 — authors explicitly call for adaptive, defense-aware attacks (e.g., AutoAttack/GCG-style optimization for prompt injection) and stronger isolation (planner dispatching to isolated executors with symbolic communication).
3. Manual task/utility specification — scaling to larger task varieties may require automation without sacrificing reliability.
4. Tool-filter failures: cannot plan tool set when next tool depends on previous output; attacker goal needs same tools as user task (17% of cases); multi-task without reset allows "wait" attacks.
5. No multimodal, no injection length/format constraints, no real-world user data.

### 5. Direct Comparison to Our Idea

| Dimension | AgentDojo (tool filter) | Our Idea (intent gate) |
|---|---|---|
| **Problem** | Agent hijack via injected tool outputs | Same hijack, but also tool poisoning + drift — same chokepoint (tool call) |
| **Gate placement** | Pre-execution, but *pre-planned* allowlist before any tool output is seen | Pre-execution, *per-call* check against frozen intent contract |
| **Policy source** | LLM itself picks allowed tools from task description (self-reported, before seeing untrusted data) — still prompt-controllable | Structured intent contract parsed once from user request (trusted) + hard rules (no external_send if not asked) — not in agent's prompt, not attacker-controllable |
| **Granularity** | Tool *name* level (is `send_email` allowed?) | Tool *call* level (is `send_email(to=attacker@gmail.com, content=passport)` consistent with original request?) — catches parameter tampering |
| **When it fails** | User task needs same tool as attack (e.g., both need `send_email`) → cannot block without breaking task; needs advance planning | Does not need advance planning; checks each call's parameters/recipient against intent, so can allow `send_email(to=user)` while blocking `send_email(to=attacker)` |
| **Evaluation** | Reports ASR/utility on its own benchmark | Will be evaluated on InjecAgent and on MCPTox — separate per-vector studies with per-benchmark ASR/FPR tables, a per-benchmark comparison ToolGate never did; AgentDojo remains an optional stretch run |

**Overlap with C1 (gate mechanism):** Low-medium. Tool filter is a gate, but a coarse one. Our gate is strictly more expressive (per-call, parameter-aware, embedding + rule veto) and does not require the agent to correctly pre-predict the tool sequence.

**Overlap with C2 (evaluation):** Low. AgentDojo is an evaluation substrate we will *use* (stretch), not a competing defense to beat. No threat to novelty.

### 6. Our Positioning Strategy

| Role | Detail |
|---|---|
| **In our paper** | Anchor benchmark (A1) — the stateful, multi-step injection benchmark; also source of the tool-filter baseline discussion |
| **How we cite** | As the dynamic, stateful benchmark that requires full ReAct planning (vs. InjecAgent's single-turn) and that demonstrates even SOTA models fail without attacks and that tool-name gating is insufficient |
| **Relationship** | Complementary — we build on its harness for our drift stretch; we differentiate our gate from its tool filter on granularity and advance-planning requirement |

**Pre-emptive rebuttal paragraph** (if reviewer asks "isn't your gate just AgentDojo's tool filter?"):
> AgentDojo's tool filter is a pre-planned tool-name allowlist: before seeing any untrusted output, the agent itself decides which tools the task *might* need and then restricts itself to that set. This lowers ASR to 7.5% but fails when the benign and malicious tasks require the same tool (17% of their cases) or when the tool sequence cannot be planned in advance — both acknowledged in their §4.3. Our gate checks every *proposed tool call* (name + parameters + recipient) against a frozen, user-derived intent contract, not a self-reported allowlist. It can therefore allow `send_email(to=user)` while blocking `send_email(to=attacker)` for the same task, and it requires no advance planning. The two gates share placement (pre-execution) but differ in policy source, granularity, and attacker-controllability.

### 7. Code & Reproducibility

| Field | Detail |
|---|---|
| **Repo** | https://github.com/ethz-spylab/agentdojo (pip install, FastAPI-like tool API) |
| **Extensibility** | One function to add a new environment/tool/attack/defense; well-documented |
| **Leaderboard** | https://agentdojo.spylab.ai |
| **LLM used** | GPT-4o (primary ablations), Claude 3.5 Sonnet (best utility), others via official APIs |
| **Compute** | No training; tool calls are simulated Python functions |
| **License** | Open-source (MIT per repo) |
| **Reimplementation effort** | Low — clone and run; our stretch pilot is 20 cases, not full 629 |

### 8. Cross-References

| Paper in this review | Relationship |
|---|---|
| **InjecAgent (Zhan et al., 2024)** | Complementary benchmark — InjecAgent is single-turn, simulated, 1,054 cases; AgentDojo is multi-step, stateful, 629 cases. We evaluate on InjecAgent as primary (cheaper) and AgentDojo as stretch to show multi-step robustness. AgentDojo's §4.2 shows InjecAgent phrasing underperforms their Important message — we will test our gate against both. |
| **MCPTox (Wang et al., 2025)** | Different vector — MCPTox is poisoning at registration (metadata), AgentDojo is injection at output. Our one gate mechanism is evaluated on **both vectors as separate studies** (injection on InjecAgent, poisoning on MCPTox) with per-vector ASR/FPR — the contribution is per-vector reporting, not a single combined number. |
| **ASB (Zhang et al., 2025)** | Superset — ASB covers DPI/IPI + memory poisoning + PoT backdoor + mixed; AgentDojo covers IPI only but with deeper statefulness. ASB's mixed attack 84% ASR shows single-vector defenses like AgentDojo's tool filter will not suffice alone. |
| **ToolGate (Liu et al., 2026)** | Predecessor gate — ToolGate is formal Hoare contracts with world-state; AgentDojo's tool filter is informal allowlist. Our gate sits between them: more expressive than allowlist, lighter than formal contracts, and unlike ToolGate is tested adversarially. |

### 9. Relevance to Thesis

★★★★★ (Essential — anchor benchmark)

**Justification:** AgentDojo is the only benchmark in our set that tests *stateful, multi-step* agent planning under injection with formal state-based scoring (not an LLM judge that can itself be hijacked). It directly motivates our gate (all defenses except tool filtering largely fail; tool filtering's 17% failure mode is our exact gap) and provides a ready-made harness for our stretch drift evaluation. Every team member should run the 20-case demo before Month 2. Mandatory citation in related work as "the dynamic, stateful injection benchmark" alongside InjecAgent.

