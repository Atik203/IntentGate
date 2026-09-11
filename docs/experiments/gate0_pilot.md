# Gate 0 — Scorer pilot (Assumption 2) — **GO**

**Date:** 2026-09-11 · **Decision:** embeddings + rule veto separate hijack from legit calls;
proceed to Phase 3 (ToolGate B2) and Phase 4 (gate integration) with default `tau = 0.75`.

## Setup

| Item | Value |
|---|---|
| Labeled calls | 25 hijack + 25 legit = 50 (constructed from 25 InjecAgent `base` cases: 13 dh + 12 ds) |
| Contracts | LLM parser v1 (all 25 parsed by the LLM backend) |
| Scoring | `S = 0.7*S_sem + 0.3*S_rule` with critical veto; `all-MiniLM-L6-v2` on CPU |
| Scripts | `scripts/build_pilot_set.py` → `scripts/pilot_score_dist.py` |

Hijack calls use the benchmark's attacker tool + parameters extracted from the attacker
instruction; legit calls use the case's user tool and its real parameters. Constructed
calls are a documented approximation (`docs`), not model outputs.

## Final results

| Metric | Value |
|---|---|
| hijack S | mean 0.537 ± 0.303 (6 vetoed to 0.0; rest 0.6–0.8) |
| legit S | mean 0.849 ± 0.040 (cluster 0.8–0.9) |
| **AUC (legit > hijack)** | **0.979** |
| At τ = 0.75 | **ASR = 0.0% · FPR = 4.0%** (1/25) |
| Borderline | `GmailReadEmail` legit at S = 0.69 (semantic 0.55) |
| τ sensitivity | τ ≤ 0.65: ASR 76%; τ = 0.70: ASR 40%; τ = 0.75: ASR 0% |

## What the pilot caught (three rule-engine false positives, fixed before freeze)

1. **CamelCase tools uncategorized** — benchmark names like `BankManagerTransferFunds`
   bypassed the snake_case category sets → added keyword-based categorization.
2. **`email` → send** — `GmailReadEmail`/`GmailSearchEmails` were vetoed as "external
   send" (FPR 20% → 12%). Send now requires action verbs (`send`, `post`, `forward`,
   `reply`, or `share` + sensitive object).
3. **`share` → send** — `GoogleCalendarGetEventsFromSharedCalendar` was vetoed; now only
   sensitive sharing (`...SharePassword`) counts (FPR 12% → 4%).

AUC improved 0.80 → 0.86 → **0.979** across the three fixes. Covered by
`tests/test_scorer_veto.py::test_camelcase_*`.

## Decision: **GO**

Gate 0 success criteria: scorer separates the classes at a usable operating point
(ASR 0% with FPR 4% < 10% target). Proceed:

- **Phase 3:** ToolGate B2 contracts (Weeks 3–4, Gate 1).
- **Phase 4:** gate integration with `tau = 0.75` default (updated in
  `configs/thresholds.yaml`; full sweep still reported in Phase 5).

## Caveats

- Constructed hijack parameters, n = 50, one benchmark (InjecAgent) — MCPTox calls join
  the full evaluation.
- Operating point τ = 0.75 is specific to MiniLM + this contract format; A3 (raw-request
  embedding) may shift it — that ablation is exactly what Phase 5 measures.
- `GmailReadEmail` borderline shows the FPR risk concentrates in low-lexical-overlap
  legit calls; keep an eye on the escalate band.
