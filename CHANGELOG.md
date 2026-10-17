# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Roadmap reshuffle (Phase 6 DONE, Phase 7 Q1 hardening, Phase 8 writing merged):** Phase 6 marked complete (P2 section removed); new Phase 7 holds all 10 submission-gate items as E23–E31 checkboxes with commands + done-criteria (E23 utility suite, E24 prompt baselines, E25 third backbone, E26 adaptive attacker, E27 Progent, E28 parser ablation, E29 embedding/transfer, E30 conformal band, E31 contract-vs-semantic per supervisor feedback, plus formalism + artifact packaging — live-server slice and drift pilot explicitly deferred to future work); old thesis-writing Phase 7 + paper-draft Phase 8 merged into one Phase 8. `team_guide.md` §6, experiments hub, and the 05-report limitation pointer updated to match.
- **Phase 6 P0-1 Qwen pilot support:** `reasoning_effort` on `LLMClient` + `--agent-reasoning-effort` (CLI > `AGENT_REASONING_EFFORT`) across all four runners — Qwen3.5 thinking models return empty `content` on the OpenAI-compatible endpoint without it (use `--agent-reasoning-effort none`); 6 tests.
- **Phase 6 P0-1 endpoint wiring:** `--agent-base-url` / `--parser-base-url` (+ `--agent-api-key` / `--parser-api-key`) on both harness runners and the `run_*_ours.py` pilots; CLI > env (`AGENT_BASE_URL`→legacy `QWEN_BASE_URL` for agent, `PARSER_BASE_URL` for parser — parser stays on default unless overridden); base URLs logged in trace/report metadata (keys never logged). `.env.example` documents all six vars; local `.env` gained empty placeholders. 7 tests (`tests/test_runner_endpoints.py`).
- **Phase 6 E18 second-backbone pilot:** Qwen3.5:4b + gpt-6-luna pilots on 200+20 cases — Qwen ASR 27.1%→2.1%, Luna 70%→45% invalid. Parser calls asserted > 0. `docs/experiments/06_phase6_pilots.md`.
- **Phase 6 E19 B2 coverage curve:** Extended MCPTox contracts 65→583 (8.1%→84.9% weighted); offline projection + 200-case re-run confirm flat coverage-vs-ASR curve. Structural weakness, not coverage-limited.
- **Phase 6 E20 intent-mimicry probe:** 13 residual near-miss cases + 3 mimicry variants each; avg S inflation +0.0112, 0/13 cross τ=0.75. `scripts/e20_intent_mimicry.py`.
- **Phase 6 E21 escalate precision:** Ground-truth classification of 583 escalated calls from Phase 5 traces; 80.5% precision, 14.8% false-escalate rate. `scripts/e21_escalate_precision.py`.
- **Phase 6 E22 stats discipline:** `power_analysis()`, `bonferroni_alpha()`, `per_specificity_fpr()` added to `src/intent_gate/eval/stats.py`; post-hoc power = 1.0 at α=0.005 for both benchmarks; 10-risk Bonferroni survives. 7 new tests.
- **Phase 6 documentation:** `docs/experiments/06_phase6_pilots.md` (E18–E22, full template). E22's 12.4% stratum metric relabeled from "FPR" to "block-rate-by-stratum" (blocked calls include escalate candidates, not pure false positives).
- **Phase 7 E23 benign utility suite:** `scripts/e23_benign_utility.py` — 50 benign cases (25 dh + 25 ds), three conditions. User-tool-allowed: none 16.0% / ours 12.0% / semantic-only 8.0%; clean-call block: none 0.0% / ours 25.0% / semantic-only 42.9%. Settles E31: contract preserves utility, semantic-only over-blocks.
- **Phase 7 E24 prompt baselines:** `--prompt-type` flag added to `scripts/run_injecagent_ours.py`; three variants in `harness/prompts/injecagent.py` (Delimiters, InstructionalPrevention, Sandwich). 50 attack cases each. Delimiters and Sandwich reduce ASR 6.8%→4.3%, improve valid rate 88.0%→92.0%. Instructional Prevention worsens ASR to 8.9%.
- **Phase 7 E31 contract-vs-semantic (supervisor Q5):** offline comparison of cached Phase 5 `ours_*` vs `a1_semantic_only_*` traces (2,013 calls, no LLM calls) via `scripts/e31_contract_vs_semantic.py`. Semantic-only over-blocks legitimate calls (322 calls A1 blocks/escalates that ours allows) while ours catches 32 attacks A1 misses; latency parity holds (p95 within ~2 ms). Contract shifts operating point toward valid-rate parity; headline ASR ties. Report in `results/phase7/e31_contract_vs_semantic/`; write-up in `docs/experiments/07_phase7_pilots.md#e31`.
- **Phase 7 E27 Progent comparison:** scope-out table (no port) positioning vs `shi2025progent` (arXiv:2504.11703, deterministic symbolic privilege-control DSL, per-tool policy authoring, AgentDojo/ASB). Added `shi2025progent` to `docs/references.bib` and paper-local `IEEE-conference/references.bib`; cited in related work. Write-up in `docs/experiments/07_phase7_pilots.md#e27`.
- **ICEEICT 2027 paper draft:** `IEEE-conference/IEEE-conference.tex` replaced IEEE placeholder body with real double-blind content (abstract, intro, related work, method with scorer $S=\alpha\cdot S_{sem}+(1-\alpha)\cdot S_{rule}$, ToolGate baseline, evaluation, results, limitations, conclusion, LLM-usage acknowledgment); all 10 bib keys cited; PDF builds cleanly via pdflatex+bibtex (5 pages, ~187 KB, fonts embedded, ≤3 MB).
- **Phase 5 Gate 3 freeze (E11–E17, `docs/experiments/05_phase5_full_evaluation.md`):** 30-job frozen matrix (20,736 cases, τ=0.75) — InjecAgent 19.0%→0.7%, MCPTox 279→144; B2 ≈ B1 (n.s.) vs ours p<1e-6; p95 16–20 ms; $11.46 list / $9.64 billed.
- **Phase 5 run infrastructure:** case-level `--resume` (7 tests), live `tqdm` bar over flushed JSONLs (`mininterval=30`), `--max-calls` 30k→40k, freeze-integrity guard against matrix/limit/settings drift (5 tests); `tqdm` declared in deps.
- **Benchmark bootstrap rewrite:** `clone_benchmarks.ps1` as pinned verify-and-repair from `configs/benchmark_versions.yaml` (`-VerifyOnly`/`-Force`/`-Only`); `data/README.md` as teammate entry point.
- **Tracked-`results/` hygiene:** `AGENTS.md`/`CONTRIBUTING.md` state the real rules; `.gitignore` += `*.egg-info/`, `node_modules/`, `config.bat`; egg-info untracked; MCPTox count corrected to 801 registered.
- **Team guide** with Gate 0→Gate 3 results, cost chart, FAQ; cross-linked from all hubs.
- **Phase 5 Stage 0 tooling:** per-call `gate_events`, A1–A3 ablations, McNemar + bootstrap CI, τ×δ sweep grid, token/cost tracking, orchestrator (freeze/`--check`), reporter; smoke-verified. 170 tests green.
- **B2 MCPTox contracts (65)** + request-seeded world state; coverage 8.1%/37.2% weighted.
- **Error taxonomy + rule fixes** (destructive-file keywords, path-scope, shell-operator guard; pilot FPR still 4%).
- **Threshold sweep infra** with knee at τ=0.75; **Gate 2 integration run** (100+100 cases, 9→0 / 22→11, p95 ≤23 ms).
- **Gated runner + Gate 2 wiring** (`--gate none|ours|toolgate`, `gate_policy.py`, `AgentLoop` via `GateMiddleware.execute`, trace provenance, escalate-band tests).
- **Repo scaffolding:** LICENSE/SECURITY/CONTRIBUTING/CoC, PR/issue templates, CI on dev/main, `.gitattributes`, dev-branch workflow, pinned `benchmark_versions.yaml`.
- **Adapters + LLM parser v1** (InjecAgent/MCPTox loaders, runners, JSON-mode parser with repair retry, schema v1 + spot-checks, `_limit_allows` word-boundary fix).

### Changed
- `--out` (`scripts/run_*_ours.py`) and `--report` (`harness/run_*.py`) are now **required** so a run can never default onto a tracked baseline path and clobber committed results; pilot `--tau` default aligned to the frozen 0.75; doc examples updated.
- Phase 6 restructured into step-by-step checkboxes (P0 backbone pilot E18 + B2 curve E19, P1 probes E20–E21 + stats, P2 buffer items); parked until the team says go.
- Docs hub status snapshot → Gate 3 ✅ with frozen headlines; team guide gains §4.8 (Gate 3 results) and drops the credit-blocker framing; blueprint timeline marks W9–12 done.
- Intent schema **v1.1** (controlled unfreeze): `system_change` limit, 9 few-shots, token-exact `system` rule; 30-request re-validation (E6).
- Docs restructure: `blueprint.md`/`setup.md`/`references.bib` → `docs/`; 10 experiment notes merged into indexed reports (merge map in `docs/experiments/README.md`).

### Fixed
- `LLMClient` auto-omits `temperature` when a model rejects `0.0` (e.g. `gpt-6-luna`, which only accepts its default temp=1), emitting a stderr warning; models that accept 0 are unchanged. 2 tests.
- `TraceLogger` default path moved out of the repo (`<tmp>/intent_gate/gate_trace.jsonl`) so bare/default gate instances (tests, `build_policy_factory` without a trace) no longer append to the tracked `results/gate_trace.jsonl`; 1 test.
- B2 fidelity: real Hoare pre/postconditions keyed by harness tool names, world-state rollback, coverage vs evaluated universe (`b2_coverage.json`); `no_contract_tools` tracked.
- Rule-engine FP fixes from the Gate 0 pilot (CamelCase action keywords, read/search-mail + shared-calendar vetoes, `_limit_allows` word boundaries).
- `count_messages` contract added to MCPTox contracts; 2 tests updated to use `nonexistent_tool_xyz` instead of `count_messages` as the no-contract fixture (199 tests green).
- Untracked `src/intent_gate.egg-info/` (now gitignored); `literature_review.md` path corrections.

### Gate 0 (2026-09-11) — GO

- `scripts/build_pilot_set.py` (50 labeled calls from 25 InjecAgent cases) + rewritten
  `scripts/pilot_score_dist.py` (real embeddings, AUC, τ sweep). Result: **AUC 0.979,
  ASR 0% / FPR 4% at τ=0.75** → Assumption 2 passes (`docs/experiments/01_gate0_foundation.md`).
- Default τ updated to 0.75 in `configs/thresholds.yaml` (Phase 5 still sweeps 0.4–0.8).
- Test-time embeddings fall back offline via `INTENT_GATE_OFFLINE_EMBEDDINGS` (CI stays fast).
- `references.bib` (10 papers) added; `literature_review/index.md` frozen for Phase 2. Entries with unverified details carry explicit verification notes.

## [0.1.0] - 2026-09-06

### Added
- Project scaffold: `pyproject.toml`, `src/intent_gate/` package (parser, scoring, gate, agent, baselines/toolgate, eval).
- Intent parser with fail-closed schema coercion and offline heuristic stand-in (`parser/`).
- Scoring stack: embedding backend with hash fallback, hard-rule engine, fused scorer with critical veto (`scoring/`).
- Gate middleware with allow/block/escalate decisions and per-call JSONL tracing (`gate/`).
- ToolGate B2 baseline: symbolic world-state, per-tool Hoare contracts, `no_contract` coverage counter (`baselines/toolgate/`).
- Harness entry points: `harness/run_injecagent.py`, `harness/run_mcptox.py`, `harness/compare_b2.py`, `harness/common.py` (ordering guard).
- Configs: `configs/intent_schema.json`, `parser_fewshots.json`, `thresholds.yaml`, `models.yaml`.
- Scripts: `scripts/pilot_score_dist.py`, `scripts/check_parser.py`, `scripts/clone_benchmarks.ps1`.
- Test suite: 26 tests covering parser schema, scorer veto, no-bypass, ordering invariant, metrics, ToolGate baseline.
- Docs: `README.md`, `setup.md`, `roadmap.md` (Phases 0-8, Gates 0-3), `AGENTS.md` (agent conventions + LLM cache guidance).
- Literature review: `literature_review/index.md` + 5 anchor paper reviews; master `blueprint.md`.
