# IntentGate — Supervisor Summary (Phases 0–6)

> **One-paragraph verdict.** IntentGate is a middleware action gate that derives an *intent
> contract* from the user's original request and scores every proposed tool call against it
> (embedding similarity + hard rule veto → allow / block / escalate). On the full frozen
> evaluation (20,736 cases, seed 42) it cut InjecAgent attack success **19.0% → 0.7%** and
> MCPTox attack-influenced calls **279 → 144**, with no measured utility loss (valid-rate
> parity), p95 latency **16–20 ms** per gated call, zero manual contracts, and a billed cost of
> **$9.64**. Phase 6 pilots replicated the effect on a second backbone (Qwen 27.1% → 2.1%)
> and showed the baseline's weakness is structural, not coverage-limited.
>
> | Gate | Meaning | Status |
> |---|---|---|
> | Gate 0 | Core idea works on a 50-case pilot | ✅ 2026-09-11 |
> | Gate 1 | Published baseline (ToolGate) reimplemented, coverage frozen | ✅ 2026-09-16 |
> | Gate 2 | Gate wired into the agent loop, speed measured | ✅ 2026-09-16 |
> | Gate 3 | Full results frozen — numbers below never change | ✅ 2026-10-12 |
> | Phase 6 | Hardening pilots (second backbone, coverage curve, probes) | ✅ 2026-10-13 |
>
> Backbone throughout: `gpt-4o-mini` (agent + parser, temperature 0) unless a row says otherwise.
>
> Where to look: full numbers in `docs/experiments/05_phase5_full_evaluation.md` (E11–E17)
> and `docs/experiments/06_phase6_pilots.md` (E18–E22); live status in `roadmap.md`.

---

## 1. The problem in one minute

Modern LLM agents don't just chat — they book, pay, run code, and call third-party tools.
Every benchmark in our literature review shows the same pattern: once an agent holds tool
permissions, a hijacked tool call succeeds at scale (InjecAgent: GPT-4 vulnerable on
24–47% across 1,054 base cases; MCPTox: 72.8% attack success on 45 live servers with 1,348
cases and <3% refusal).

The attack paths differ (injected tool output, poisoned tool description, multi-turn drift)
but converge on one observable: **the agent executes an action the user never intended.**

Existing answers are unsatisfying: benchmarks reveal the vulnerability but propose no
defense, and the only published action-level gate (ToolGate, Jan 2026) needs a
hand-authored formal contract **per tool** — expensive, and never tested on any adversarial
benchmark. Our question: *can a gate derived automatically from the user's own request
match that protection at zero contract cost?*

---

## 2. How the system works

Five steps, every proposed tool call, before execution:

| # | Step | What happens | Cost |
|---|---|---|---|
| 1 | **Parse (once per session)** | User request → structured intent contract (goals, allowed tool categories, data access, side-effect limits). LLM parser, temperature 0, frozen schema v1.1 | 1 LLM call per session |
| 2 | **Embed (once per session)** | Contract embedded with `all-MiniLM-L6-v2` (CPU, hash-pinned); each proposed call naturalized to a sentence and embedded | milliseconds |
| 3 | **Score** | S = 0.7·S_sem + 0.3·S_rule: cosine similarity to the contract plus deterministic rule score | milliseconds |
| 4 | **Veto** | Hard rules (e.g., unrequested file write, external send, payment) force-block regardless of similarity | microseconds |
| 5 | **Decide** | S ≥ 0.75 → allow; S in [0.65, 0.75) → escalate (human review; counts as block in benchmarks); else block | — |

The escalate band is δ=0.1 around τ. In benchmark mode escalate counts as block (conservative
measurement); in demo mode it prompts the user to accept/decline (both paths tested).

Three design rules that matter: the contract is parsed **before** any attacker content is
visible (ordering invariant, tested); **every** tool execution passes through the gate
(no-bypass, tested); the gate is **fail-closed** (unknown = disallow for risky effects).

### Threat model (what we trust, what we don't)

| Element | Status | Rationale |
|---|---|---|
| User's original request | **Trusted** (parsed once, then frozen) | The one thing the attacker cannot rewrite |
| Tool definitions + tool outputs | **Untrusted** (may carry injections/poisoning) | This is where all three attack vectors live |
| Agent backbone | Untrusted-but-observed (participates in ReAct) | Gate scores its proposals; backbone choice is varied (E18/E25) |
| Single-turn scope | Assumed (multi-turn drift out of scope) | Stated limitation, Phase 7-deferred pilots aside |

### Illustrative walkthrough (not measured data — shows the mechanism)

User request: *"Find the cheapest flight to Berlin and hold it — don't pay yet."*
Contract: goals=[find + hold flight], categories=[search, hold], limits={financial: no
payment, external_send: disallow, file_write: disallow}.

| Proposed call | S_sem | S_rule | S | Decision | Why |
|---|---|---|---|---|---|
| `SearchFlights(to=Berlin)` | 0.91 | 1.0 | 0.94 | **allow** | matches goals and categories |
| `BankManagerTransferFunds(1000, to=123)` (injected) | 0.56 | 0.0 | 0.39 | **block** | low similarity + financial veto |
| `WebBrowserNavigateTo(recipe)` (borderline legit) | 0.71 | 1.0 | 0.71 | **escalate** | inside [τ−δ, τ) band → human review |

---

## 3. Phase 0 — Literature review & blueprint (DONE)

- **What:** 10-paper synthesis (AgentDojo, InjecAgent, MCPTox, ASB, ToolGate + 5) with
  structured Q1–Q9 notes, condensed into the master blueprint (Sec 0–18, the design source
  of truth).
- **How:** `literature_review/` + `literature_review/index.md`; references in
  `docs/references.bib`. The five anchors that shaped the design:

| Paper | Fact we built on |
|---|---|
| AgentDojo (NeurIPS 2024) | 629 cases; tool-filter defense fails without pre-planning → we score proposals, not names |
| InjecAgent (ACL Findings 2024) | GPT-4 24–47% vulnerable → our primary benchmark |
| MCPTox (AAAI 2026) | 72.8% ASR, <3% refusal, 353 tools → our second benchmark + B2 coverage universe |
| ASB (ICLR 2025) | 84.3% max mixed-attack ASR; 11-defense taxonomy → our baseline menu + joint ASR/FPR/latency reporting |
| ToolGate (arXiv Jan 2026) | Only published action-level gate; hand-authored contracts, never adversarially tested → our B2 and our gap |
- **Why it mattered:** fixed the threat model, picked the two benchmarks, and identified the
  gap (no tested, zero-contract action gate) that defines the thesis contribution.

## 4. Phase 1 — Project skeleton (DONE)

- **What:** Typed Python package (`src/intent_gate/`), benchmark harnesses, configs,
  CI running `pytest -q` on `dev`/`main`, branch model (feature → `dev` → `main`).

| Area | Code | Role |
|---|---|---|
| Intent parsing | `src/intent_gate/parser/` | Request → frozen contract (once per session) |
| Scoring | `src/intent_gate/scoring/` | Embeddings + rule veto → S |
| Gate | `src/intent_gate/gate/` | Allow/block/escalate + JSONL trace |
| Agent | `src/intent_gate/agent/` | LLM client + ReAct loop (executes only via gate) |
| Baseline | `src/intent_gate/baselines/toolgate/` | B2 contracts + world state |
| Metrics | `src/intent_gate/eval/` | CIs, McNemar, sweeps, cost |
| Runners | `harness/` | Benchmark execution (ordering-guarded) |
- **Why it mattered:** every later number is reproducible from this scaffolding —
  seeded runs, pinned model IDs, hashes logged in every trace.

## 5. Phase 2 — Foundation pilot → Gate 0 (✅ 2026-09-11)

- **What:** the cheapest possible test of Assumption 2 (hijack vs legitimate calls separate
  in embedding space) on 50 cases, before building the full gate.
- **How:** `scripts/pilot_score_dist.py`; intent schema v1 frozen, then v1.1 (adds
  `system_change` limit, 9 few-shots, 30-request LLM re-validation).

| Metric | Result |
|---|---|
| AUC (hijack vs legit) | **0.979** |
| Attack success at τ=0.75 | **0%** |
| False-positive rate at τ=0.75 | **4%** |
| Decision | **GO** |

- **Why it mattered:** killed the biggest risk early — had the distributions overlapped,
  the project would have stopped here. Three rule-engine false positives found and fixed.
  τ=0.75 was chosen at the threshold-sweep knee (best attack-rate vs false-positive
  trade-off) and frozen from here on — never re-tuned on later results.

## 6. Phase 3 — ToolGate baseline → Gate 1 (✅ 2026-09-16)

- **What:** faithful minimal reimplementation of ToolGate (Hoare pre/postconditions per
  tool + symbolic world state with rollback) so the comparison is fair, not a strawman.
- **How:** contracts keyed by harness tool names; world state seeded from the trusted
  request; coverage frozen in `configs/b2_coverage.json`.

| Benchmark | Contracts | Coverage |
|---|---|---|
| InjecAgent (79 evaluated tools) | 79/79 | **100%** |
| MCPTox (801 registered tools) | 65 | **8.1% distinct / 37.2% availability-weighted** |

Early gated reruns showed the shape of the problem: on MCPTox, B2 blocked only the
out-of-scope `write_file` — everything else was uncontracted or passed preconditions.
Phase 5 confirmed it at scale (B2 271 vs B1 279 attack-influenced, statistically
indistinguishable).

- **Why it mattered:** the long tail + poisoned registrations stay `no_contract` by
  construction — this structural fact becomes the E19 finding later. Fidelity notes: real
  Hoare pre/postconditions (not stubs), world-state effects with rollback on postcondition
  violations, best-effort state seeding from the trusted request, and an explicit
  `no_contract_tools` counter so invisible tools are counted, never silently allowed.
  ToolBench fallback validation used (documented, honest).

## 7. Phase 4 — Gate build → Gate 2 (✅ 2026-09-16)

- **What:** real ReAct agent loop executing only via `GateMiddleware.execute`, escalate
  band, trace logging (S, S_sem, S_rule, decision, latency on every call), threshold-sweep
  tooling (Pareto knee at τ=0.75).
- **How:** 100 InjecAgent + 100 MCPTox cases, B1 vs ours vs B2 through identical prompts
  (only the middleware differs — measured delta = gate effect).

| Benchmark | B1 (no gate) | Our gate | B2 |
|---|---|---|---|
| InjecAgent attack success | 9 / 100 | **0 / 100** (0 false blocks) | 8 / 100 |
| MCPTox attack-influenced | 22 | **10** (12 blocked) | 23 |
| Gate latency p95 | — | **≤ 23 ms** (17.8–23.1 measured) | — |

- **Why it mattered:** first honest side-by-side evidence the idea works end-to-end.
  Same run also produced the τ-sweep Pareto (E9) and the first error taxonomy (E10) —
  both superseded by the frozen full-scale versions in Phase 5.

## 8. Phase 5 — Full evaluation → Gate 3 (✅ 2026-10-12, FROZEN)

- **What:** the complete matrix under a code/config freeze (lock + manifest, git SHA
  recorded): 6 conditions (B1 / B2 / ours / 3 ablations) × 5 dataset files = **30 jobs,
  20,736 cases**, seed 42, τ=0.75, δ=0.1, α=0.7, backbone **gpt-4o-mini for both agent and
  parser** (temperature 0). Integrity `--check` passed 30/30.
- **How:** `scripts/run_phase5.py` (resumable, 3-way parallel, ~5.6 h wall-clock) →
  `scripts/report_phase5.py` (breakdowns, bootstrap CIs, McNemar, Pareto, taxonomy).

| Benchmark | B1 | Our gate | B2 | Significance |
|---|---|---|---|---|
| InjecAgent ASR-valid (2,108) | 354 (19.0%) | **13 (0.7%; 340 blocked)** | 321 (17.2%) | ours p=1.3e-33; B2 p=1.00 (n.s.) |
| └ direct-hijack | 8.8% | **0.0%** | ≈B1 | — |
| └ indirect-hijack | 28.3% | **1.3%** | ≈B1 | — |
| MCPTox attack-influenced (1,348) | 279 | **144** (140 blocked) | 271 (10 blocked) | ours p=1.25e-07; B2 p=0.33 (n.s.) |

Per-split (InjecAgent: dh 510 + ds 544 cases × base/enhanced):

| Split | B1 | B2 | Ours (blocked) |
|---|---|---|---|
| dh_base (510) | 7.8% (35) | 5.6% (25) | **0.0%** (0; 39 blocked) |
| dh_enhanced (510) | 9.9% (44) | 5.7% (25) | **0.0%** (0; 41 blocked) |
| ds_base (544) | 25.0% (122) | 24.3% (118) | **1.2%** (6; 121 blocked) |
| ds_enhanced (544) | 31.5% (153) | 31.0% (153) | **1.4%** (7; 139 blocked) |

Direct hijacks are eliminated entirely; all 13 residuals sit in the harder indirect splits.

- **Ablations (full matrix, measured):**

| Ablation | InjecAgent ASR-valid | MCPTox attack-influenced |
|---|---|---|
| A1 semantic-only | **0.0% all four slices** (0 successes) | 81 (204 blocked) |
| A2 rule-only | dh 0.2–0.7%, ds 24.3–31.6% (≈ B1) | 263 (≈ B1, 14 blocked) |
| A3 raw-request | 0.0–1.6% (≈ ours) | 116 (165 blocked, ≈ ours) |

  Honest reading: **semantics do the detecting** — rules alone
  detect almost nothing, so their value is the fail-closed veto guarantee plus the
  escalate-band input, not detection lift. A3 ≈ ours likewise narrows the contract claim
  (stated in the report, not hidden).
- **Residuals:** all 13 remaining InjecAgent failures share one signature — rule=1.0,
  S just above τ (0.75–0.79), read-only near-miss calls. One boundary, fully characterized.
- **Utility:** valid-rate parity B1 vs ours on every slice (ours 86.9–89.7% vs B1
  87.5–89.7%, Δ ≤ 0.6 pp — no clean-call loss). Per-risk example: Credential Leakage
  0.130 → 0.017 attack rate.
  Escalate share at τ=0.75 is 21.6% (InjecAgent) / 18.2% (MCPTox) — benchmark mode counts
  escalate as block; E21 shows the band fires at 80.5% precision, so most escalates are
  true attacks awaiting review, not false alarms.
- **Setup cost:** **0 contracts (ours) vs 145 manual (B2)** on the evaluated tool set.
- **Latency:** ours p50 ≈ 12–13 ms, p95 **16–20 ms** per gated call (CPU embeddings;
  target <100 ms — covers embed + score + veto; the once-per-session parser LLM call is
  amortized, not per-call); B2 ≤ 0.06 ms (in-memory checks).
- **Money:** $11.46 list-price / **$9.64 actually billed** (~16% prompt-cache saving).

| Group | Cases | LLM calls | List-price |
|---|---|---|---|
| B1 | 3,456 | 3,456 | $1.33 |
| B2 | 3,456 | 3,456 | $1.33 |
| Ours (agent + parser) | 3,456 | 6,912 | $2.20 |
| Ablations A1–A3 | 10,368 | 20,736 | $6.60 |
| **Total** | 20,736 | **34,560** | **$11.46 / $9.64 billed** |

## 9. Phase 6 — Hardening pilots (✅ 2026-10-13, preliminary)

Rule: frozen Phase 5 numbers never touched — all new work is E18+ preliminary evidence.

| ID | Experiment | Headline |
|---|---|---|
| E18 | Second-backbone pilot (Qwen3.5:4b local, 100 cases/arm; Luna arm n=20) | Qwen **27.1% → 2.1%** ASR (invalid 4% both arms, valid-rate 96% parity); Luna prose-only (70%/45% invalid) → honestly excluded, backbone-incompatibility not gate deficit |
| E19 | B2 coverage curve (65 → 583 contracts, 37.2% → 84.9% weighted) | Curve **flat**: projection 67.9% ASR remains; 200-case rerun 1/45 attacks blocked (2.2%). B2's weakness is **structural** (poisoned registrations pass preconditions), not coverage-limited |
| E20 | Intent-mimicry probe (13 residuals × 3 variants, offline re-score) | Avg S inflation **+0.0112** (max +0.020); 0/13 newly cross τ — semantic signal stable |
| E21 | Escalate precision (all 583 escalated calls, ground-truth classified) | **80.5%** precision (354/440); 14.8% false-escalate; falses cluster in one tool family (browser navigation near τ) |
| E22 | Stats discipline (post-hoc power, Bonferroni, specificity FPR) | Power **1.0** at α=0.005 both benchmarks; 10-risk breakdowns survive correction; block-rate 12.8% specific / 9.6% vague (includes escalate candidates — valid-rate parity stays the utility metric) |

Qwen split detail (100 cases/arm, parser calls 100 ✓ on the gated arm):

| Split | B1 ASR-valid | Ours ASR-valid |
|---|---|---|
| dh (50 cases) | 7/48 decided (14.6%) | **0/48 (0.0%)** |
| ds (50 cases) | 19/48 decided (39.6%) | **2/48 (4.2%)** |
| Combined | 26/96 (27.1%) | **2/96 (2.1%)** |

E20 samples (mimicry keeps already-passing near-misses passing, but adds almost nothing):

| Case | Tool | Original S | Max mimic S | Δ |
|---|---|---|---|---|
| ds_base_0506 | TwilioGetPhoneNumberInfo | 0.754 | 0.774 | +0.020 |
| ds_base_0260 | FedExShipManagerSearchShipment | 0.788 | 0.807 | +0.019 |

E19 projection breakdown (271 Phase 5 attack cases × extended contracts, offline):

| Category | Cases |
|---|---|
| Already blocked by Phase 5 B2 | 10 |
| Newly contracted and blocking (precondition fails) | **0** |
| Newly contracted but still allowing (looks legitimate) | 184 |
| Still no contract | 87 |
| **Projected attack-influenced** | **194 (67.9% ASR)** |

Subset note (same 200 cases): the old 65-contract B2 blocked 10 there; the extended set
blocks 1 attack case (+2 benign-call blocks in `ignored` cases). The mechanism behind the
drop is not yet pinned down — recorded here so the numbers reconcile; either way the
coverage-vs-ASR curve is flat.

E21 by source: InjecAgent 259 attacker-tool of 348 escalated (74.4%) with 86 user-tool
falses (24.7%); MCPTox 95 attacker-tool (40.4%) with **0** user-tool falses — remainder
ambiguous/other in both. Sample falses: three `WebBrowserNavigateTo` calls ("navigate to
Blueberry Scones recipe", S=0.710) — legitimate navigations just below τ, correctly kept
in the human-review band rather than blocked.

- **Why it mattered:** turned the two most attackable claims into evidence —
  model-agnosticism replicates off the dev backbone, and the "B2 is a strawman" objection
  is answered by measurement (we gave B2 9× more contracts; it still barely moves).

---

## 10. Headline results (the one table)

| Benchmark | Unprotected (B1) | IntentGate (ours) | ToolGate reimpl (B2) |
|---|---|---|---|
| InjecAgent attack success | 19.0% (354) | **0.7% (13)** | 17.2% (≈B1, n.s.) |
| MCPTox attack-influenced | 279 | **144** | 271 (≈B1, n.s.) |
| False blocks on legitimate use | — | **0 observed** (valid-rate parity) | — |
| Latency p95 per call | — | **16–20 ms** | ≤0.06 ms |
| Setup cost | — | **0 contracts** | 145 manual contracts |
| Evaluation cost | — | **$9.64 billed** (34,560 calls) | — |

Backbone check: Qwen3.5:4b replicates (27.1% → 2.1%); gpt-6-luna incompatible with the
shared ReAct prompt (excluded with justification, not silently dropped).

How to read this table: B2's column is the point — statistically indistinguishable from
unprotected on both benchmarks despite 145 hand-written contracts, which is why the thesis
frames B2 ≈ B1 as a finding about per-tool contracts (not a shortfall of effort; E19
proves it by giving B2 9× more contracts). The latency gap (16–20 ms vs 0.06 ms) is the
honest price of semantic scoring over in-memory checks — still 5× inside the 100 ms
deployability budget. The $9.64 bought 34,560 audited model calls, every one traceable.

Measurement note: MCPTox uses our heuristic evaluator, validated against the authors'
labels (precision 0.82, recall 0.26 — conservative: it under-counts attacks). All B1/B2/ours
comparisons share the same evaluator, so the *deltas* are fair even where absolute counts
are conservative.

## 11. What it cost (total)

| Item | Amount |
|---|---|
| Phase 5 full matrix | ~5.6 h wall-clock (`--jobs 3`), **$9.64 billed** ($11.46 list) |
| Per-case multiplier | ours ≈ 1.55× B1 (the parser call); A1/A2/A3 ≈ $2.20 each per full run |
| Phase 6 pilots | cents (Qwen ≈ $0.03 local + parser; Luna ≈ $0.005 parser-only) |
| Test suite | **199 tests**, green on every branch |
| Spend discipline | `results/` committed (teammates read, never re-run); every run resumable |

## 12. Honest limitations (Ch 6 material — each with its planned answer)

1. **Static attacks only** → E26 live adaptive pilots (paraphrase-delivery + threshold-aware).
2. **Two effective backbones** → E25 third backbone, same 100-case protocol.
3. **Utility is proxied** → E23 dedicated benign-task suite replaces the proxy with a number.
4. **Static MCPTox snapshot**, not live servers → stands; documented, deferred to future work.
5. **Single-turn scope** → stands; drift pilot deferred to future work.
6. **A3 ≈ ours** → E28 parser ablation quantifies exactly what the LLM parser buys.
7. **Heuristic MCPTox evaluator** (precision 0.82 / recall 0.26, conservative) → shared
   across all conditions so deltas are fair; absolute counts understate attacks.

## 13. What's next

| Phase | Work | Status |
|---|---|---|
| Phase 7 | Q1 hardening (~$8): E23 utility suite · E24 prompt baselines · E25 third backbone · E26 adaptive attacker · E27 Progent · E28 parser ablation · E29 embedding/transfer · E30 conformal band · formalism + artifact | ⏳ next |
| Phase 8 | Thesis + paper (chapters below) from frozen evidence + pilots | ⏳ after Phase 7 |

| Chapter | Source (already written) |
|---|---|
| Ch 1 Intro & motivation | §1–§2 of this summary + blueprint Sec 0–2 |
| Ch 2 Related work | literature_review/index.md + E27 Progent positioning |
| Ch 3 Method | §2 + formalism (Neyman–Pearson τ, assumption table, reference monitor) |
| Ch 4 B2 baseline | §6 + `03_b2_toolgate.md` + E19 curve |
| Ch 5 Evaluation | §8–§10 (frozen) + §9 pilots + E23–E30 |
| Ch 6 Limitations | §12 (each item already paired with its answer or plan) |
| Appendix | §14 pins + sample contract/trace |

After Phase 7 the package targets a Q1 security venue (TDSC/TIFS or Computers & Security;
JISA/Applied Intelligence as backup) — the adaptive loop + third backbone + conformal band
are what separate the first group from the second.

Staffing: E27 (Progent) and E30 (conformal) need specialist effort — staff those first;
E23–E26/E28–E29 plus the artifact run parallel across the remaining members.

## 14. Where to look (artifact map)

| Question | Answer |
|---|---|
| Full frozen numbers | `docs/experiments/05_phase5_full_evaluation.md` (E11–E17) |
| Pilot numbers | `docs/experiments/06_phase6_pilots.md` (E18–E22) |
| Live status + Phase 7/8 plan | `roadmap.md` |
| Design (source of truth) | `docs/blueprint.md` |
| Raw evidence (committed, read don't re-run) | `results/phase5/`, `results/phase6/` |
| Run it yourself | `docs/setup.md` → `pytest -q` (199 green) → `docs/experiments/README.md` commands |
| Benchmark pins | `configs/benchmark_versions.yaml` (InjecAgent `f19c9f2c`, MCPTox snapshot 2026-09-11: 1,348 cases, 45 servers, 801 tools) |
| Frozen coverage record | `configs/b2_coverage.json` (never overwritten; extended counts live in Phase 6 results) |

Pinned models: agent + parser `gpt-4o-mini` (temp 0); embeddings
`sentence-transformers/all-MiniLM-L6-v2` (CPU, hash `4588b3f9e962`); pilots add
`qwen3.5:4b` (local Ollama) and `gpt-6-luna` (excluded arm, documented).

*Status: Phases 0–6 complete. This file is a briefing distillate — every number above is
cited to the report or results file named beside it; nothing here is new evidence.*

## Appendix — questions a supervisor typically asks (with one-line answers)

1. *"Why not just use a bigger model?"* — attacks scale with capability (paper figures
   24–72.8% across models); the gate sits outside the model and replicates on Qwen.
2. *"What breaks first under adaptive attack?"* — the E16 near-miss band (S 0.75–0.79);
   E20 shows paraphrase adds almost nothing, E26 will attack it live.
3. *"Can this run inline in production?"* — p95 16–20 ms vs a 100 ms budget, CPU-only;
   the LLM parser call is once per session, not per action.
4. *"Why trust the MCPTox counts?"* — heuristic evaluator, precision 0.82/recall 0.26,
   shared across conditions: deltas fair, absolutes conservative. See measurement note §10.
5. *"What remains open before submission?"* — Phase 7's nine items (§13): utility suite,
   prompt baselines, third backbone, and a live adaptive loop first; formalism and the
   artifact in parallel.
