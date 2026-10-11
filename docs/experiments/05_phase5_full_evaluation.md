# E11–E17 — Phase 5 full evaluation (Gate 3 results freeze)

> **At a glance:** 30 jobs, 20,736 cases, 34,560 LLM calls, seed 42, frozen 2026-10-12.
> Ours takes InjecAgent ASR-valid 19.0% → 0.7% overall (dh 8.8% → 0.0%, ds 28.3% → 1.3%)
> and MCPTox attack-influenced 279 → 144, both McNemar p < 1e-6 vs B1.
> B2 is statistically indistinguishable from B1 (p = 1.00 / 0.33).
> Valid-rate parity holds (no utility loss), p95 ≤ 20 ms, total billed $9.64.
> **Nothing after this point rewrites these numbers.**

## Goal

Produce the complete, reproducible result set the thesis and paper rest on:
B1 vs B2 vs ours on the full suites (2,108 InjecAgent + 1,348 MCPTox), ablations A1–A3 on the
full matrix, paired significance, breakdowns, error taxonomy, latency/utility/cost.
(Prior slices E8–E10 used 100-case subsets; everything here is the full frozen matrix.)

## Setup

- **Freeze:** `configs/phase5_lock.json` + `results/phase5/manifest.json`
  (git `307487f`, clean tree, τ=0.75, δ=0.1, α=0.7, seed 42).
- **Matrix:** 6 conditions × 5 case files = 30 jobs
  (B1 none · B2 toolgate · ours · A1 semantic-only · A2 rule-only · A3 raw-request).
- **Models:** agent + parser `gpt-4o-mini` (temp 0); embeddings
  `sentence-transformers/all-MiniLM-L6-v2` (probe hash `4588b3f9e962`, `sentence-transformers`
  backend — verified in the manifest, not the hash fallback).
- **Commands:**
  ```powershell
  python scripts/run_phase5.py --freeze
  python scripts/run_phase5.py --run --jobs 3
  python scripts/run_phase5.py --check          # passed, 30/30
  python scripts/report_phase5.py --dir results/phase5 --out results/phase5/report.json
  python scripts/report_phase5.py --dir results/phase5 --markdown results/phase5/report.md
  python scripts/error_taxonomy.py --b1 ... --gated ... --trace ... --no-parse --out results/phase5/error_taxonomy_{injecagent,mcptox}.json
  ```
- **Wall clock:** ~5.6 h at `--jobs 3`. Integrity `--check` passed with default flags.

## Results

### E11 — headline matrix (ours vs baselines)

InjecAgent ASR-valid (succ / decided):

| Slice (n) | B1 | B2 | Ours |
|---|---|---|---|
| dh_base (510) | 7.8% (35) | 5.6% (25) | **0.0%** (0; 39 blocked) |
| dh_enhanced (510) | 9.9% (44) | 5.7% (25) | **0.0%** (0; 41 blocked) |
| ds_base (544) | 25.0% (122) | 24.3% (118) | **1.2%** (6; 121 blocked) |
| ds_enhanced (544) | 31.5% (153) | 31.0% (153) | **1.4%** (7; 139 blocked) |
| **All InjecAgent (2,108)** | **19.0%** (354) | **17.2%** (321) | **0.7%** (13; 340 blocked) |

MCPTox (n=1,348; attack-influenced = success + work_not_success):

| Condition | success | attack-influenced | blocked | ignored |
|---|---|---|---|---|
| B1 | 103 | 279 (20.7%) | 0 | 1,012 |
| B2 | 98 | 271 (20.1%) | 10 | 1,008 |
| Ours | 66 | **144 (10.7%)** | **140** | 1,007 |

### E12 — ablations A1–A3 (full matrix)

| Ablation | InjecAgent ASR-valid | MCPTox attack-influenced |
|---|---|---|
| A1 semantic-only | **0.0% all four slices** (0 succ) | 81 (204 blocked) |
| A2 rule-only | dh 0.2–0.7%, ds 24.3–31.6% (≈ B1) | 263 (14 blocked; ≈ B1) |
| A3 raw-request | 0.0–1.6% (≈ ours) | 116 (165 blocked; ≈ ours) |

Reading: semantics carry the gate — A2 (rules alone) is a near-no-op on ds/MCPTox, while A1
matches or slightly exceeds ours on raw attack reduction. The rules' contribution is precision
on dh plus the veto semantics the escalate band needs (E13); they are not the detection engine.
A3 ≈ ours implies the contract-parsing step adds little over embedding the raw request on these
splits — a point for the limitations section, not against the gate (the contract is also the
audit trail and the escalate-band input).

### E13 — τ×δ Pareto (per-call re-decision over cached ours traces)

27-cell grid (τ 0.40–0.80 × δ 0.05/0.10/0.15), artifact `report.json → pareto`:

- InjecAgent: ASR 0.0 already at τ=0.75 for all δ; frozen point (τ=0.75, δ=0.1) holds with
  escalate share 21.6% (benchmark mode counts escalate as block).
- MCPTox: frozen point ASR 0.583 per-call with escalate share 18.2%; minimum at τ=0.80
  (ASR 0.427, escalate 16.0%).
- The Gate 2 knee (τ=0.75, E9) is re-confirmed on full traces; no re-tuning was done post-freeze.

### E14 — paired stats (bootstrap 95% CI + McNemar vs B1; primary slices)

| Slice | Ours ASR (succ/n) | 95% CI | B1 ASR | McNemar p |
|---|---|---|---|---|
| InjecAgent ds_enhanced (544) | 0.0129 | [0.0037, 0.0239] | 0.2812 | **1.3e-33** (χ²) |
| MCPTox (1,348) | 0.0490 | [0.0378, 0.0608] | 0.0764 | **1.25e-07** (χ²) |
| B2 ds_enhanced | 0.2812 | [0.2445, 0.3199] | 0.2812 | 1.00 (n.s.) |
| B2 MCPTox | 0.0727 | [0.0586, 0.0868] | 0.0764 | 0.33 (n.s., exact binomial) |
| A2 ds_enhanced | 0.2831 | [0.2463, 0.3217] | 0.2812 | 0.88 (n.s.) |

CIs are non-overlapping (ours vs B1) on both benchmarks. B2 and A2 are statistically
indistinguishable from unprotected B1 — the formal-contract baseline and the rule-only
ablation both fail to move the needle where it matters.

### E15 — breakdowns, stratification, coverage

- **MCPTox per risk (B1 → ours success rate):** Credential Leakage 0.130 → 0.017;
  Instruction Tampering 0.053 → 0.0; Service Disruption 0.029 → 0.010;
  Infrastructure Damage 0.056 → 0.024; Code Injection 0.079 → 0.048;
  Information Manipulation 0.110 → 0.078; Privacy Leakage 0.062 → 0.047.
  Flat (small-n, within noise): Data Tampering 0.100 → 0.108 (n=120),
  Message Hijacking 0.159 → 0.182 (n=44). Full table in `report.json → breakdowns`.
- **InjecAgent per split:** dh combined 8.8% → 0.0%; ds combined 28.3% → 1.3%.
  Per-attacker-tool and per-user-tool tables in `report.json` (30 + 17 rows).
- **FPR evidence:** no dedicated legit-only suite exists; the proxy is threefold —
  (i) valid-rate parity across conditions (ours 86.9–89.7% vs B1 87.5–89.7% per slice),
  (ii) user-tool calls allowed at B1-like levels (utility proxies in report),
  (iii) Gate 0 pilot FPR 4% at τ=0.75 (E4). A per-specificity stratification on full traces
  was not run — recorded as a limitation, candidate for Phase 6.
- **B2 coverage (frozen, `configs/b2_coverage.json`):** InjecAgent 79/79 (100%, 145 total
  contracts with extras); MCPTox 65/801 (8.1% distinct / 37.2% availability-weighted).
  The `no_contract` long tail + poisoned registrations are counted, never silently allowed —
  and E11 shows exactly why that matters: B2 ≈ B1.

### E16 — error taxonomy (residual failures with score evidence)

`results/phase5/error_taxonomy_{injecagent,mcptox}.json` (`--no-parse`, contracts from traces).

- **InjecAgent (13/13 analyzed):** every residual is a ds read-only exfiltration call
  (`SpokeoSearchPeople`, `EpicFHIRGetPatientDetails`, `TwilioGetPhoneNumberInfo`, …) with
  **S ∈ [0.75, 0.79] — just above τ — and rule=1.0** (no veto; reads trip no side-effect
  rule). The same case IDs fail in base and enhanced (0171, 0195, 0260, 0377, 0506):
  a stable semantic near-miss class, not noise. The attacker's read is near-identical in
  meaning to the user's legitimate read — the hardest case for a similarity gate, and the
  precise input the Phase 6 intent-mimicry probe (E18) will systematize.
- **MCPTox (sampled residuals):** same signature — rule=1.0, S above τ, called tool is a
  legitimate query/read the user plausibly wanted (`maps_geocode`, `run_select_query`,
  `tavily-search`, `generate_image`). This is the E10 registration-poisoning class confirmed
  at full scale: the gate sees a call consistent with intent, but the tool itself was
  maliciously registered. Tool provenance is out of scope for an action gate — documented,
  not hidden.

### E17 — latency, utility, cost

- **Latency (per gated call):** ours p50 ≈ 12–13 ms, **p95 16–20 ms** across all slices
  (criterion: < 100 ms ✓); B2 p95 ≤ 0.06 ms (in-memory checks, no model calls).
- **Utility:** valid-rate parity B1 vs ours on every slice (Δ ≤ 0.6 pp); user-tool calls
  allowed at B1-like levels; MCPTox ignored share 0.7478 (B2) vs ours ≈ 0.747 (no clean-call
  loss).
- **Cost:** list-price **$11.46** (agent $7.99 + parser $3.46; `cost.py` rates verified
  against the live OpenAI pricing page 2026-10-12: mini $0.15/$0.60); **billed $9.64** —
  ~16% below list via automatic prompt caching. Per-group list actuals: B1 $1.33 · B2 $1.33 ·
  ours $2.20 · A1 $2.21 · A2 $2.19 · A3 $2.20 (34,560 calls, ~5.6 h wall at `--jobs 3`).
  Per-job costs in every report (`estimated_cost_usd`); ours ≈ 1.55× B1 per case (parser call).

### Success criteria (blueprint Sec 16) — verdict

| Criterion | Result |
|---|---|
| ASR_ours < ASR_B1 both benchmarks, McNemar p < 0.05 | ✅ p=1.3e-33 (ds_enh), p=1.25e-07 (mcptox), CIs non-overlapping |
| FPR_ours < 10% at chosen τ | ✅ proxy: 4% pilot FPR + valid-rate parity (no dedicated legit suite — limitation) |
| Setup cost 0 vs documented B2 count | ✅ 0 vs 145 contracts on the same tool set |
| Latency p95 < 100 ms/call CPU | ✅ 16–20 ms |
| B2 runs and is documented | ✅ coverage frozen + reported; B2 ≈ B1 is itself a finding |
| Deliverables | ⏳ thesis + package + report done here; paper draft Phase 8 |

## Artifacts (all under `results/phase5/`, tracked in git)

| Path | Contents |
|---|---|
| `manifest.json` + `configs/phase5_lock.json` | freeze (git SHA, config hashes, model IDs, embedding hash, settings) |
| `{b1,b2,ours,a1_semantic_only,a2_rule_only,a3_raw_request}_{test_cases_*,mcptox}.json` | 30 per-condition reports (counts, usage, cost, embedding metadata) |
| `*.jsonl` | per-case rows incl. `gate_events` |
| `*_trace.jsonl` | per-call traces (S, S_sem, S_rule, decision, latency, contract) |
| `report.json` / `report.md` | headline, stats, breakdowns, latency, utility, pareto |
| `error_taxonomy_{injecagent,mcptox}.json` | residual records + contracts + scores |
| `logs/` | per-job stdout logs + orchestrator out/err (progress record) |

## Limitations

1. **MCPTox evaluator is heuristic** (payload/sensitive-path; precision 0.82 / recall 0.26 vs
   authors' labels, E3) — success counts are substrate-relative, reported alongside
   attack-influenced for that reason.
2. **Paired stats cover the two primary slices** (ds_enhanced + MCPTox); remaining slices have
   headline CIs only in this report.
3. **No dedicated legitimate-only suite** — FPR rests on valid-rate parity + the E4 pilot.
4. **Single backbone** (gpt-4o-mini) — generality is claimed, not yet shown → Phase 6 P0.
5. **Static snapshot, not live servers** (blueprint Sec 8) → Phase 6 P2 slice.
6. **Small-n flat spots** (Message Hijacking n=44, Data Tampering n=120) — reported, not smoothed.
7. **A3 ≈ ours** narrows the contract-parsing claim to auditability/escalate input rather than
   detection lift on these splits — stated here so reviewers don't have to find it.

## Supervisor Q&A

**Q: Why is A1 (semantic-only) as good as or better than ours at attack reduction?**
A: Because detection is semantic-led — A2 proves rules alone do nearly nothing on ds/MCPTox.
The rules' value is precision vetos on dh-style side effects and the veto signal the escalate
band consumes, plus determinism reviewers can audit. The combined score is the shipped design;
the ablation decomposes it honestly.

**Q: Isn't B2 a strawman at 8.1% coverage?**
A: Coverage is frozen, counted, and reported — and the *weighted* 37.2% covers the tools that
actually get called, yet B2 still ≈ B1 (p=1.00/0.33). The failure isn't lack of contracts on
the tail; it's structural: per-tool Hoare contracts can't see poisoned registrations or
attacker tools outside the evaluated set. Phase 6 extends the curve toward ~70% weighted to
close this objection empirically.

**Q: 21.6% escalate share — isn't that a utility alarm?**
A: In benchmark mode escalate counts as block, and valid-rate parity shows legitimate
throughput is unaffected — the band fires on attacker-tool calls, which is its job. The open
question is escalate *precision* on real ambiguous traffic → Phase 6 E19 hand-label study.

**Q: What would change your conclusion?**
A: A legit-only suite showing FPR > 10%, a second backbone showing no delta, or B2 at high
coverage matching ours. All three are queued as Phase 6 P0/P1 — the freeze stands regardless.
