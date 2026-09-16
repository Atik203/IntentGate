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

**Freeze before starting:** intent schema v1.1 · B2 contracts + `configs/b2_coverage.json` · runner `--gate none|ours|toolgate` · defaults τ=0.75, δ=0.1, α=0.7. Any change after the first full run = new freeze + full re-run.

**Run matrix** (identical prompts/tool blocks/model for every condition; seed 42):

| Condition | InjecAgent — 1,054 cases (dh+ds × base+enhanced) | MCPTox — 1,348 snapshot cases |
|---|---|---|
| B1 — none (unprotected) | full | full |
| B2 — toolgate (manual contracts) | full | full |
| Ours — intent gate, τ=0.75 | full | full |

- Runner: `harness/run_injecagent.py`, `harness/run_mcptox.py`; run one case-file/setting at a time so failures are resumable; each run writes report JSON + per-case JSONL + gate-trace JSONL (S, S_sem, S_rule, decision, latency, contract, embedding hash, `model_id`).
- Budget: ≈6.6k agent calls + ≈2.1k parser calls (ours) on `gpt-4o-mini` (est. $10–20, ~2–4 h wall-clock); log tokens/cost per run; artifacts under `results/phase5/`.

- [ ] Full runs B1 vs B2 vs Ours on the matrix above (all 6 file-level runs per condition)
- [ ] Integrity check per run: case counts, valid rates, `no_contract` counts, parser backends, model/embedding hashes present in every trace
- [ ] τ ∈ {0.40–0.80 step 0.05} × δ ∈ {0.05, 0.10, 0.15} sweep → ASR–FPR Pareto from cached traces (no re-runs; `scripts/sweep_gated.py`)
- [ ] Ablations A1–A4 + optional A5 — A1 semantic-only (no rule veto) · A2 rule-only (no embeddings) · A3 raw-request embedding vs structured contract · A4 hard-block only vs escalate-as-block · A5 B2 with seeded file state (baseline sensitivity)
- [ ] Breakdowns: MCPTox per-risk-category (10) · InjecAgent per-tool (user vs attacker tools) · per split (dh/ds) and setting (base/enhanced)
- [ ] Stratification: vague vs specific contracts (`specificity`) for FPR; `no_contract` share for B2; escalate share at each τ
- [ ] Statistics: bootstrap 95% CI (10k resamples) on ASR/FPR + paired McNemar B1 vs ours per case, per benchmark (report CIs and p-values, never a single point)
- [ ] Error taxonomy: ~50 sampled failures per benchmark, classes {FPR case, false negative, B2 coverage, over-strict}, with contract + score evidence (`scripts/error_taxonomy.py` at scale)
- [ ] Latency: p50/p95 per call and per case from traces (target p95 < 100 ms) + benign-task utility retention
- [ ] Headline figures: results table, Pareto curve, setup-cost bar (0 vs 144 contracts), latency table, cost-vs-ASR table
- [ ] Gate 3 freeze: tag the commit, freeze `docs/experiments/05_phase5_full_evaluation.md`, update roadmap + CHANGELOG (no edits to results after this point)

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
