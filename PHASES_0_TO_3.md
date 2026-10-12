# IntentGate Thesis – Phases 0 to 3 Overview

This document summarises the design, implementation goals, and key deliverables for **Phases 0 through 3** of the Intent-Consistency Gate thesis project.  Each phase builds on the previous one and corresponds to a “Gate” milestone in the roadmap (`roadmap.md`).

---

## Phase 0 – Literature Review & Blueprint *(Completed 2026‑09‑11)*

| Aspect | What was done |
|--------|---------------|
| **Goal** | Synthesise 10 key papers (Q1–Q9) and produce a single source of truth – the **blueprint** (`docs/blueprint.md`, Sec 0‑18). |
| **Deliverables** | • `literature_review.md` + index<br>• 5 anchor reviews (AgentDojo, InjecAgent, MCPTox, ASB, ToolGate)<br>• `README.md` (project overview, structure, evaluation plan, quick‑start) |
| **Status** | All checklist items `[x]`. The blueprint is the design authority for every subsequent phase. |

**Key design decisions recorded in the blueprint**

* Fail‑closed contract defaults (missing fields → disallow).
* Intent‑contract schema (`intent_schema.json`) versioning.
* Scoring formula: **S = α·S_sem + (1‑α)·S_rule**.
* Gate result enum: `allow / block / escalate`.
* JSONL trace format: `S`, `S_sem`, `S_rule`, decision, latency, contract, embedding hash, `model_id`.

---

## Phase 1 – Project Structure Initialization *(Completed 2026‑09‑11)*

| Aspect | What was done |
|--------|---------------|
| **Goal** | Set up a clean, reproducible Python package layout and a full pytest suite (26/26 passing). |
| **Deliverables** | • `pyproject.toml`, `.python-version`, venv + `pip install -e .`<br>• Package skeleton `src/intent_gate/` with sub‑packages: `parser`, `scoring`, `gate`, `agent`, `baselines.toolgate`, `eval`.<br>• `harness/` stubs: `run_injecagent.py`, `run_mcptox.py`, `compare_b2.py`, `common.py`.<br>• `configs/`: `intent_schema.json`, `parser_fewshots.json`, `thresholds.yaml`, `models.yaml`.<br>• `scripts/`: `pilot_score_dist.py`, `check_parser.py`, `clone_benchmarks.ps1`.<br>• Licensing, security, contributing docs; GitHub CI (`pytest -q` on `dev`/`main`).<br>• Branch model: feature branch → `dev` → `main`. |
| **Status** | All 28 checklist items `[x]`. The repo is a fully functional, test‑covered skeleton. |

**Core types** (defined in `src/intent_gate/types.py`)

* `ToolCall` – name, arguments, kit.
* `IntentContract` – parsed intent, slots, constraints.
* `GateResult` – `allow`, `block`, `escalate`.

---

## Phase 2 – Foundation & Pilot *(Completed 2026‑09‑16) → Gate 0*

| Aspect | What was done |
|--------|---------------|
| **Goal** | Validate **Assumption 2**: the scorer separates hijack from legitimate traffic before building the full gate. Cheapest possible failure point. |
| **Benchmark cloning** | InjecAgent, MCPTox, ToolGate, AgentDojo snapshots stored under `data/raw/` with committed hashes (`configs/benchmark_versions.yaml`). |
| **Pilot scoring runs** | 50‑case scorer pilot → AUC 0.979, ASR 0 % / FPR 4 % at threshold τ = 0.75.  Three false‑positive rule‑engine findings were fixed. |
| **Intent schema v1.1** | Added `system_change`, 9 few‑shots, 30‑request re‑validation (`docs/experiments/02_parser_schema.md`). |
| **Goals met** | • B1 unprotected ReAct runs on 20 InjecAgent cases (≈ 20 % success) and 20 MCPTox cases (≈ 30 % attack‑influenced).<br>• Go/No‑Go decision: **GO** – Assumption 2 holds. |
| **Status** | All 41 checklist items `[x]`. The scorer and parser are production‑ready and integrated with the JSONL trace pipeline. |

**Key components introduced**

* `src/intent_gate/scoring/` – embedding backend (`all-MiniLM-L6-v2`), rule‑engine, combined scorer.
* `src/intent_gate/parser/` – real LLM intent parser (temp 0, JSON mode, 1 repair retry).
* JSONL trace format (see Phase 0) populated on every gate call.

---

## Phase 3 – ToolGate B2 Baseline *(Completed 2026‑09‑16) → Gate 1*

| Aspect | What was done |
|--------|---------------|
| **Goal** | Implement a **faithful minimal ToolGate** (Appendix G of the thesis) that can run side‑by‑side with the new intent gate. This defines the comparison baseline for the paper. |
| **Hoare contracts** | • InjecAgent: 79/79 user + attacker tools covered.<br>• MCPTox: 65 contracts over the 801‑tool registered snapshot → 8.1 % distinct / 37.2 % availability‑weighted. The long tail / poisoned registrations stay `no_contract`. |
| **Symbolic world‑state** | Fields: `balance`, `files`, `directories`, `permissions`. Snapshot/rollback on post‑violation, seeded from the trusted request. |
| **Coverage freeze** | `configs/b2_coverage.json` records the above percentages; `no_contract` / `no_contract_tools` are counted and reported in every run. |
| **Documented divergences** | `docs/experiments/03_b2_toolgate.md` explains why ToolBench was not cloned and how manual contract review was used instead. |
| **Status** | All 11 checklist items `[x]`. Gate 1 is validated; the B2 baseline is fully functional and its metrics are frozen for the Phase 5 evaluation freeze. |

**Core B2 modules**

* `src/intent_gate/baselines/toolgate/` – world‑state, contract checker, coverage reporting.
* `gate/` – integrates B2 contracts alongside the new intent‑gate scorer.
* `configs/b2_coverage.json` – frozen numbers, never silently allow a tool without a contract.

---

## Overall Flow (Phases 0‑3)

1. **Blueprint (Phase 0)** defines the intent‑contract schema, scoring formula, and gate decision logic.
2. **Skeleton (Phase 1)** supplies the package, tests, and configuration files that make the system runnable.
3. **Pilot validation (Phase 2)** proves the scorer can separate hijack from legitimate traffic; the gate is “Gate 0” – B1 unprotected runs.
4. **Baseline ToolGate (Phase 3)** adds formal Hoare contracts and a symbolic world‑state, producing the **Gate 1** comparison point (B2).

After Phase 3 the repository contains:

* **Full gate middleware** (`gate/`), allowing `allow / block / escalate` decisions.
* **Embedding‑based semantic score** (`S_sem`) and **rule‑based score** (`S_rule`).
* **JSONL trace** per tool call with `S`, `S_sem`, `S_rule`, decision, latency, contract, embedding hash, `model_id`.
* **B2 coverage data** and `no_contract` counters for reporting.
* **130+ unit tests** green (parser, veto, no‑bypass, ordering, metrics, ToolGate).

These foundations enable the remaining phases (4‑5) to perform full‑scale evaluation, threshold sweeps, ablations, and the final results freeze.

---

*File generated: `PHASES_0_TO_3.md`*