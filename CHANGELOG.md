# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Professional repo docs: `LICENSE` (MIT), `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, this changelog.
- GitHub PR/issue templates and CI workflow running `pytest -q` on `dev` and `main`.
- `.gitattributes` for consistent line endings across Windows/macOS/Linux.
- `dev` integration branch workflow (feature branches -> `dev` -> `main`).
- Pinned benchmark versions in `configs/benchmark_versions.yaml`: InjecAgent @ `f19c9f2c`, ToolGate @ `976ad3f5`, AgentDojo @ `089ed468`, MCPTox snapshot 2026-09-11 (1,348 cases, 45 servers).
- Clone script downloads the MCPTox ZIP snapshot (git protocol is unsupported on anonymous.4open.science).
- `harness/adapters/injecagent.py`: case loader (safe `Tool Parameters` parsing, split/setting inference, deterministic subsets) + fixture tests (32 total).

### Fixed
- Untracked generated `src/intent_gate.egg-info/` and `pdfs/InjectAgent.pdf` (both covered by `.gitignore`).
- Corrected `literature_review.md` filename in README/blueprint; marked gitignored local-only paths.

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
