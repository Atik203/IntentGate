# Phase 8 — Related-Work Matrix (T1)

**Status:** Draft v1 — dated 2026-10-22. Prepared for the Phase 8 novelty gate (8.0).
**Purpose:** Feature-level comparison of the closest request-derived action-authorization /
runtime-defense systems against IntentGate v1, so candidate contributions C1–C3 can be stated
as falsifiable claims (T2) and the novelty boundary frozen before any implementation or
confirmatory run.

**Method:** Each row is populated from the local review file (where it exists) plus a fetch
of the primary source page (arXiv/DOI/ACL) on 2026-10-22 to pin version and access date.
No "first/novel/state-of-the-art" claim is made here; rows record what each system does and
what IntentGate does, leaving the gap statement to the supervisor-approved T2.

**Implementation-status legend:**
- **Implemented** — code exists in this repo and is evaluated.
- **Design comparison only** — reviewed + discussed in E27, no head-to-head run.
- **Reviewed only** — local review file exists, no code.
- **Pending** — source checked, full feature review not yet done.

---

## Master comparison matrix

| System | Source (version, access date) | Trusted input | Policy representation | Decision point | Argument / resource awareness | Update lifecycle | User confirmation | Threat model | Datasets | Model families | Metrics | Artifact availability | Implementation status vs IntentGate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **IntentGate v1 (this project)** | repo @ HEAD (frozen Phase 5/7) | User request → frozen `IntentContract` (goals, expected tool categories, permitted data access, side-effect limits) parsed once before any attacker content | Embedding of contract text + rule score; `S = α·S_sem + (1−α)·S_rule` (α=0.7), hard veto when rule triggered & S_rule=0; allow/block/escalate band (τ=0.75, δ=0.1) | Tool-call boundary (`GateMiddleware.execute`) | Side-effect limits, destructive keywords, path/recipient scope; v2 (T5, planned) adds typed argument policy | Immutable per session; no update; no user confirmation in benchmark mode | Escalate band exists; interactive mode prompts; benchmark mode auto-blocks | Indirect injection (hidden text in tool returns), poisoned tool descriptions, multi-step/argument substitution | InjecAgent, MCPTox (Phase 5); AgentDojo planned (Phase 8) | gpt-4o-mini (anchor), Qwen3.5:4b (local), DeepSeek (boundary) | ASR, FPR, p95 latency, call-level allow/block | pip package + `results/` + Docker + SHA-256 manifest | — (reference row) |
| **ClawGuard** (Zhao et al.) | arXiv:2604.11790 **v2**, last revised 2026-05-11 (fetched 2026-10-22) | User objective `H₀`, parsed pre-session before any external tool call | Task-specific rule set `R_task` (network/file/command rules) + fixed non-overridable `R_base`; `R = R_base ∪ R_task`; deterministic rule match (whitelist/blacklist/`amb`) + obfuscation normalizer | Tool-call boundary (pre-execution) | Paths, domains, commands; obfuscation normalizer (Base64/hex/Unicode/eval/IFS/quote mixing) | Induced once pre-session, user-confirmed; skill allowlist `Ψ` persists across sessions | Yes — user reviews/edits `R_task`; `amb` calls queued for approval | Indirect injection: web/local content, MCP tool poisoning, skill-file injection; direct prompt injection out of scope | AgentDojo, InjecAgent, ChatInject, MCPTox, MSB, Skill-Inject; utility on WebArena/AgentBench-OS/SWE-bench | DeepSeek-V3.2, MiniMax-M2.5, Qwen3.5-397B, GPT-5.4, Claude Sonnet 4.6 | CR, ASR, DSR, RR; utility retention (87.4%→95.1%); token overhead (~5%) | Code on GitHub (Claw-Guard/ClawGuard) | Reviewed only (`literature_review/papers/07-clawguard-2026.md`) |
| **Task Shield** (Jia et al.) | ACL 2025, DOI 10.18653/v1/2025.acl-long.1435, pp. 29680–29697 (fetched 2026-10-22) | User-specified goals | Test-time task-alignment check: verifies each instruction/tool call serves user objectives | Tool-call / instruction level (test-time) | Task alignment of instructions and tool calls (not path/domain rules) | Per-call test-time check; no persistent policy | Not stated (automated check) | Indirect prompt injection via external data sources | AgentDojo (ASR 2.07%, utility 69.79% on GPT-4o) | GPT-4o (reported) | ASR, task utility | Paper + code (not verified here) | Reviewed only (source checked; no local review file) |
| **Progent** (Shi et al.) | arXiv 2504.11703 **v3**, revised 2026 (verified 2026-10-18) | Task | Symbolic privilege rules generated from task; can update during execution with checks on policy expansion | Tool-call level (policy check) | Privilege rules over actions/tools | Dynamic update during execution with approval for expansion | Approval for privilege expansion | Indirect injection / privilege escalation | Not run on IntentGate benchmarks (scope-out, E27) | Not stated in source | Not reported on our benchmarks | Code on GitHub (sunblaze-ucb/progent) | Design comparison only (E27) |
| **AgentSpec** (Wang et al.) | ICSE 2026, DOI 10.1145/3744916.3764546, pp. 2938–2950 (fetched 2026-10-22) | Not stated in fetched abstract (runtime constraint DSL) | Runtime constraint DSL across agent domains | Runtime enforcement (constraint-based) | Constraints over agent behavior (domain-general DSL) | Not stated in fetched abstract | Not stated in fetched abstract | Agent safety / reliability (domain-general) | Not stated in fetched abstract | Not stated in fetched abstract | Not stated in fetched abstract | Paper (code availability not verified here) | Reviewed only (source checked; no local review file) |
| **ToolGate** (Liu et al.) | arXiv 2601.04688 **v1** (verified 2026-08-24) | Tool pre/postconditions | Per-tool Hoare contracts `{P}T{Q}` over symbolic world state | Tool-call boundary (contract check) | Tool-level pre/postconditions (state predicates) | Manual authoring per tool (no auto-induction) | Not stated (manual contracts) | Not evaluated adversarially by original authors | ToolBench (GPT-5.2: 85.5/93.0/91.8) | GPT-5.2 (reported) | Rejection rate 29.4%; no adversarial eval in original | Code on GitHub (OceannTwT/ToolGate) | Implemented as B2 (`baselines/toolgate/`); coverage 100% InjecAgent / 8.1%→84.9% MCPTox |
| **CaMeL** (Debenedetti et al.) | arXiv 2503.18813 (local review `08-camel-2025.md`, 2026-10-22) | User task + capability policy | Planner/executor separation with capability-based data flow | Execution boundary (capability check) | Data-flow capabilities (provenance) | Static policy (planner-derived) | Not stated | Indirect injection via data flow | AgentDojo (reported in paper) | Not stated in local review | Not stated in local review | Paper + code (not verified here) | Reviewed only (local review exists) |

## Systems not yet reviewed (pending)

| System | Source | Status |
|---|---|---|
| MELON (Zhu et al.) | arXiv preprint (2025) | Pending — supporting defense, cited by ClawGuard |
| StruQ (Chen et al.) | USENIX Security 2025 | Pending — protocol-level defense |
| TrustAgent (Hua et al.) | Findings of EMNLP 2024 | Pending — staged constitution approach |
| Adaptive Attacks (Zhan et al.) | Findings of NAACL 2025 | Pending — defense-aware adaptive attacks |
| CaMeL deep review | arXiv 2503.18813 | Local review exists (`08-camel-2025.md`); feature-level depth pending |

## Gaps and open questions (to resolve before T2)

1. **ClawGuard is the nearest competitor.** It already does task-derived policy + boundary enforcement + user confirmation + obfuscation normalization + secret sanitization + skill-file channel. IntentGate v1 overlaps on (a) request-derived policy, (b) boundary enforcement, (c) model-agnostic middleware. Any "first request-derived gate" claim is now indefensible; the defensible delta must be stated narrowly (lifecycle comparison, small-model cost point, formal property, typed argument values, released artifact).
2. **Task Shield** is the closest on *task alignment* (semantic, not rule-based) but only evaluated on AgentDojo with GPT-4o. Direct numerical comparison requires running on the same cases/tools/prompts.
3. **AgentSpec** details (trusted input, lifecycle, datasets, metrics) are not recoverable from the fetched abstract alone; full text review pending before it can be cited as a baseline.
4. **Progent** is a design comparison only (E27); no head-to-head run exists.
5. **ToolGate** is the only implemented baseline (B2); coverage limits are documented in `configs/b2_coverage.json`.
6. **CaMeL** full feature review is pending; its planner/executor separation is a different mechanism (capability-based data flow) that may be non-comparable — handle per A5 (subset arm or principled non-comparability note).

## Notes for T2 (contribution statement)

- C1 (lifecycle comparison) is the strongest survivor: ClawGuard = induced-once + user-confirmed; IntentGate v1 = immutable per session; Progent = dynamic update with approval. This is a measurable contrast.
- C2 (argument-aware authorization, v2/T5) is viable only if it checks value-level items ClawGuard's rules do not (recipient/destination values, multi-action decomposition, schema drift). Justify against ClawGuard's obfuscation normalizer and rule set before implementing.
- C3 (reproducible evaluation package + adjudicated labels + paired traces + DOI) is independent of method novelty and should be presented as a first-class contribution (A2).
- No novelty claim may be made until this matrix is supervisor-approved and the closest-work table is frozen.
