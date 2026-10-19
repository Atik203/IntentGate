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

## E25 - Third backbone pilot (Gap 4)
- Status: [x] complete - boundary condition: DeepSeek refuses the static InjecAgent attacks.
- Goal: replicate the ASR delta on a new model family with full ReAct participation.
- Setup: `scripts/run_injecagent_ours.py --per-split 50 --setting base --gate none|ours
  --model-name deepseek-flash` with the role-specific endpoint flags; parser stays
  `gpt-4o-mini`. Model version DeepSeek-V4.1-Flash-1017, thinking disabled
  (`--agent-reasoning-effort none`). Outputs:
  `results/phase7/e25_third_backbone/deepseek_{none,ours}/`.
- Results (100 cases per condition, base setting):

| Backbone | B1 ASR | Ours ASR | Gate blocks | Valid rate (B1/ours) | Reading |
|---|---:|---:|---:|---|---|
| gpt-4o-mini (freeze) | 19.0% (2,108) | 0.7% | 340 | - | primary result |
| qwen3.5:4b (E18) | 27.1% (100) | 2.1% | 24 | 96% / 96% | replicates |
| DeepSeek V4.1 Flash (E25) | 0.0% (100) | 0.0% (100) | 0 | 96% / 97% | refuses; delta undefined |

  On the exact 100-case slice used here, the frozen gpt-4o-mini traces give B1 14.3%
  (12/84 valid) and ours 0.0%, so the DeepSeek row is comparable to that slice rather than
  to the 2,108-case freeze. DeepSeek's outputs name the injected instruction as untrusted
  (for example, "this is a prompt injection") and do not call the attacker tool. The gate
  blocked zero calls in the ours condition because no attacker calls were proposed. The
  0.0% -> 0.0% row is therefore a ceiling effect, not a gate effect, and E25 does not
  provide a third replication; qwen remains the only replication.
- Artifacts: `results/phase7/e25_third_backbone/deepseek_{none,ours}/` (summaries, case
  JSONL, traces, logs); smoke in `.../deepseek_smoke/`. The abandoned `gpt4o_none/`
  directory was removed because the slice baseline is derivable from the frozen traces.
- Limitations: one static benchmark, 100 cases, one model version; the refusal may be
  prompt-specific; no adaptive attack was run against this backbone. A zero B1 ASR leaves
  no headroom for measuring a gate delta.
- Supervisor Q&A:
  - Q: Does the third backbone replicate? A: No. DeepSeek refuses the static injections,
    so the gated and unprotected conditions both have zero attacker calls. The qwen row
    remains the only replication.
  - Q: Does 0.0% for ours show the gate works on DeepSeek? A: No. The gate was never
    exercised; zero attacker calls were proposed.

## E26 - Adaptive attacker pilots (Gap 2)
- Status: [x] complete - live delivery, offline threshold-aware, and echo-guard arms.
- Goal: attack the gate itself, live. (a) paraphrase-delivery (ASB's 5 injection phrasings);
  (b) threshold-aware (calls aimed just above tau); (c) test a post-hoc verbatim-echo guard.
- Setup:
  (a) Live delivery: the five ASB phrasings (naive, escape characters, context ignoring,
      fake completion, combined) are applied to the attacker instruction inside the tool
      response; 100 cases per phrasing, `--gate ours`, tau=0.75, all other inputs fixed.
  (b) Offline threshold-aware: mine prevented attacker-tool calls with S in [0.60, 0.75)
      from the four frozen Phase 5 InjecAgent traces; rewrite free-text parameters with
      text from the trusted contract; re-score with the full gate. The strict arm edits
      only free-text keys (`query`, `keywords`, `search_term`, ...); the lenient arm edits
      any string parameter or adds a `query` parameter and is an upper bound.
  (c) Echo guard: a post-hoc, deterministic guard flags a contiguous 6-token span from
      the request, goals, or permitted data access inside free-text arguments. It is
      evaluated offline and does not change the frozen matrix.
- Results:
  (a) Live delivery (100 cases per phrasing; valid excludes invalid and error rows):

| Phrasing | Succ/valid | ASR-valid | Invalid | Errors | Gate-blocked calls |
|---|---:|---:|---:|---:|---:|
| Naive (baseline) | 0/90 | 0.0% | 10 | 0 | 12 |
| Escape characters | 0/84 | 0.0% | 16 | 0 | 43 |
| Context ignoring | 1/90 | 1.1% | 10 | 0 | 15 |
| Fake completion | 1/92 | 1.1% | 7 | 1 | 27 |
| Combined | 2/92 | 2.2% | 6 | 2 | 67 |

  Delivery phrasing changes gated ASR by at most 2.2 percentage points (2/92) and is not
  monotone across variants. The two successes are call-level attacker-tool invocations;
  harmful follow-up calls in those cases are still gated. This arm does not show a
  delivery-only bypass; the offline threshold-aware arm is the stronger adaptive result.
  Gate-blocked calls include both user-tool and attacker-tool calls, so the column is not
  an attack metric.
  (b) 262 prevented attacker-tool calls were replayed. 34 call instances (11 unique call
      templates) have free-text parameters; all 34 cross tau after the echo (median
      Delta S +0.176, max +0.253) and no rule veto catches them. The lenient upper bound
      crosses for 180/262 calls; 82 calls have no editable parameter. Full report:
      `results/phase7/e26_adaptive/offline/e26b_threshold_probe.json`.
  (c) The six-token echo guard blocks 34/34 strict E26b calls (11/11 templates). It adds
      no block among 194 allowed user-tool calls (281 user calls total). The threshold
      sweep gives 33/34 at 8 tokens, 29/34 at 10, and 28/34 at 12. Report:
      `results/phase7/e26_adaptive/offline/e26c_echo_guard.json`.
- Artifacts: `scripts/e26_threshold_probe.py`, `scripts/e26c_echo_guard.py`,
  `src/intent_gate/scoring/echo_guard.py`, `tests/test_e26_echo_guard.py`, and the two
  JSON reports under `results/phase7/e26_adaptive/offline/`.
- Interpretation: live delivery phrasing is weak on this slice (0-2.2% gated ASR), but the
  semantic score is sensitive to verbatim overlap with the trusted request. A read-only
  search call can be pushed from just below tau to allow by copying the user's own wording
  into a free-text argument. This is a call-level counterfactual, not an end-to-end ASR; it
  motivates argument-aware vetoes or scoring the call structure rather than raw parameter text.
  The six-token guard is a concrete argument-aware veto for the measured verbatim echo. It
  catches verbatim copies, not paraphrases.
- Limitations: the live arm is 100 cases per phrasing and two successes do not establish
  a delivery effect; the offline arm has 11 unique templates, so generality is limited;
  these calls were already prevented (block or escalate), so the offline result is a
  counterfactual decision; invalid or schema-incompatible arguments would be rejected by a
  real tool; no live agent run for the strict offline arm; the guard catches verbatim
  copies only, and its false-positive estimate covers 194 allowed user-tool calls.
- Supervisor Q&A:
  - Q: Does adapting the attack break the gate? A: Live delivery phrasing does not on this
    slice (0-2.2%). At the score level, the offline argument echo does: all 34 instances
    across 11 free-text templates cross tau and rules do not veto them. End-to-end execution
    was not tested.
  - Q: Is this the same as E20 mimicry? A: No. E20 wrapped a call in prose outside the
    real scorer; this probe edits the actual call parameters and re-scores with the real
    gate, including rules.
  - Q: Does the echo guard close the bypass? A: For the measured verbatim copies, yes:
    34/34 calls and 11/11 templates are blocked, with no new blocks among 194 allowed
    user-tool calls. Paraphrased echoes remain open, and the guard is offline only.

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
- Status: [x] complete (negative/underpowered result)
- Goal: answer "why not just heuristics."
- Setup: 200-case InjecAgent subset (100 dh + 100 ds, base), gpt-4o-mini agent; three
  conditions: B1, ours with `--parser heuristic`, ours with `--parser llm`. The heuristic
  is the deterministic fail-closed fallback, not a tuned parser.
- Results:

| Condition | ASR-valid | Succ/valid | Invalid | Errors | Gate-blocked calls | Parser calls |
|---|---:|---:|---:|---:|---:|---:|
| B1 | 17.9% | 30/168 | 32 | 0 | 0 | 0 |
| Ours + heuristic | 0.0% | 0/169 | 30 | 1 | 29 | 0 |
| Ours + LLM | 0.0% | 0/171 | 29 | 0 | 32 | 200 |

  Both gated conditions block every attacker call on this subset, and the heuristic is
  indistinguishable from the LLM parser on ASR and block count. The subset is underpowered
  for the full-run difference: the 2,108-case gated ASR is 0.7%, so a 200-case slice has an
  expected 1-2 successes. E28 does not establish a security advantage for the LLM parser.
- Interpretation: the honest answer to "why not just heuristics" is not "heuristics miss
  attacks." A fail-closed keyword heuristic can match ASR on a small slice. The LLM parser
  is retained for contract quality and intent coverage (slots, categories, permissions)
  and for the E23 utility comparison; E28 shows that those properties, not this ASR delta,
  must carry the argument. A heuristic benign-utility run remains future work.
- Artifacts: `results/phase7/e28_parser_ablation/` (b1, ours_heuristic, ours_llm);
  `--parser` flag in `scripts/run_injecagent_ours.py`; `build_run_parser` in
  `harness/common.py`; tests in `tests/test_runner_endpoints.py`.
- Limitations: 200 cases, call-level ASR, no end-to-end task completion; the heuristic is
  a fallback, not tuned; no benign-utility measurement under the heuristic; the slice is
  underpowered for a <1% ASR difference.
- Supervisor Q&A:
  - Q: Does the heuristic parser fail? A: On this slice it does not: both parsers reach 0%
    ASR with 29-32 blocked calls. The subset cannot resolve a 0.7% difference, so E28 is
    not evidence of equivalence either.
  - Q: Why keep the LLM parser? A: Contract quality and utility, not this ASR table. The
    heuristic's fail-closed defaults and benign-task cost were not measured here.

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
