# Phase 7 Pilots — ICEEICT 2027 submission (E23–E31)

Template: At a glance → Goal → Setup → Results → Artifacts → Limitations → Supervisor Q&A (same as 06).

## E23 — Legitimate-only utility suite (Gap 3)
- Status: [x] complete
- Goal: measure task-completion with gate ON vs OFF on benign tasks (zero attacks).
- Setup: reuse InjecAgent user cases with attacker instruction removed (per supervisor); ran
  `scripts/e23_benign_utility.py` with three conditions: `--gate none` (unprotected),
  `--gate ours --ablation none` (full gate), `--gate ours --ablation semantic-only` (A1);
  50 benign cases (25 dh + 25 ds); output under `results/phase7/e23_utility/`.
- Results (50 clean cases, call-level utility NOT end-to-end task success):

| Condition | User-tool-allowed | Clean-call block rate | p95 latency |
|---|---|---|---|
| none (unprotected) | 16.0% | 0.0% | 2457 ms |
| ours (full gate) | 12.0% | 25.0% | 2332 ms |
| semantic-only (A1) | 8.0% | 42.9% | 2561 ms |

- Interpretation: semantic-only over-blocks legitimate calls (42.9% block rate) while
  allowing fewer user tools (8.0%) — confirming semantic-only is NOT equivalent to ours.
  The contract preserves more legitimate calls (12.0% allowed vs 8.0% for semantic-only)
  with fewer clean-call blocks (25.0% vs 42.9%). This settles E31: contract wins on
  utility, ties on headline ASR. Latency p95 includes LLM call time (not gate-only),
  so comparisons across conditions are valid but absolute numbers are dominated by
  model inference.
- Limitations: small sample (50 cases, 7-8 proposed calls each); call-level utility only,
  not end-to-end task completion; benign cases derived from attack cases by stripping
  attacker content; p95 latency includes LLM inference, not gate-only overhead.
- Supervisor Q&A:
  - Q: Does the gate block legitimate user calls? A: Yes — 25.0% clean-call block rate
    for full gate, 42.9% for semantic-only. The gate trades some utility for security.
  - Q: How does semantic-only (A1) compare on benign utility? A: Worse — 8.0% allowed
    vs 12.0% for full gate, 42.9% vs 25.0% block rate. Contract preserves utility.

## E24 — Prompt-level baselines (Gap 1a)
- Status: [x] complete
- Goal: compare system-text prompt defenses vs baseline on InjecAgent attack cases.
- Setup: `--gate none` with three prompt variants added to `harness/prompts/injecagent.py`:
  **Delimiters** (wrap tool outputs in <<OBS_START/<<OBS_END>>), **InstructionalPrevention**
  (system prompt tells agent to ignore injected instructions), **Sandwich** (repeat user
  instruction after each observation). 50 cases (25 dh + 25 ds, base setting).
- Results (50 attack cases, gate=none for all):

| Prompt variant | ASR | Valid rate | Attack success (succ cases) |
|---|---|---|---|
| baseline (InjecAgent) | 6.8% | 88.0% | 3 |
| Delimiters | 4.3% | 92.0% | 2 |
| Instructional Prevention | 8.9% | 90.0% | 4 |
| Sandwich | 4.3% | 92.0% | 2 |

- Interpretation: Delimiters and Sandwich reduce ASR by ~37% (6.8% → 4.3%) and improve
  valid rate (88.0% → 92.0%). Instructional Prevention worsens ASR (8.9%) — telling the
  agent to ignore injected instructions can backfire by making it more cautious overall.
  Delimiters + Sandwich are the strongest prompt-only defenses but still far behind the
  full gate (ASR 0.7% on InjecAgent).
- Limitations: 50-case sample; single backbone (gpt-4o-mini); no gate involved (these are
  prompt-only defenses, not middleware).
- Supervisor Q&A:
  - Q: Do prompt defenses help? A: Delimiters and Sandwich reduce ASR modestly but are
    far weaker than the middleware gate. They are complementary, not substitutes.
  - Q: Which prompt baseline is best? A: Delimiters and Sandwich tie at 4.3% ASR.

## E25 — Third backbone pilot (Gap 4)
- Status: [ ] not started
- Goal: replicate ASR delta on a new model family with full ReAct participation.
- Setup: `scripts/run_injecagent_ours.py --per-split 50 --setting base --gate none|ours --model-name <new-family>`, parser stays gpt-4o-mini; `--out` under `results/phase7/e25_third_backbone/`.
- Results: per-backbone delta table (B1 ASR → ours ASR), 3 rows.
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E26 — Adaptive attacker pilots (Gap 2)
- Status: [ ] not started
- Goal: attack the gate itself, live. (a) paraphrase-delivery (ASB's 5 injection phrasings); (b) threshold-aware (S ∈ [0.75, 0.79]).
- Setup: InjecAgent pilot slice; live re-score vs τ=0.75.
- Results: ASR-under-adaptation table + honest scope sentence (static vs adaptive).
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E27 — Progent comparison (Gap 1b)
- At a glance: [x] scope-out complete, re-verified 2026-10-18 against
  [arXiv v3](https://arxiv.org/html/2504.11703v3) (2026-05-14).
- Goal: compare enforcement design without inventing a benchmark comparison.
- Setup: inspected the paper and the
  [authors' artifact](https://github.com/sunblaze-ucb/progent). The earlier
  unversioned summary is superseded by this v3 comparison.
- Results:

| Dimension | IntentGate | Progent v3 |
|---|---|---|
| Policy source | LLM parser, once per trusted request | LLM initial policy and runtime updates |
| Call check | Embeddings plus deterministic veto | Symbolic rules over tool names and arguments |
| Policy change | Frozen during the session | SMT checks narrowing, approval for expansion |
| Unmatched operation | Scored against the contract, high-risk defaults apply | No matching permission blocks the call |
| User decision | Escalate band, auto-blocked in benchmark mode | Configurable expansion approver and fallback |
| Evaluation | InjecAgent and static MCPTox | AgentDojo, ASB, and MCP integration |
| Authoring cost | No manual per-tool contracts, one parser call per session | Automatic policies, no cost measured on this repository's tools |

  Progent's update control prevents unapproved policy expansion. The old
  claim that its updater silently widens the allowlist is withdrawn.
  This source does not establish a manual-authoring disadvantage for Progent.
- Artifacts: `literature_review/papers/06-progent-shi-2025.md`,
  `literature_review/index.md`, citation `shi2025progent` in both BibTeX files.
- Limitations: no port or head-to-head run was performed. The released
  experiment commands use AgentDojo and ASB. An InjecAgent/MCPTox comparison
  needs an adapter, evaluator validation, and a specified expansion-approval
  policy. Those items are outside this bounded comparison. No mandatory
  count of 79 hand-authored policies or comparative setup-cost advantage is claimed.
- Supervisor Q&A:
  - Q: Why is Progent absent from the ASR table? A: Its released experiment
    adapters differ from this protocol. The table compares design only.
  - Q: Does IntentGate uniquely derive policies from user requests? A: No.
    Its evaluated distinction is a frozen contract and CPU score-plus-veto
    enforcement, with once-per-session parsing and the stated benchmark scope.

## E28 — Parser ablation (Upgrade B)
- Status: [ ] not started
- Goal: answer "why not just heuristics."
- Setup: InjecAgent 200-case subset, B1 + ours with LLM parser swapped for heuristic fallback.
- Results: ASR/valid-rate deltas.
- Artifacts: TBD
- Limitations: TBD
- Supervisor Q&A: TBD

## E29 — Embedding swap + τ transfer (Upgrade B)
- Status: [x] complete (offline call replay; no LLM or tool calls)
- Goal: show τ is a procedure, not a magic number.
- Setup: re-score 722 cached InjecAgent calls with pinned
  `sentence-transformers/all-mpnet-base-v2` revision
  `e8c3b32edf5434bc2275fc9bab85f82640a19130`. Seventeen request groups are split into
  11 calibration and 6 held-out groups, with base/enhanced variants kept together.
- Results: MiniLM selects τ=0.70 in both transfer directions, but held-out attacker-call pass
  rates are 39.77% and 34.86%; its frozen τ=0.75 gives 2.27% and 1.83%. MPNet selects τ=0.76
  base→enhanced and τ=0.77 enhanced→base, giving 2.27% and 0.92%; frozen τ=0.75 gives 2.27%
  and 1.83%. Held-out user-call blocking is 0% in all reported rows. Threshold selection must
  be repeated for each encoder and target distribution.
- Artifacts: `scripts/e29_embedding_transfer.py`,
  `results/phase7/e29_embedding_transfer/`, and `tests/test_phase7_offline.py`.
- Limitations: only 17 independent request groups are available. These are call-level replay
  rates and tool-name proxies, not end-to-end ASR or task completion.
- Supervisor Q&A: a stronger encoder does not remove calibration; changing score geometry
  changes the threshold selected under the same constraint.

## E30 — Conformal escalate band (Upgrade A)
- Status: [x] complete (negative practical result)
- Goal: turn heuristic [τ−δ, τ+δ] band into distribution-free guarantee.
- Setup: group all 2,013 full-gate calls by 408 trusted-request hashes, then split 204/204.
  At α=0.1, calibrate the maximum per-group `abs(S-tau)` with fixed τ=0.75.
- Results: δ=0.75 yields the full-support interval [0,1] and covers 100% of the 204 held-out
  groups and 1,101 calls. The heuristic radius 0.1 covers 43.14% of held-out groups. All 100
  deterministic sensitivity splits also cover 100%, because the interval is vacuous.
- Artifacts: `scripts/e30_conformal_calibration.py`,
  `results/phase7/e30_conformal_band/`, `src/intent_gate/eval/stats.py`, and tests.
- Limitations: score coverage is not decision correctness or an ASR bound. The system retains
  its asymmetric production interval `[tau-delta,tau)`; this diagnostic interval is not used.
- Supervisor Q&A: 100% coverage does not prove safety because the calibrated interval covers
  the entire known score support.

## E31 — Contract-vs-semantic contribution (supervisor Q5)
- At a glance: [x] corrected offline analysis. Original artifacts are
  retained, and `e31_corrected_report.json` supersedes their interpretation.
- Goal: separate independent-run differences from component effects on
  identical proposed calls and frozen contracts.
- Setup: all five frozen Phase 5 trace pairs. Independent runs are matched
  by case ID, tool name, canonical JSON arguments, and repeated occurrence.
  A separate replay compares the recorded full-gate decision with
  `S_sem >= tau` on every full-gate proposal. No model or tool is executed.
  InjecAgent tool-role proxies use the pinned case metadata. Missing local
  MCPTox metadata remains unknown. Benchmark pins are InjecAgent
  `f19c9f2c79a41046eb13c03c51a24c567a8ffa07` and the 2026-09-11 MCPTox snapshot.
- Results:

| Decision pair | Exact calls across independent runs | Same-proposal replay |
|---|---:|---:|
| Both allow | 751 | 848 |
| Both prevent execution | 633 | 805 |
| Full prevents, semantic-only allows | 22 | 28 |
| Semantic-only prevents, full allows | 306 | 332 |
| Total comparisons | 1,712 | 2,013 |

  The independent runs have 301 unmatched full-gate calls and 308 unmatched
  A1 calls. Only 1,377 exact matches also share an identical contract.
  The replay avoids that policy mismatch. It finds 240 critical vetoes,
  including 28 calls semantic-only would allow. The prior 1,614
  `veto_saves` count was incorrect because passing rules were counted twice.

  Of the 28 replay veto differences, five use designated attacker tools in
  InjecAgent and 23 have unknown MCPTox role. The 332 score-fusion relaxations
  include 22 designated user-tool calls, 14 designated attacker-tool calls,
  and 296 unknown MCPTox calls. Tool roles do not validate argument safety.
  Those 14 attacker-tool relaxations are a security tradeoff, so the old
  statement that the full gate loses nothing is withdrawn.

  Observed p95 gate-call timings remain descriptive. They exclude parser
  calls and initial contract embedding. Both full and A1 conditions use a
  parsed contract, so this analysis isolates rules and fusion, not removal
  of the contract. The raw-request ablation addresses the latter question.
- Artifacts: `scripts/e31_contract_vs_semantic.py`,
  `tests/test_e31_analysis.py`,
  `results/phase7/e31_contract_vs_semantic/e31_corrected_report.json`.
  The corrected report includes input SHA-256 hashes and per-risk counts.
- Limitations: same-proposal replay estimates call-level decisions, not
  end-to-end ASR or benign-task completion. The independent-run table can
  include different contracts, while repeated exact calls are paired in
  trace order. No unlabeled decision flip is called a false positive or
  a prevented attack. Frozen Phase 5 headline results remain unchanged.
- Supervisor Q&A:
  - Q: Where does the full gate win or lose? A: Critical vetoes prevent
    28 calls that semantic-only permits. Fusion also allows 332 calls that
    semantic-only prevents, including both user-tool and attacker-tool
    proxies. The measured tradeoff supports a narrower component claim.

## Artifact packaging
- Status: [~] implemented and locally verified; clean-container validation pending
- Goal: one-command repro (`docker build && docker run pytest -q`). Wire `scripts/run_phase5.py --check` into container entrypoint.
- Results: local tests pass, and artifact-only verification checks all 30 frozen reports plus
  SHA-256 hashes for 94 Phase 5 files. Docker Desktop did not expose its Linux engine, so the
  required image build and run could not be verified on this host.
- Artifacts: `Dockerfile`, `.dockerignore`, `requirements-repro.in`,
  `requirements-repro.txt`, `scripts/container_entrypoint.py`,
  `configs/phase5_artifact_hashes.json`, and `docs/experiments/phase7_packaging_notes.md`.

## Method formalism (writing task, no new runs)
- Status: [x] complete
- (a) τ-selection as FPR-constrained ASR minimization (Neyman–Pearson) pointing at Pareto figure.
- (b) assumption-violation table (trusted request / untrusted tool content / single-turn scope).
- (c) Anderson reference-monitor framing (2 sentences).
- Lands in Ch 3 draft + blueprint Sec 9 pointer.
- Artifacts: `docs/thesis/chapter3_method.md` and
  `docs/experiments/phase7_formalism_notes.md`.
