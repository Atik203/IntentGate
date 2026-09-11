# Roadmap — Intent-Consistency Gate Thesis

> Tracker for the thesis + paper. Single source of truth for progress: `blueprint.md` (design), `roadmap.md` (status).
> Legend: `[x]` done · `[ ]` todo · `[~]` in progress · `Gate N` = blueprint Sec 12/13 milestone.
> Update this file in the same commit that completes a task.

---

## Phase 0 — Literature Review & Blueprint — DONE

- [x] 10-paper Q1–Q9 synthesis (`literature_review.md` + `literature_review/index.md`)
- [x] 5 anchor reviews in `literature_review/papers/` (AgentDojo, InjecAgent, MCPTox, ASB, ToolGate)
- [x] Master blueprint Sec 0–18 (`blueprint.md` — single source of truth)
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
- [ ] 50-case scorer pilot (hijack vs legitimate S distributions) → `scripts/pilot_score_dist.py` filled with real labeled cases
- [ ] Go/No-Go decision on Assumption 2 (blueprint Sec 0/Sec 13 step 4); if overlap → rule-heavier redesign (A2) or LLM-as-judge (A4)
- [ ] Freeze `intent_schema.json` + 3 few-shot examples; spot-check parser on 30 diverse requests
- [ ] `references.bib` started (verified figures only)

## Phase 3 — ToolGate B2 Baseline (Weeks 3–4) → Gate 1

**Goal: faithful minimal ToolGate reimpl (Appendix G) ready to run side-by-side — the comparison that defines the paper.**

- [ ] Author Hoare contracts for evaluated tool subset (InjecAgent 17 + MCPTox subset, NOT all 353)
- [ ] Symbolic world-state extended (`balance`, `files`, `permissions`, per-tool fields)
- [ ] Validate B2 on ToolBench/MCP-Universe subset (~50 tasks) — fidelity check
- [ ] Freeze B2 coverage %; `no_contract` counted and reported (gap visible, not hidden)
- [ ] Document any divergence from ToolGate paper behavior honestly

## Phase 4 — Gate Build (Weeks 5–8) → Gate 2

**Goal: working middleware — embed + rule + threshold + escalate + trace — wired to the agent loop.**

- [ ] Real LLM intent parser (temp 0, JSON mode, 1 repair retry) replacing heuristic stand-in
- [ ] Real embedding model (`all-MiniLM-L6-v2`) wired + model hash logged in every trace
- [ ] GateMiddleware integrated with `AgentLoop` (ReAct → gate → executor)
- [ ] Escalate band: benchmark mode = block + `would_escalate`; demo mode = user prompt
- [ ] No-bypass enforcement test green (direct executor access fails in harness)
- [ ] 100-case integration run (InjecAgent + MCPTox); p95 latency measured
- [ ] Unit tests per blueprint Sec 14 + threshold sweep infra (`eval/sweep.py`)

## Phase 5 — Main Evaluation (Weeks 9–12) → Gate 3 (results freeze)

**Goal: complete, reproducible results. Nothing gets rewritten after this.**

- [ ] Full runs B1 vs B2 vs Ours: InjecAgent (1,054 cases) + MCPTox (1,348 or snapshot)
- [ ] τ ∈ {0.4–0.8} × δ ∈ {0.05–0.15} sweep → ASR–FPR Pareto curve (from cached traces, no re-runs)
- [ ] Ablations A1–A4 (semantic-only / rule-only / raw-request / threshold-escalate)
- [ ] Per-risk-category breakdown (MCPTox 10 categories) + per-tool breakdown (InjecAgent 17 tools)
- [ ] Bootstrap 95% CI on ASR + paired McNemar (B1 vs ours, per case)
- [ ] Error taxonomy: ~50 sampled failures per benchmark (FPR case / false negative / B2 coverage / over-strict)
- [ ] Headline figures: results table, Pareto curve, setup-cost bar, latency table, cost-vs-ASR table

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
| Gate 0 | B1 reproduces + 50-case pilot passes (Assumption 2) | [ ] |
| Gate 1 | B2 reimpl validated on ToolBench subset (coverage reported) | [ ] |
| Gate 2 | Gate integrated; unit tests green; p95 latency measured | [ ] |
| Gate 3 | Results freeze (Phases 4–5 complete) | [ ] |
| Submission | Thesis + paper draft complete | [ ] |
