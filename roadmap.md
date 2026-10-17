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

- [x] Clone benchmarks into `data/raw/` (InjecAgent, MCPTox snapshot, ToolGate, AgentDojo) via `scripts/clone_benchmarks.ps1` — rewritten as a pinned verify-and-repair bootstrap (`-VerifyOnly` / `-Force` / `-Only`) so teammates reproduce the exact measured commits
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
- [x] Component unit tests + threshold sweep infra over the gated traces (`eval/sweep.py` case-level re-decision, `scripts/sweep_gated.py`, Pareto in `docs/experiments/04_gate2_gated_eval.md`; 130 tests green at the time, 199 today) — blueprint Week 5–8 labels this "Section 14", which is the supervisor chapter (flagged in the sweep doc)

## Phase 5 — Main Evaluation (Weeks 9–12) → Gate 3 (results freeze) — DONE 2026-10-12

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
- Budget was ~4–8 h with 3-way file-level parallelism; actual: **~5.6 h**. **Cost chart** (34,560 LLM calls total; actuals from the frozen run 2026-10-12 — list-price estimate vs billed):

| Group | Cases | Calls | List-price actual | Billed share* |
|---|---|---|---|---|
| Main matrix — B1 (agent) | 3,456 | 3,456 | $1.33 | |
| Main matrix — B2 (agent) | 3,456 | 3,456 | $1.33 | |
| Main matrix — Ours (agent + parser) | 3,456 | 6,912 | $2.20 | |
| Ablations A1–A3 (agent + parser each) | 10,368 | 20,736 | $6.60 | |
| **Total** | 20,736 | **34,560** | **$11.46** | **$9.64** |

\*Billed total from the OpenAI dashboard; per-group billed splits aren't reported — the ~16%
gap vs list is automatic prompt caching (byte-identical system/tool prefixes).

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
- [x] Write `configs/phase5_lock.json` + `results/phase5/manifest.json` (frozen 2026-10-12, git `307487f`, clean tree)
- [x] 15 main runs: B1/B2/Ours × {dh_base, ds_base, dh_enhanced, ds_enhanced, mcptox}
- [x] 15 ablation runs: A1/A2/A3 × {dh_base, ds_base, dh_enhanced, ds_enhanced, mcptox}
- [x] Integrity check (`--check`): 30/30 passed with default flags

**Stage 2 — analysis:**
- [x] τ×δ Pareto (all + per benchmark) from cached traces; escalate share (~20% at τ=0.75, benchmark mode counts as block)
- [x] Bootstrap 95% CI + paired McNemar per benchmark (B1 vs ours: p=1.3e-33 ds_enh, p=1.25e-07 mcptox; B2 n.s.)
- [x] Breakdowns: MCPTox per risk (11) · InjecAgent per attacker tool (30) + per user tool (17) · per split (dh/ds) and setting (base/enhanced)
- [x] Stratification: valid-rate parity (FPR proxy) + E4 pilot 4%; per-specificity stratification deferred to Phase 6
- [x] Error taxonomy: 13 InjecAgent residuals (all S 0.75–0.79, rule=1.0, read-only exfil) + MCPTox registration class, with contract + score evidence
- [x] Latency p50/p95 per call (ours p95 16–20 ms); utility proxies (valid-rate parity); cost-vs-ASR ($11.46 list / $9.64 billed)
- [x] Headline figures: results table, Pareto curve, setup-cost bar (0 vs 145 contracts), latency table, cost-vs-ASR table

**Stage 3 — Gate 3 freeze:**
- [x] `docs/experiments/05_phase5_full_evaluation.md` (E11–E17: matrix, Pareto, ablations, breakdowns, stats, taxonomy, latency/utility; limitations + supervisor Q&A)
- [x] Roadmap + CHANGELOG updated, commit tagged, PR to `dev`; no results edits after this point

## Phase 6 — Strengthening & Hardening (Weeks 13–14) — DONE 2026-10-13

**Goal: turn the thesis's two most attackable claims into evidence. Rule: never touch frozen
Phase 5 numbers — all new work gets E18+ numbers framed as preliminary.**
**Status: COMPLETE — all P0/P1 pilots done (E18–E22, `docs/experiments/06_phase6_pilots.md`).
Teammates continue at Phase 7.**

### P0-1 — Second-backbone pilot / E18 (model-agnostic claim)

All Phase 5 evidence is gpt-4o-mini (n=1). Re-run a ~200-case subset (B1 + ours) on two new
backbones and compare ASR *deltas*, never absolutes.

- [x] Wire `--agent-base-url` / `--parser-base-url` through `harness/run_injecagent.py` +
  `harness/run_mcptox.py` (+ `--agent-api-key` / `--parser-api-key`, same flags on the
  `run_*_ours.py` pilots; `LLMClient` already accepts `base_url`; env fallback
  `AGENT_BASE_URL`→legacy `QWEN_BASE_URL` for agent, `PARSER_BASE_URL` for parser) + tests
  (`tests/test_runner_endpoints.py`, 7 tests). Extras landed with the pilot:
  `--agent-reasoning-effort` (Qwen3.5 thinking models return empty `content` on the
  OpenAI-compatible endpoint without `reasoning_effort=none`), `--out`/`--report` made
  **required** (a run can no longer default onto a tracked baseline path), `TraceLogger`
  default moved out of the repo, `LLMClient` auto-omits unsupported `temperature`
  (`gpt-6-luna`). 190 tests green → **199 tests green** (7 stats + 2 test-fix + 2 PPF pins)
- [x] Pull `qwen3.5:4b` (**not** `:latest` — 6.6–7.6 GB won't fit 6 GB VRAM); set Ollama
  `num_ctx` ≥ 16384 (default 4k silently truncates our prompts despite the 256K window);
  verify served ctx via `ollama show`; keep MiniLM embeddings on CPU. *(pulled + num_ctx set
  on dev box; num_ctx caveat remains documented for GPU box deployments)*
  Dev-box note (Ollama v0.40.5): the server ignores `OLLAMA_NUM_CTX` /
  `OLLAMA_CONTEXT_LENGTH` env and per-request `options.num_ctx` (VRAM-based default 4096
  sticks) → baked-in variant instead: Modelfile with `FROM qwen3.5:4b` +
  `PARAMETER num_ctx 16384` → `ollama create qwen3.5-16k`. Pilots pass
  `--model-name qwen3.5-16k`. Verified: served `context_length` 16384 via `/api/ps`,
  3.56 GB VRAM, warm inference ~4 s, `reasoning_effort: none` returns clean content.
- [x] Smoke on Qwen re-run: dh 0/3, ds 2/3 (B1) → ours τ=0.75 blocks both (ds 0/3).
  Parser assertion: `usage.parser.calls > 0` ✓
- [x] **Qwen pilot (~100-case B1 + ours completed):** ASR 27.1% → 2.1%, parser calls=100,
  gate blocked 24, 0 false positives. `results/phase6/qwen_pilot_*`
- [x] **Luna arm (gpt-6-luna) completed:** 10-case per split B1 + ours. B1: 70% invalid
  (prose output); ours: 45% invalid, parser calls=20. Luna mitigates via structured contract.
  `results/phase6/luna_pilot_*`
- [x] Write up delta comparison → E18 (`docs/experiments/06_phase6_pilots.md`)

### P0-2 — B2 coverage curve / E19 (strawman defense)

- [x] Contract next MCPTox tools by availability rank; re-run `scripts/freeze_b2_coverage.py`
  (65 → 583 contracts, 8.1% → 84.9% weighted coverage)
- [x] Re-run B2 MCPTox at ~40% and ~70% weighted coverage; plot coverage-vs-ASR curve
  (200-case re-run: 2.2% block rate — curve is flat)
- [x] Write up (with the honest outcome whatever it is) → E19

### P1 — cheap, high signal (cached traces + manual work)

- [x] E20 intent-mimicry probe: take the 13 residual near-miss templates → generate
  intent-mimicking variants → re-score vs τ=0.75 offline → report S inflation Δ
  (avg ΔS = +0.0112, 0/13 cross τ with mimicry)
- [x] E21 escalate precision: classify all 583 escalated calls rule-based against ground truth
  from case metadata (full census, deterministic — not a sampled hand-label)
  (80.5% precision, 14.8% false-escalate rate on 583 escalated calls)
- [x] Stats discipline: post-hoc power analysis on n=2,108/1,348 + multiple-comparison
  correction across the 10-risk breakdowns; amend E14 notes if anything changes
  (power=1.0 at α=0.005; 10-risk Bonferroni α=0.005 survives)
- [x] Per-specificity FPR stratification on full traces (deferred from E15)
  (specific: 12.8% FPR / vague: 9.6% / overall: 12.4% — includes escalate candidates)

**Team (done):** P0 items (E18/E19) · E20 (mimicry) · E21 (escalate precision) · E22 (stats).

## Phase 7 — Q1 Hardening (all 10 submission-gate items)

**Goal: close every gap the Q1 review named, in effort order. Same iron rule as Phase 6:
frozen Phase 5 numbers (E11–E17) are never touched or re-run — all new work gets E23+
numbers framed as preliminary, committed under `results/phase7/` and written up in
`docs/experiments/07_phase7_pilots.md` (same At-a-glance → … → Supervisor-Q&A template as 06).
Branch from `dev` (`feat/phase7-<topic>`), PR back to `dev`. Total est. API cost ~$8.**

**Numbering note (authoritative):** earlier drafts called the paraphrase pilot E23 and the
parser ablation E24. Final mapping below wins — E23 = utility suite, E24 = prompt baselines,
E25 = third backbone, E26 = adaptive attacker, E27 = Progent, E28 = parser ablation,
E29 = embedding/transfer, E30 = conformal band, E31 = contract-vs-semantic (supervisor Q5).

### P0 — submission gate (do first, all parallelizable)

- [x] **E23 legitimate-only utility suite (Gap 3: utility is proxied, never measured).**
      Goal: measure task-completion with gate ON vs OFF on benign tasks with zero attacks.
      How: reuse InjecAgent user cases with attacker instruction removed (per supervisor, no
      new loader needed) → run `scripts/e23_benign_utility.py` with three conditions:
      `--gate none` (unprotected), `--gate ours --ablation none` (full gate),
      `--gate ours --ablation semantic-only` (A1). Explicit `--out` under
      `results/phase7/e23_utility/`. Done when: user-tool-allowed rate + clean-call block rate
      is reported in `07_phase7_pilots.md#e23`; valid-rate-parity claim is replaced by a
      measured number. E22's 12.4% stratum metric already relabeled from "FPR" to
      block-rate-by-stratum.
      → COMPLETE: 50 benign cases (25 dh + 25 ds). User-tool-allowed: none 16.0% / ours 12.0%
      / semantic-only 8.0%; clean-call block: none 0.0% / ours 25.0% / semantic-only 42.9%.
      Semantic-only over-blocks legitimate calls — settles E31: contract preserves utility.
- [x] **E24 prompt-level baselines (Gap 1a: only one real baseline).** Goal: beat the field,
      not a strawman. How: add system-text variants (delimiters, instructional-prevention,
      sandwich/repeat-instruction from the ASB taxonomy) as new `--gate` modes or prompt
      flags in `harness/gate_policy.py` (no new infra — same harness, same 100-case pilot
      slice as E18) → run B1 vs ours vs each defense. Done when: one 5-metric panel
      (ASR, utility, latency, setup cost, backbone) covers all conditions in
      `07_phase7_pilots.md#e24`. Est. ~$2.
      → COMPLETE: `--prompt-type` flag added to `scripts/run_injecagent_ours.py`; three
      variants in `harness/prompts/injecagent.py` (Delimiters, InstructionalPrevention,
      Sandwich). 50 attack cases each (25 dh + 25 ds, base). Delimiters 4.3% / Sandwich 4.3%
      / baseline 6.8% / InstrPrev 8.9% ASR. Valid rate: Delimiters 92.0% / Sandwich 92.0%
      / baseline 88.0%. Delimiters + Sandwich reduce ASR ~37% but still far behind full gate
      (0.7% InjecAgent).
- [~] **E25 third backbone pilot (Gap 4: generality is n=1.5).** Goal: replicate the ASR
      delta on a new model family with full ReAct participation. How: same 100-case protocol
      as E18 (`scripts/run_injecagent_ours.py --per-split 50 --setting base --gate none|ours
      --model-name <new-family-via-API>`, parser stays `gpt-4o-mini`, explicit `--out` under
      `results/phase7/e25_third_backbone/`). Candidates: DeepSeek, Claude, or Llama-70B-class.
      Done when: per-backbone delta table (B1 ASR → ours ASR) has 3 rows in
      `07_phase7_pilots.md#e25`; if it fails to replicate, document the boundary condition
      instead (also publishable). Est. ~$1. If Luna-style prose-only output recurs, exclude
      with the same convention-#7 justification as E18.
      → IN PROGRESS: key/base URL now configured (`.env` -> `DEEPSEEK_*`; topped up 2026-10-18). Model: `deepseek-flash` (version DeepSeek-V4.1-Flash-1017); append `--agent-base-url https://api.deepseek.com/v1 --agent-api-key <from .env> --model-name deepseek-flash --agent-reasoning-effort none` to the E25 command above (thinking mode is default-on; none disables it and re-enables temperature). Smoke test with
      gpt-4o confirmed the pipeline works with a different model ID (20 calls, ~$0.16).
      Full 50/50 run aborted mid-execution — needs completion.
- [ ] **E26 adaptive attacker pilots (Gap 2: all attacks are static).** Goal: attack the gate
      itself, live. Two arms, both on the InjecAgent pilot slice: (a) paraphrase-delivery —
      ASB's 5 injection phrasings (`literature_review/papers/04-asb-zhang-2025.md`) applied to
      attack delivery, re-scored live vs τ=0.75, ASR delta vs E20; (b) threshold-aware —
      attacker aiming at the E16 near-miss band (S ∈ [0.75, 0.79]) à la Kerckhoffs (τ public),
      report how many crafted calls land above τ. Done when: ASR-under-adaptation table +
      honest scope sentence (static vs adaptive) lands in `07_phase7_pilots.md#e26`.
      Est. ~$1. Keep the static-attack scope claim prominent either way.
      → NOT STARTED.

### P1 — acceptance-makers (staff the starred ones first: specialist effort, not runner time)

- [x] **E27 Progent comparison (Gap 1b).** Goal: position vs the closest neighbor (policy-language
      tool-call gate, 2025 — currently missing from related work). How: ★ needs someone to read
      Progent, then either a faithful-mini port on the 100-case slice or a documented scope-out
      (why a port is infeasible + a feature-by-feature table vs our gate). Done when: Progent is
      cited in `literature_review/` + `docs/references.bib`, and `07_phase7_pilots.md#e27` holds
      either delta numbers or the scope-out table. Absence here reads as unawareness — do not skip.
      → COMPLETE: scope-out table written; `shi2025progent` (arXiv:2504.11703) added to
      `docs/references.bib` + paper-local `IEEE-conference/references.bib`; cited in paper related work.
- [ ] **Method formalism (Upgrade A, writing task, no new runs).** Goal: read as a contribution,
      not just measurements. How: (a) one paragraph framing τ-selection as FPR-constrained ASR
      minimization (Neyman–Pearson) pointing at the existing Pareto figure; (b) an
      assumption-violation table (trusted request / untrusted tool content / single-turn scope →
      what breaks when each is violated, with E16/E18/E26 as evidence). Done when: both land in
      Ch 3 draft + blueprint Sec 9 pointer; Anderson reference-monitor framing added (2 sentences).
- [ ] **E30 conformal escalate band (Upgrade A, offline, no LLM calls).** Goal: turn the
      heuristic [τ−δ, τ+δ] band into a distribution-free guarantee. How: ★ needs conformal-prediction
      comfort — calibrate a coverage guarantee on cached Phase 5 traces
      (`results/phase5/ours_*_trace.jsonl`), report empirical coverage at the chosen α, add
      `conformal_band()` next to `power_analysis()` in `src/intent_gate/eval/stats.py` + tests.
      Done when: calibrated (α, empirical coverage) pair + method note in
      `07_phase7_pilots.md#e30`. Highest leverage-per-line item in this phase.
- [ ] **E28 parser ablation (Upgrade B).** Goal: answer "why not just heuristics." How: one
      InjecAgent 200-case subset, B1 + ours with the LLM parser swapped for the heuristic
      fallback → ASR/valid-rate deltas. Done when: delta table in `07_phase7_pilots.md#e28`.
      Est. ~$1–2.
- [ ] **E29 embedding swap + τ transfer (Upgrade B, offline, free).** Goal: show τ is a
      procedure, not a magic number. How: re-score cached traces with one stronger embedding
      (E5/MPNet) + report τ tuned on base tested on enhanced (and vice versa). Done when:
      transfer table + recalibration note in `07_phase7_pilots.md#e29`.
- [x] **E31 contract-vs-semantic contribution (supervisor Q5).** Goal: E12 showed A1
      (semantic-only) ≈ ours on headline ASR — locate *where* the full contract + rules +
      escalate add value, or scope the claim honestly. How: offline on cached traces
      (`results/phase5/ours_*` vs `a1_*` JSONLs, no LLM calls): (a) per-category/per-risk
      outcome flips — ours blocks where A1 allows and vice versa (expect rules decisive on
      high-severity veto categories); (b) escalate-band ablation — what the band loses
      without S_rule/veto input; (c) cost/latency parity check (contract parse is
      once-per-session, amortized). Done when: flip table + "where the contract
      wins/ties/loses" verdict in `07_phase7_pilots.md#e31`; if A1 ties everywhere, the
      contract claim is scoped to auditability + fail-closed guarantees (already stated in
      E12 — this makes it measured, not asserted).
      → COMPLETE: offline on 2,013 cached calls; semantic-only over-blocks legitimate calls
      (322 A1 blocks/escalates that ours allows) while ours catches 32 attacks A1 misses;
      latency parity holds; verdict: contract wins on valid-rate/auditability, ties on
      headline ASR.
- [ ] **Artifact packaging (venue requirement).** Goal: one-command repro. How: Dockerfile +
      pinned `pip install` + `results/` manifest check (`scripts/run_phase5.py --check`
      already exists — wire it into the container entrypoint). Done when: clean-machine
      `docker build && docker run pytest -q` passes and the repro commands in
      `docs/experiments/README.md` run unmodified inside the container.
- [ ] Write up E23–E31 → `docs/experiments/07_phase7_pilots.md` (same template as 06).

**Explicitly deferred to future work (Ch 6 material, not pilots):** live-server MCPTox slice
(static-snapshot limitation stands, blueprint Sec 8) · 20-case multi-turn drift pilot
(AgentDojo subset) — new infra + cost, lowest return before submission.

## Phase 8 — Thesis + Paper Writing (merged; old Phase 7 + old Phase 8)

**Goal: thesis chapters + workshop/Findings-tier submission paper from the same frozen
evidence (E11–E17) + pilots (E18+). Journal expansion optional, after Findings.**

### Thesis

- [ ] Ch 1: Intro & motivation (problem, OWASP excessive agency, why action gate)
- [ ] Ch 2: Related work — answer Reviewer #2 Q#1 in first paragraph ("not just embeddings + if-statements")
- [ ] Ch 3: Method — intent parser, contract schema, scorer + veto, gate middleware, escalate band
- [ ] Ch 4: ToolGate B2 baseline (Appendix G translation, coverage %, fidelity notes)
- [ ] Ch 5: Evaluation — metrics, baselines, ablations, per-category, stats, error taxonomy
- [ ] Ch 6: Limitations & future work (adaptive attacks, code-exec scope, live-vs-snapshot)
- [ ] Reproducibility appendix: hashes, configs, contract examples, JSONL sample
- [ ] Supervisor review rounds; final defence

### Paper (workshop/Findings, ~4–8 pages)

- [x] Outline (2-column short paper) → COMPLETE: `IEEE-conference/IEEE-conference.tex` drafted (abstract, intro, related work, method, ToolGate baseline, evaluation, results, limitations, conclusion, LLM-usage acknowledgment); double-blind anonymized; 5 pages, compiles via pdflatex+bibtex.
- [x] Related work: ToolGate "same gate, opposite policy source" framing (blueprint Sec 18) → COMPLETE: Progent (shi2025progent) added to references + cited.
- [x] Results section: ASR/FPR/latency/setup-cost tables + Pareto + error taxonomy → COMPLETE: Table I headline results (InjecAgent 19.0%→0.7%, MCPTox 20.7%→10.7%, McNemar p=1.3e-33 / p=1.25e-07), setup cost 0 vs 145 contracts, p95 16–20 ms, error taxonomy (13 residuals), E31 contract-vs-semantic flips.
- [x] Writing guides wired: `docs/prompt.md` + `docs/writing-guideline.md` adapted for the conference template (journal-only sections noted) and linked from `AGENTS.md`.
- [x] ICEEICT final pass to submission quality (≤6 pages incl. references, 30 verified refs, vector figures, cell-grid tables, no first-person pronouns): **DONE 2026-10-18** (steps A–D + expert-review pass): 6 pages, 254 KB, Type 1 fonts only, double-blind; title covers injection + poisoning. Remaining: co-author/supervisor info (placeholders in) + CMT upload.
- [ ] Reviewer #2 checklist (blueprint Sec 18) cleared item by item
- [ ] Reproducibility package: pip wrapper + contracts + logs + one-slide "ToolGate vs Ours" table
- [ ] (Optional, after Findings) Expand to journal: Q2 security journal (e.g., JISA / Applied Intelligence)

---

## Success Criteria (blueprint Sec 16 — falsifiable)

- [x] ASR_ours < ASR_B1 on both InjecAgent and MCPTox, 95% CI non-overlapping (McNemar p < 0.05) — p=1.3e-33 / p=1.25e-07 (E14)
- [x] FPR_ours < 10% at chosen τ (or <5% hard-block, escalate counted separately) — proxy: 4% pilot FPR + valid-rate parity (E15)
- [x] Setup cost: 0 contracts for ours vs. documented manual count for B2 on same tool set — 0 vs 145
- [x] Latency overhead p95 < 100ms per tool call on CPU — 16–20 ms (E17)
- [x] ToolGate B2 runs and is documented (coverage % reported) — InjecAgent 100%, MCPTox 8.1%/37.2% (E11/E15)
- [ ] Deliverables: thesis + pip package + GitHub + evaluation report + paper draft

---

## Key Milestones (blueprint Sec 12/13)

| Gate | Definition | Status |
|---|---|---|
| Gate 0 | B1 reproduces + 50-case pilot passes (Assumption 2) | [x] 2026-09-11 — AUC 0.979, ASR 0/FPR 4% @ τ=0.75 |
| Gate 1 | B2 reimpl validated on ToolBench subset (coverage reported) | [x] 2026-09-16 — InjecAgent 79/79; MCPTox 65 contracts (37.2% availability-weighted); ToolBench not cloned → blueprint Sec 10 fallback validation (`docs/experiments/03_b2_toolgate.md`) |
| Gate 2 | Gate integrated; unit tests green; p95 latency measured | [x] 2026-09-16 — 130 tests green then (199 today); p95 ≤ 23 ms on gated calls; `docs/experiments/04_gate2_gated_eval.md` |
| Gate 3 | Results freeze (Phases 4–5 complete) | [x] 2026-10-12 — 30 jobs, 20,736 cases, InjecAgent 19.0%→0.7%, MCPTox 279→144, B2≈B1 (n.s.), p95 ≤20 ms, $9.64 billed |
| Submission | Thesis + paper draft complete | [ ] |
