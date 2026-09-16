# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Gate 2 integration run (2026-09-16): B1 vs ours (τ=0.75) vs B2 on 100 InjecAgent + 100 MCPTox cases with real `all-MiniLM-L6-v2` embeddings — InjecAgent ASR-valid 9.0% → 1.0% (ours; 0 false-positive blocks), MCPTox attack-influenced 22 → 11 (13 malicious calls blocked), p95 ≤ 23 ms per gated call; results in `docs/experiments/gate2_integration.md`.
- Gated benchmark runner: `--gate {none,ours,toolgate}` for `harness/run_injecagent.py`, `harness/run_mcptox.py`, and the `scripts/run_*_ours.py` pilots; `harness/gate_policy.py` builds the policy from the trusted request before attacker content (ordering invariant), blocked attacker calls flip InjecAgent `succ`→`unsucc` and MCPTox → `blocked`, per-case `gate_events`/`gate_blocked` are written to the JSONL, and run-level model/embedding metadata goes to the gate trace.
- Gate 2 wiring: `AgentLoop` is a real ReAct loop (stable tool-prompt prefix, `Final Answer`/`Action`/JSON parsing, step cap) whose `execute` is `GateMiddleware.execute`; `ToolRegistry.describe()` provides the cacheable tool block (`tests/test_agent_loop_gate.py`).
- Trace provenance: `EmbeddingBackend.metadata` (model_id + functional probe hash + backend) logged on every JSONL record; `TraceLogger(metadata=...)` records run-level model/benchmark info; middleware caches the contract embedding per session (`score_call(contract_vec=...)`).
- Escalate-band tests: benchmark mode -> block + `would_escalate`; demo mode -> prompt accept/decline paths (`tests/test_no_bypass.py`).
- Professional repo docs: `LICENSE` (MIT), `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, this changelog.
- GitHub PR/issue templates and CI workflow running `pytest -q` on `dev` and `main`.
- `.gitattributes` for consistent line endings across Windows/macOS/Linux.
- `dev` integration branch workflow (feature branches -> `dev` -> `main`).
- Pinned benchmark versions in `configs/benchmark_versions.yaml`: InjecAgent @ `f19c9f2c`, ToolGate @ `976ad3f5`, AgentDojo @ `089ed468`, MCPTox snapshot 2026-09-11 (1,348 cases, 45 servers).
- Clone script downloads the MCPTox ZIP snapshot (git protocol is unsupported on anonymous.4open.science).
- `harness/adapters/injecagent.py`: case loader (safe `Tool Parameters` parsing, split/setting inference, deterministic subsets) + fixture tests (32 total).
- `scripts/run_injecagent_reference.py`: runs InjecAgent's own prompted-agent pipeline on a deterministic subset (S3a reference). Result: 20.0% ASR-valid first step on 20 base cases with `gpt-4o-mini` (paper ballpark ~24%) → harness trusted; see `docs/experiments/b1_reference_injecagent_20.md`.
- Gate-ready InjecAgent harness: vendored prompts (`harness/prompts/injecagent.py`), ported evaluator with differential parity test (`harness/parsing.py`), case runner emitting structured `ToolCall`s (`harness/injecagent_runner.py`), `scripts/run_injecagent_ours.py`. Our B1 run matches the authors' reference 20/20 case evals (20.0% ASR; `docs/experiments/b1_ours_injecagent_20.md`).
- MCPTox static snapshot support: adapter (`harness/adapters/mcptox.py`), heuristic runner/evaluator (`harness/mcptox_runner.py`), `scripts/run_mcptox_ours.py`. B1 n=20: 10% success, 30% attack-influenced; evaluator validated vs authors' labels (precision 0.82 / recall 0.26); see `docs/experiments/b1_mcptox_20.md`.
- LLM intent parser v1: JSON mode + one repair retry + fail-closed fallbacks (`IntentParser._parse_llm`), `build_parser()` factory, `response_format` support in `LLMClient`. Authorization rule + 4 extra few-shots fix over-blocking of explicit user side effects. Schema frozen v1 (`configs/intent_schema.json`); 30-request spot-check all-LLM (`docs/experiments/parser_spotcheck_v1.md`).
- Rule-engine fix: `_limit_allows` no longer treats the substring "no" as a denial (word-boundary prefixes only), so scoped authorizations ("allow: $500 to account 123") pass.

### Changed
- Literature review and docs reverted to the verified 5-review / 10-entry basis: the 2026-09-12 TraceGrant/IGAC addendum was removed intentionally; `roadmap.md`, `README.md`, `blueprint.md`, and `references.bib` are consistent again (blueprint typo fix included).

### Fixed
- ToolGate B2: real Hoare pre/postconditions keyed by harness tool names (`<Toolkit><Tool>`, e.g. `GmailSendEmail`), world-state effects with rollback on post violations, and coverage computed against the evaluated InjecAgent tool universe — frozen in `configs/b2_coverage.json` (`docs/experiments/gate1_b2.md`); `no_contract_tools` now tracked.
- Untracked generated `src/intent_gate.egg-info/` and `pdfs/InjectAgent.pdf` (both covered by `.gitignore`).
- Corrected `literature_review.md` filename in README/blueprint; marked gitignored local-only paths.
- Rule-engine category false positives found by the Gate 0 pilot: CamelCase benchmark tools now categorized via action keywords; read/search email tools no longer vetoed as "external send"; "shared calendar" no longer vetoed as sensitive sharing.

### Gate 0 (2026-09-11) — GO

- `scripts/build_pilot_set.py` (50 labeled calls from 25 InjecAgent cases) + rewritten
  `scripts/pilot_score_dist.py` (real embeddings, AUC, τ sweep). Result: **AUC 0.979,
  ASR 0% / FPR 4% at τ=0.75** → Assumption 2 passes (`docs/experiments/gate0_pilot.md`).
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
