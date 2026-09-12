# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Lit-review controlled unfreeze (2026-09-12, per roadmap + CHANGELOG rule): new reviews `literature_review/papers/06-tracegrant-liao-2026.md` (Closest/High — request-derived POEC contract, 0% ASR on AgentDojo/ASB, no InjecAgent/MCPTox, deterministic+stateful, no graded score/escalation) and `07-igac-zhu-2026.md` (Supporting/Medium-High — server-side intent certificate/manifest narrowing, no adversarial benchmarks, 36-trial external subset). Matrix, Quick Triage, Gap Map row 1, and Verification Log updated; Gap Map row 1 "None/Novel" claim superseded; 2 new BibTeX entries in `references.bib`.
- `blueprint.md` novelty/C2 claims narrowed to a graded (τ/δ, escalate) stateless zero-setup gate evaluated as **two separate benchmark studies** (InjecAgent injection, MCPTox tool poisoning, reported independently — per supervisor instruction, no combined cross-vector claim); README mirrored; roadmap Phase 8 related-work reframed to three-way gate comparison (ToolGate/TraceGrant/IGAC/Ours) + optional AgentDojo-subset TraceGrant-comparison stretch (Phase 6).
- `pdfs/` now holds `2608.21126v1.pdf` (TraceGrant) + `ssrn-7195899.pdf` (IGAC) (gitignored).
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

### Fixed
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
