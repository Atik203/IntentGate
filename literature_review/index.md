# Literature Review Index

**Project:** Intent-Consistency Verification at the Action Gate for Tool-Using LLM Agents

**Last updated:** 2026-08-24

> **FROZEN for Phase 2 (Gate 0, 2026-09-11).** This index and the 5 detailed paper reviews
> are the citation basis for the thesis/paper (BibTeX: `references.bib`). Re-verification of
> flagged figures happens only via a roadmap + CHANGELOG entry.

---

## Master Comparison Matrix

| # | Paper | Year | Venue | Role | Threat to Novelty | Last Verified | File |
|---|---|---|---|---|---|---|---|
| 1 | AgentDojo (Debenedetti et al.) | 2024 | NeurIPS (Datasets & Benchmarks) | **Anchor (Benchmark)** | Low | 2026-08-24 | [papers/01-agentdojo-debenedetti-2024.md](papers/01-agentdojo-debenedetti-2024.md) |
| 2 | InjecAgent (Zhan et al.) | 2024 | Findings of ACL | **Anchor (Benchmark)** | Low | 2026-08-24 | [papers/02-injecagent-zhan-2024.md](papers/02-injecagent-zhan-2024.md) |
| 3 | MCPTox (Wang et al.) | 2025 | arXiv (AAAI 2026 submission) | **Anchor (Benchmark)** | Low | 2026-08-24 | [papers/03-mcptox-wang-2025.md](papers/03-mcptox-wang-2025.md) |
| 4 | Agent Security Bench / ASB (Zhang et al.) | 2025 | ICLR 2025 | **Anchor (Benchmark)** | Low | 2026-08-24 | [papers/04-asb-zhang-2025.md](papers/04-asb-zhang-2025.md) |
| 5 | ToolGate (Liu et al.) | 2026 | arXiv preprint (2601.04688v1) | **Closest (System)** | High | 2026-08-24 | [papers/05-toolgate-liu-2026.md](papers/05-toolgate-liu-2026.md) |
| — | TrustAgent (Hua et al.) | 2024 | Findings of EMNLP | Pending | Pending | — | — |
| — | MELON (Zhu et al.) | 2025 | arXiv preprint | Pending | Pending | — | — |
| — | StruQ (Chen et al.) | 2025 | USENIX Security | Pending | Pending | — | — |
| — | CaMeL (Debenedetti et al.) | 2025 | arXiv preprint | Pending | Pending | — | — |
| — | Adaptive Attacks (Zhan et al.) | 2025 | Findings of NAACL | Pending | Pending | — | — |

### Legend

| Role | Meaning |
|---|---|
| **Anchor (Benchmark)** | Foundational benchmark — reveals vulnerability, proposes no defense; we build on it for evaluation |
| **Closest (System)** | Addresses same problem (tool-call verification) with different approach — requires sharp differentiation |
| **Supporting (Defense)** | Adjacent defense/attack paper — provides baseline or threat model context |
| **Preprint** | Not yet peer-reviewed — cite with caution |

| Threat to Novelty | Meaning |
|---|---|
| **High** | Published solution overlaps substantially with our action-gate verification — gap argument must be sharp |
| **Medium** | Adjacent defense evaluated on same benchmarks — needs explicit differentiation paragraph |
| **Low** | Benchmark-only or different attack surface — cite as complementary / evaluation substrate |

---

## Quick Triage (At a Glance)

**Essential reading (must-read before team meetings):**
- ToolGate (Liu et al., 2026) — **Closest system**; only contract-grounded tool execution gate published; High threat — never tested on adversarial injection benchmarks; manual contract authoring is key gap
- InjecAgent (Zhan et al., 2024) — **Anchor**; standard indirect prompt injection benchmark (1,054 cases, 62 attacker tools); GPT-4 vulnerable 24% → 47% enhanced; our primary evaluation substrate
- AgentDojo (Debenedetti et al., 2024) — **Anchor**; most extensible harness (97 tasks, 629 test cases, 4 environments); best benign utility 78% (Claude 3.5 Sonnet); defenses fail to get both high utility + low ASR

**Important context:**
- MCPTox (Wang et al., 2025) — **Anchor**; first live MCP-server benchmark (1,312 cases in v1, 45 real servers, 353 tools; up to 72.8% ASR, <3% refusal) — distinct poisoning-at-registration surface our gate must also cover
- ASB (Zhang et al., 2025) — **Anchor**; broadest coverage (4 attack families + PoT backdoor, 27 methods, 13 backbones, 400+ tools); highest ASR 84.3%; demonstrates need for unified defense across system/user/tool/memory stages

**Diagnostic / measurement (cite for threat severity):**
- [Pending: Adaptive Attacks (Zhan et al., 2025) — breaks most defenses to >85% ASR under defense-aware adaptive attacks; warning not to claim robustness without adaptive evaluation]
- [Pending: StruQ / CaMeL / MELON / TrustAgent — supporting defenses to position against]

---

## Gap Map

| What our idea does | Who else does it | Gap remaining |
|---|---|---|
| Intent-consistency check at action gate (pre-execution verification) | **None** (claimed gap) | Novel |
| Block tool calls diverging from user intent under injection | TrustAgent (EMNLP 2024) — via hand-authored Agent Constitution pre/in/post-planning | TrustAgent uses static natural-language constitution + GPT-4 sandbox emulation; no live tool evaluation; requires hand-authoring per domain |
| Contract-grounded tool execution | ToolGate (Liu et al., 2026) — Hoare-style pre/postconditions on symbolic world-state | ToolGate requires manual contract per tool, never evaluated on injection/poisoning benchmarks (InjecAgent/MCPTox), no adaptive-attack testing |
| Indirect prompt injection benchmarking | InjecAgent (ACL 2024), AgentDojo (NeurIPS 2024), ASB (ICLR 2025) | All reveal high ASR but propose no defense — we reuse as evaluation harness |
| Tool-poisoning at registration time | MCPTox (2508.14925v1) — 1,312 live-server cases, 45 servers, 353 tools | MCPTox measures vulnerability only; proposes no defense; registration-time surface never tested against ToolGate-style gates |
| Cross-surface unified defense | ASB (ICLR 2025) — evaluates 11 defenses across 4 stages | No defense neutralizes all stages; ASB evaluates existing defenses but does not propose gate mechanism |
| Formal/provable security | StruQ (USENIX 2025) — structured instruction/data channels via fine-tuning; CaMeL — planner/executor separation with capabilities | Both require model-level changes/fine-tuning; heavy deployment cost vs. our model-agnostic middleware claim |
| Training-free injection detection | MELON (2025) — masked re-execution + tool comparison | Doubles inference cost (2× trajectory); empirical only, no formal guarantees |

---

## Verification Log

| Date | Paper | Status Change | Source |
|---|---|---|---|
| 2026-08-24 | AgentDojo | Verified full html 2406.13352v3: 97 tasks / 629 cases (74 tools, 4 envs), <66% benign utility, tool filter 7.5% ASR | arXiv html + https://github.com/ethz-spylab/agentdojo + leaderboard |
| 2026-08-24 | InjecAgent | Verified full html 2403.02691v3: 1,054 cases (17 user tools × 62 attacker), GPT-4 24%→47% ASR, user-case Cramér's V 0.28–0.31 | ACL Anthology 2024.findings-acl.624 + html |
| 2026-08-24 | MCPTox | Verified full html 2508.14925v1: 1,312 cases (224/548/725 paradigms), 45 live servers / 353 tools, o1-mini 72.8% ASR, <3% refusal, IPI→TPA 0% | arXiv html + https://anonymous.4open.science/r/AAAI26-7C02 |
| 2026-08-24 | ASB | Verified full html 2410.02644v4: 10 scenarios, 400+ tools, 27 methods, 13 backbones, mixed 84.3% ASR, NRP metric | arXiv html + https://github.com/agiresearch/ASB |
| 2026-08-24 | ToolGate | Verified full html 2601.04688v1 (52k chars + App G): Hoare {P}T{Q}, 29.4% rejection, GPT-5.2 85.5/93.0/91.8 ToolBench, no adversarial eval | arXiv html + https://github.com/OceannTwT/ToolGate |
| — | TrustAgent | Pending — Findings of EMNLP 2024, staged constitution approach | — |
| — | MELON / StruQ / CaMeL / Adaptive Attacks | Pending | — |
