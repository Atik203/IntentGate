# Roadmap — Intent-Consistency Gate Thesis

> Tracker for the thesis + paper. Single source of truth for progress: `docs/blueprint.md` (design), `roadmap.md` (status).
> Legend: `[x]` done · `[ ]` todo · `[~]` in progress · `Gate N` = blueprint Sec 12/13 milestone.
> Update this file in the same commit that completes a task.

---

## Phase 0 — Literature Review & Blueprint — DONE

- [x] 10-paper Q1–Q9 synthesis (`literature_review.md` + `literature_review/index.md`)
- [x] 5 anchor reviews in `literature_review/papers/` (AgentDojo, InjecAgent, MCPTox, ASB, ToolGate)
- [x] Master blueprint Sec 0–18 (`docs/blueprint.md` — single source of truth)
- [x] Repo `README.md` (project overview, structure, evaluation plan, quick start)

## Phase 1 — Project Structure Initialization — DONE (commit 3ff9e33)

- [x] `pyproject.toml` + `.python-version` + venv + pip (`pip install -e .`)
- [x] pytest suite: 26/26 passing (parser, veto, no-bypass, ordering, metrics, ToolGate)
- [x] `src/intent_gate/` skeleton: parser / scoring / gate / agent / baselines.toolgate / eval
- [x] `harness/` stubs: `run_injecagent.py`, `run_mcptox.py`, `compare_b2.py`, `common.py`
- [x] `configs/`: `intent_schema.json`, `parser_fewshots.json`, `thresholds.yaml`, `models.yaml`
- [x] `scripts/`: `pilot_score_dist.py`, `check_parser.py`, `clone_benchmarks.ps1`
- [x] `.env.example`, `data/README.md`, `results/.gitkeep`, `.gitignore` (venv, egg-info, data/raw, results)
- [x] Professional repo docs: `LICENSE` (MIT), `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`
- [x] GitHub PR/issue templates + CI workflow (`pytest -q` on `dev`/`main`)
- [x] Branch model: feature branch → `dev` → `main` (dev integration branch created)

## Phase 2 — Foundation & Pilot (Weeks 1–2) → Gate 0

**Goal: confirm Assumption 2 (scorer separates hijack from legit) before building the full gate. Cheapest place to fail.**

- [x] Clone benchmarks into `data/raw/` (InjecAgent, MCPTox snapshot, ToolGate, AgentDojo) via `scripts/clone_benchmarks.ps1`
- [x] Record exact commit hashes / snapshot versions (required for reproducibility, blueprint Sec 8) → `configs/benchmark_versions.yaml`
- [x] B1 unprotected ReAct runs on 20 InjecAgent cases — ballpark reproduced (20% ours = 20% authors' harness, paper ~24% GPT-4); our pipeline is gate-ready
- [x] B1 unprotected ReAct runs on 20 MCPTox cases (static snapshot fallback documented; 30% attack-influenced, heuristic evaluator)
- [x] 50-case scorer pilot (hijack vs legitimate S distributions) → `scripts/build_pilot_set.py` + `scripts/pilot_score_dist.py`
- [x] Go/No-Go decision on Assumption 2: **GO** — AUC 0.979, ASR 0% / FPR 4% at τ=0.75 (`docs/experiments/01_gate0_foundation.md`); three rule-engine FPs found and fixed
- [x] Intent schema **v1.1** (controlled unfreeze 2026-09-16: adds `system_change`, 9 few-shots, 30-request re-validation `docs/experiments/02_parser_schema.md`); v1 frozen 2026-09-11 with the original spot-check
- [x] `docs/references.bib` started (verified figures only) → 10 entries, `literature_review/index.md` frozen

## Phase 3 — ToolGate B2 Baseline (Weeks 3–4) → Gate 1

**Goal: faithful minimal ToolGate reimpl (Appendix G) ready to run side-by-side — the comparison that defines the paper.**

- [x] Author Hoare contracts for evaluated tool subset (InjecAgent 79/79 user+attacker tools; MCPTox 65 contracts over the 801-tool registered snapshot = 8.1% distinct / 37.2% availability-weighted — the long tail + poisoned registrations stay `no_contract`)
- [x] Symbolic world-state extended (`balance`, `files`, `directories`, `permissions`, per-tool fields) + snapshot/rollback on post violations + best-effort seeding from the trusted request
- [x] Validate B2 — ToolBench not cloned: blueprint Sec 10 fallback used (manual contract review vs official tool schemas + recorded-call replay; `docs/experiments/03_b2_toolgate.md`)
- [x] Freeze B2 coverage % — `configs/b2_coverage.json` (InjecAgent 100%; MCPTox 8.1% / 37.2% weighted); `no_contract`/`no_contract_tools` counted and reported
- [x] Document any divergence from ToolGate paper behavior honestly (`docs/experiments/03_b2_toolgate.md`; code changes + test suite green)

## Phase 4 — Gate Build (Weeks 5–8) → Gate 2

**Goal: working middleware — embed + rule + threshold + escalate + trace — wired to the agent loop.**

- [x] Real LLM intent parser (temp 0, JSON mode, 1 repair retry) replacing heuristic stand-in — landed in Phase 2 (`parser/parser.py`, `docs/experiments/02_parser_schema.md`)
- [x] Real embedding model (`all-MiniLM-L6-v2`) wired + model hash logged in every trace — `EmbeddingBackend.metadata` (model_id + probe hash + backend) on every JSONL record; contract embedded once per session, only the call per step
- [x] GateMiddleware integrated with `AgentLoop` (ReAct → gate → executor) — `agent/react.py` loop executes via `gate.execute`, tests in `tests/test_agent_loop_gate.py`
- [x] Escalate band: benchmark mode = block + `would_escalate`; demo mode = user prompt (`tests/test_no_bypass.py`)
- [x] No-bypass enforcement test green (direct executor access fails in harness) — loop + middleware integration tests pin the single execution path
- [x] 100-case integration run (InjecAgent + MCPTox); p95 latency measured — 100 InjecAgent + 100 MCPTox across none/ours/toolgate; ASR-valid 9.0% → 1.0% (ours, 0 FP blocks), p95 ≤ 23 ms (`docs/experiments/04_gate2_gated_eval.md`)
- [x] Component unit tests + threshold sweep infra over the gated traces (`eval/sweep.py` case-level re-decision, `scripts/sweep_gated.py`, Pareto in `docs/experiments/04_gate2_gated_eval.md`; 130 tests green) — blueprint Week 5–8 labels this "Section 14", which is the supervisor chapter (flagged in the sweep doc)

## Phase 5 — Main Evaluation (Weeks 9–12) → Gate 3 (results freeze)

**Goal: complete, reproducible results. Nothing gets rewritten after this.**

**Freeze before starting:** intent schema v1.1 · B2 contracts + `configs/b2_coverage.json` · runner `--gate none|ours|toolgate` · defaults τ=0.75, δ=0.1, α=0.7. The orchestrator writes a lock + manifest (git SHA, config hashes, model IDs, embedding hash) before the first full run; any code/config change after that = new freeze + full re-run.

**Decisions (locked 2026-09-16):** InjecAgent runs **base + enhanced (2,108 cases: dh 510 + ds 544 each)**; MCPTox = 1,348 snapshot cases. Ablations A1–A3 run on the **full matrix** (A4 is trace-derived). Utility = **proxies from the runs** (InjecAgent valid-rate + user-tool calls allowed; MCPTox ignored share). No LLM judge for MCPTox in Phase 5 (heuristic evaluator documented; report both `success` and attack-influenced).

**Run matrix** (identical prompts/tool blocks/model, seed 42, one run per cell):

| Condition | InjecAgent 2,108 (dh/ds × base/enhanced) | MCPTox 1,348 |
|---|---|---|
| B1 — none (unprotected) | full | full |
| B2 — toolgate (manual contracts) | full | full |
| Ours — intent gate, τ=0.75 | full | full |
| A1 — semantic-only | full | full |
| A2 — rule-only | full | full |
| A3 — raw-request embedding | full | full |

- 30 file-level runs, resumable; each writes report JSON + per-case JSONL + trace/gate events (S, S_sem, S_rule, decision, latency, contract, embedding hash, `model_id`, tokens/cost). Artifacts: `results/phase5/`.
- Budget: ~4–8 h with 3-way file-level parallelism. **Cost chart** (34,560 LLM calls total; smoke rates ≈ $0.0005/call agent-only, ≈ $0.00074/call for ours with parser):

| Group | Cases | Calls | Est. cost |
|---|---|---|---|
| Main matrix — B1 (agent) | 3,456 | 3,456 | ≈ $1.7 |
| Main matrix — B2 (agent) | 3,456 | 3,456 | ≈ $1.7 |
| Main matrix — Ours (agent + parser) | 3,456 | 6,912 | ≈ $2.6 |
| Ablations A1–A3 (agent + parser each) | 10,368 | 20,736 | ≈ $7.7 |
| **Total** | 20,736 | **34,560** | **≈ $14 (plan $15–20 with MCPTox long prompts + rerun margin)** |

Per benchmark: InjecAgent 2,108 cases × 6 conditions = 12,648 agent calls (+8,432 parser); MCPTox 1,348 × 6 = 8,088 agent (+5,392 parser). `scripts/run_phase5.py --dry-run` prints the live estimate.

**Stage 0 — pre-run engineering (must land before the freeze):**
- [x] Gate every proposed call (user + attacker), not only attack-relevant ones — per-call decision/latency in `gate_events` (FPR proxy + full latency samples)
- [x] Wire ablations A1–A3 (`--ablation semantic-only|rule-only|raw-request`), ablation tag in trace metadata
- [x] Exact McNemar (+ continuity-corrected variant) and seeded bootstrap CI (10k) in `eval/stats.py`, with tests
- [x] τ×δ sweep grid (τ ∈ {0.40–0.80 step 0.05} × δ ∈ {0.05, 0.10, 0.15}) + escalate share per cell
- [x] Token/cost logging captured per run
- [x] `scripts/run_phase5.py` orchestrator: resume, `--jobs` parallelism, retry/backoff, `--max-calls` guard, lock/manifest, `--check` integrity mode
- [x] `scripts/report_phase5.py` reporter: tables, breakdowns (risk/tool/split/setting), stratification, CIs/McNemar, τ×δ Pareto, latency/utility, cost-vs-ASR
- [x] Smoke runs (5 cases per condition) green before the freeze — events/latency/cost/ablation paths verified

**Stage 1 — freeze + full runs:**
- [ ] Write `configs/phase5_lock.json` + `results/phase5/manifest.json` (requires clean tree)
- [ ] 15 main runs: B1/B2/Ours × {dh_base, ds_base, dh_enhanced, ds_enhanced, mcptox}
- [ ] 15 ablation runs: A1/A2/A3 × {dh_base, ds_base, dh_enhanced, ds_enhanced, mcptox}
- [ ] Integrity check (`--check`): case counts, valid rates, parser backends, hashes, `no_contract` counts

**Stage 2 — analysis:**
- [ ] τ×δ Pareto (all + per benchmark) from cached traces; escalate share
- [ ] Bootstrap 95% CI + paired McNemar per benchmark (B1 vs ours; ours vs B2)
- [ ] Breakdowns: MCPTox per risk (10) · InjecAgent per attacker tool + per user tool · per split (dh/ds) and setting (base/enhanced)
- [ ] Stratification: vague vs specific FPR proxy; B2 `no_contract` share
- [ ] Error taxonomy: ~50 sampled failures per benchmark ({FPR case, false negative, B2 coverage, over-strict}) with contract + score evidence
- [ ] Latency p50/p95 per call and per case; utility proxies; cost-vs-ASR
- [ ] Headline figures: results table, Pareto curve, setup-cost bar (0 vs 144 contracts), latency table, cost-vs-ASR table

**Stage 3 — Gate 3 freeze:**
- [ ] `docs/experiments/05_phase5_full_evaluation.md` (E11–E17: matrix, Pareto, ablations, breakdowns, stats, taxonomy, latency/utility; limitations + supervisor Q&A)
- [ ] Roadmap + CHANGELOG updated, commit tagged, PR to `dev`; no results edits after this point

## Phase 6 — Stretch & Hardening (Weeks 13–14)

**Goal: only if Phase 5 finishes with buffer. Core deliverable = injection + poisoning only.**

- [ ] (Optional) 20-case multi-turn drift pilot (AgentDojo subset) — include as "preliminary" or defer
- [ ] (Optional) 20-case paraphrase-robustness mini-pilot (defense-aware paraphrase)
- [ ] Decide: drift pilot in thesis (preliminary) or future work — one figure max

## Phase 7 — Thesis Writing (Weeks 13–16)

- [ ] Ch 1: Intro & motivation (problem, OWASP excessive agency, why action gate)
- [ ] Ch 2: Related work — answer Reviewer #2 Q#1 in first paragraph ("not just embeddings + if-statements")
- [ ] Ch 3: Method — intent parser, contract schema, scorer + veto, gate middleware, escalate band
- [ ] Ch 4: ToolGate B2 baseline (Appendix G translation, coverage %, fidelity notes)
- [ ] Ch 5: Evaluation — metrics, baselines, ablations, per-category, stats, error taxonomy
- [ ] Ch 6: Limitations & future work (adaptive attacks, code-exec scope, live-vs-snapshot)
- [ ] Reproducibility appendix: hashes, configs, contract examples, JSONL sample
- [ ] Supervisor review rounds; final defence

## Phase 8 — Paper Draft (parallel, Weeks 12–16)

**Goal: workshop/Findings-tier submission; journal expansion optional.**

- [ ] Workshop/Findings outline (2-column short paper, ~4-8 pages)
- [ ] Related work: ToolGate "same gate, opposite policy source" framing (blueprint Sec 18)
- [ ] Results section: ASR/FPR/latency/setup-cost tables + Pareto + error taxonomy
- [ ] Reviewer #2 checklist (blueprint Sec 18) cleared item by item
- [ ] Reproducibility package: pip wrapper + contracts + logs + one-slide "ToolGate vs Ours" table
- [ ] (Optional, after Findings) Expand to journal: Q2 security journal (e.g., JISA / Applied Intelligence)

---

## Success Criteria (blueprint Sec 16 — falsifiable)

- [ ] ASR_ours < ASR_B1 on both InjecAgent and MCPTox, 95% CI non-overlapping (McNemar p < 0.05)
- [ ] FPR_ours < 10% at chosen τ (or <5% hard-block, escalate counted separately)
- [ ] Setup cost: 0 contracts for ours vs. documented manual count for B2 on same tool set
- [ ] Latency overhead p95 < 100ms per tool call on CPU
- [ ] ToolGate B2 runs and is documented (coverage % reported)
- [ ] Deliverables: thesis + pip package + GitHub + evaluation report + paper draft

---

## Key Milestones (blueprint Sec 12/13)

| Gate | Definition | Status |
|---|---|---|
| Gate 0 | B1 reproduces + 50-case pilot passes (Assumption 2) | [x] 2026-09-11 — AUC 0.979, ASR 0/FPR 4% @ τ=0.75 |
| Gate 1 | B2 reimpl validated on ToolBench subset (coverage reported) | [x] 2026-09-16 — InjecAgent 79/79; MCPTox 65 contracts (37.2% availability-weighted); ToolBench not cloned → blueprint Sec 10 fallback validation (`docs/experiments/03_b2_toolgate.md`) |
| Gate 2 | Gate integrated; unit tests green; p95 latency measured | [x] 2026-09-16 — 130 tests green; p95 ≤ 23 ms on gated calls; `docs/experiments/04_gate2_gated_eval.md` |
| Gate 3 | Results freeze (Phases 4–5 complete) | [ ] |
| Submission | Thesis + paper draft complete | [ ] |
