# PROJECT_BRIEF.md — IntentGate (ICEEICT 2027 paper)

- **Last scanned:** 2026-10-24
- **Files read:** `IEEE-conference/IEEE-conference.tex` (full), `configs/thresholds.yaml`,
  `configs/models.yaml`, `configs/intent_schema.json`, `src/intent_gate/scoring/scorer.py`,
  `src/intent_gate/scoring/embeddings.py`, `docs/experiments/05_phase5_full_evaluation.md`
  (targeted), `docs/experiments/06_phase6_pilots.md` (targeted: E18–E22),
  `docs/experiments/07_phase7_pilots.md` (targeted: E23–E26), `docs/experiments/README.md`,
  `docs/references.bib` (key entries), `docs/prompt.md` (voice rules), `roadmap.md` Phase 8,
  `AGENTS.md`, `CHANGELOG.md` (paper entries).
- **Skimmed or skipped:** `data/raw/*` (benchmark clones, ~440 MB), raw JSONL traces (sampled via
  experiment reports), `IEEE-conference/*.log/.aux` build artifacts, IEEEtran class. The project
  scanner stopped at its 5,000-file cap inside `data/raw/`; counts from that pass are not used.

## 1. Problem, gap, objective

- **Problem:** tool-using LLM agents can be redirected by attacker text in tool output (indirect
  prompt injection) or tool descriptions (tool poisoning) into unauthorized side effects
  [paper §I; blueprint Sec 0–2].
- **Gap as the paper states it:** existing defenses need model changes, a judge call per action,
  or hand-authored per-tool policies [paper §I–§II]. Closest systems: ToolGate (manual Hoare
  contracts), Progent (task-derived symbolic policy, updates during execution), ClawGuard
  (task-scoped constraints + user confirmation), Task Shield (LLM judge), CaMeL (capability taint
  tracking) [paper §II; blueprint Sec 19].
- **Objective:** derive an intent contract once from the trusted request, score each proposed call
  with embedding similarity plus a deterministic veto, and decide allow/block/escalate with no LLM
  call per action [paper abstract, §III].
- **Article type:** method + empirical evaluation. **Venue:** ICEEICT 2027, IEEE conference,
  double-blind, 6 pages including references.

## 2. Data

| Dataset | Role | Size | Notes |
|---|---|---|---|
| InjecAgent | indirect injection | 2,108 cases (base + enhanced; dh + ds) | pinned commits [paper §V-A; `configs/benchmark_versions.yaml`] |
| MCPTox | tool poisoning | 1,348 cases, static snapshot | live servers deferred [paper §V-A] |
| ToolBench/MCP-Universe | B2 fidelity validation only | not cloned; contract review + recorded-call replay used | [paper §IV] |
| AgentDojo | related work only | — | [paper §II] |

## 3. Method

- **Parser:** gpt-4o-mini, temperature 0, JSON mode, one repair retry; runs once per session,
  before any tool definitions or attacker content [paper §III-A/B; `configs/models.yaml`].
- **Schema (v1.1):** `goals`, `expected_tool_categories`, `permitted_data_access`,
  `side_effect_limits`, `specificity`, `raw_request` [`configs/intent_schema.json`].
- **Paper notation:** contract `C=(A,K,H)` where A = allowed (entity, operation, resource), K =
  numeric/path constraints, H = high-risk flags [paper Eq. 1]. **Mapping to schema is not stated
  in the paper** (audit finding).
- **Embedding:** `sentence-transformers/all-MiniLM-L6-v2`, CPU; contract embedded once, call
  embedded per decision [paper §III-B; `configs/models.yaml`].
- **Scoring (code is authoritative):** `S_sem = (cos(e_C,e_c)+1)/2` clipped to [0,1]
  [`scorer.py:30–31`]; `S_rule ∈ {0,1}`; veto returns `S=0` [`scorer.py:32–33`]; otherwise
  `S = 0.7·S_sem + 0.3·S_rule` clipped [paper Eq. 2–3; `configs/thresholds.yaml`].
- **Decision:** block if `S_rule=0` or `S < τ−δ`; escalate if `τ−δ ≤ S < τ`; allow otherwise.
  `τ=0.75`, `δ=0.1`, `α=0.7` [paper Eq. 4; `configs/thresholds.yaml`]. Escalate counts as block
  in benchmark mode.
- **No bypass:** every call goes through `GateMiddleware.execute()` [paper §III-A; tests].

## 4. Workflow

1. Load benchmark case → trusted request + untrusted content [paper §III-A].
2. Parse intent contract once (before tools load) → embed and cache [§III-B].
3. Agent proposes call → gate embeds call, evaluates rules, fuses, thresholds [§III-C/D].
4. Allow → execute; block → gate error observation; escalate → block + flag [§III-D].
5. Loop to step cap (15) → score case → aggregate ASR/FPR/latency/setup cost [paper §V].

## 5. Experiments

- **Arms:** B1 (no gate), B2 (ToolGate reimplementation), Ours (IntentGate), A1 semantic-only,
  A2 rule-only, A3 raw-request embedding [paper §V-C].
- **Shared settings:** identical prompts/tool blocks; gpt-4o-mini agent and parser; MiniLM
  embeddings; seed 42; temperature 0; max 15 steps [`configs/`; `harness/run_*.py`].
- **Statistics:** paired McNemar with continuity correction; seeded bootstrap 10k; Bonferroni
  α=0.005 over 10 risk breakdowns; post-hoc power reported [paper §V-D; E22].
- **Pilots:** second backbone (qwen3.5:4b), prompt baselines (E24), benign utility (E23),
  adaptive delivery (E26), echo guard (E26c), DeepSeek boundary (E25) [07_phase7_pilots.md].

## 6. Results index

| Result | Value | Source |
|---|---|---|
| InjecAgent ASR, B1 → Ours | 19.0% → 0.7% (354 → 13 of 2,108) | `05_phase5_full_evaluation.md:49` |
| MCPTox attack-influenced, B1 → Ours | 279 (20.7%) → 144 (10.7%) | `05...:56–57` |
| B2 InjecAgent / MCPTox | 17.2% / 20.1%, n.s. vs B1 | `05...:49,56` |
| McNemar p | 1.3e-33 / 1.25e-07 | roadmap success criteria; paper §V |
| B2 setup cost | 145 contracts (InjecAgent); 65/801 MCPTox = 8.1% distinct / 37.2% weighted | `05...:113`; E19 |
| B2 extended coverage | 583/801 = 60.9% distinct / 84.9% weighted; curve flat | `06_phase6_pilots.md:110–121` |
| p95 gate latency | 16–20 ms CPU; B2 0.06 ms | `05...:139` |
| Escalation | 583 calls; 60.7% attacker / 14.8% user / 24.5% other; 80.5% precision | E21 |
| Block rate (2,013 calls) | 12.8% specific, 9.6% vague, 12.4% overall | E22 |
| Mimicry | +0.0112 mean S; 13 residuals already ≥ τ; 0 additional crossings | E20 |
| Qwen replication | 27.1% → 2.1% | E18 |
| Benign pilot (50 cases) | allowed 16.0/12.0/8.0%; clean-block 0.0/25.0/42.9% | E23 |
| Prompt baselines (50 each) | 6.8% none, 4.3% delimiters, 4.3% sandwich, 8.9% instruction | E24 |
| DeepSeek | 0/100 both conditions (refusal boundary) | E25 |
| Echo guard | 34/34 calls, 11/11 templates, 0/194 new blocks | E26c |

## 7. Claim-evidence map (key claims)

| Claim (paper location) | Evidence | Support |
|---|---|---|
| ASR 19.0% → 0.7% (abstract, §I, §V) | phase5 table line 49 | direct |
| MCPTox 20.7% → 10.7% (abstract, §I, §V) | phase5 table lines 56–57 | direct |
| 16–20 ms p95 (abstract, §III, table) | phase5 line 139 | direct |
| 145 contracts (abstract, §IV) | phase5 line 113 | direct |
| B2 coverage 8.1%/37.2% (§II, §IV) | E19 + coverage config | direct |
| 583 escalated, 60.7/14.8/24.5 (§III-D, §V-C) | E21 | direct |
| 12.8/9.6/12.4 block rates (§V-E) | E22 | direct |
| 13 residuals, +0.0112, 0 new crossings (§V-F) | E20 | direct |
| Qwen 27.1 → 2.1 (§V-G) | E18 | direct |
| Benign 16/12/8, 0/25/42.9 (§V-G) | E23 | direct |
| Prompt 6.8/4.3/4.3/8.9 (§V-G) | E24 | direct |
| DeepSeek refusal (§V-G, limitations) | E25 | direct |
| Echo guard 34/34, 0/194 (§VI) | E26c | direct |
| "zero setup" (abstract, conclusion) | parser is one LLM call/session | **partial — overclaims** |
| "coverage incomplete (65/801)" attributed to ToolGate (§II) | that is this reimplementation's coverage | **partial — attribution** |
| ClawGuard "six injection benchmarks" (§II) | repo docs confirm InjecAgent + MCPTox only | **partial — unverified count** |
| "no head-to-head ... on InjecAgent or MCPTox" (§II) | literature audit in repo | partial — needs hedge |

## 8. Terminology lock

| Concept | Canonical | Symbol | Do not use |
|---|---|---|---|
| Request-derived policy | intent contract | C | "contract" alone (ambiguous vs ToolGate) |
| Baseline policy | ToolGate per-tool contract / tool contract | P, Q | "contract" alone |
| Semantic score | semantic score | S_sem | "similarity score" |
| Rule score | rule score | S_rule | "rule compliance" |
| Combined score | gate score | S | "confidence" |
| Operating point | threshold | τ | "cutoff" |
| Escalate half-width | half-width | δ | "margin" |
| Attack metric | ASR (InjecAgent); attack-influenced calls (MCPTox) | — | mixing the two |
| Utility proxy | valid rate (call-level) | — | "utility" alone |
| Setup metric | hand-authored contracts | — | "setup cost" without qualifier |

## 9. Conflicts between sources

| What | Where | Trusted | Decision |
|---|---|---|---|
| `S_sem` formula: raw cosine vs `(cos+1)/2` | paper Eq. 2 vs `scorer.py:30` | code | Fix equation |
| Contract notation `(A,K,H)` vs schema fields | paper Eq. 1 vs `intent_schema.json` | schema | Add one-sentence mapping |
| τ default 0.6 (design) vs 0.75 (runs) | blueprint Sec 5 vs paper/config | config + results | Paper is correct; blueprint is stale design text |
| "zero setup" vs one parser LLM call | paper abstract/conclusion vs §VI | §VI | Reword to "no per-tool authoring" |
| Two different "583" | contracts (E19) vs escalated calls (E21) | both correct | Label each |
| "enhanced" settings | benchmark term | — | Keep; not a banned-word use |

## 10. Venue and supervisor constraints

- IEEE conference template, A4, 6 pages including references, double-blind, ≤3 MB, Type-1 fonts.
- Supervisor voice guide: `docs/prompt.md` + `docs/writing-guideline.md`; no first person, no em
  dashes, no prose semicolons, banned AI-tell words, simple academic English.
- AI-use policy: acknowledgment says LLMs used only for language polishing.
- Deadline window: conference upload in `roadmap.md` Sprint 0 Part A.

## 11. Section status

| Section | Status | Main gaps |
|---|---|---|
| Abstract | Complete | "zero setup" overclaim; otherwise accurate |
| I Introduction | Complete | redundant "this study/this paper" sentences; unverified survey count |
| II Related work | Complete | attribution of B2 coverage; ClawGuard count; table header ambiguity |
| III Method | Complete | Eq. 2 mismatch; schema mapping missing; veto sets S=0 not stated |
| IV B2 baseline | Complete | 583 contracts vs calls ambiguity; attribution |
| V Evaluation/Results | Complete | 583 labels; mimicry wording; MCPTox failure wording |
| VI Limitations | Complete | tool-contract sentence reads as IntentGate's own |
| Conclusion | Complete | "zero setup" overclaim |
| Acknowledgment | Complete | — |

## 12. Open questions (ranked)

1. Which files did the author personally write? Needed for voice-profile confidence (currently low).
2. Is the artifact public at submission or only after acceptance? (Conclusion wording.)
3. May the post-hoc power sentence be replaced by effect sizes/CIs, or is it supervisor-required?
4. Confirm the intended meaning of "MCPTox failures cluster in classes no contract covers" (B2
   coverage vs IntentGate's request-level rules).
5. Verify the Ferrag et al. survey count before keeping any number ("more than thirty" was softened).
6. Exact submission deadline/portal policy for AI-use disclosure.
