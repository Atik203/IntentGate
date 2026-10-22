# Paper-to-Code Audit (T4) — IntentGate

**Date:** 2026-10-22
**Scope:** Compare `IEEE-conference/IEEE-conference.tex` claims/equations against `src/intent_gate/`
and configs. Deliverable for Sprint 0 task T4. No source files changed except the one must-fix
manuscript equation noted below (with rebuild required).

**Verdict:** One must-fix normalization mismatch (fixed in tex). All other items are either
equivalent under a documented mapping or documentation-only mismatches. No must-fix code change.

---

## Traceability table

| # | Paper claim (location) | Code location | Status | Notes |
|---|---|---|---|---|
| 1 | Eq. 1 `C = (A, K, H)` — allowed (entity,operation,resource), numeric/path constraints, high-risk flags (`IEEE-conference.tex:118-121`) | `src/intent_gate/types.py:24-47` `IntentContract` (goals, expected_tool_categories, permitted_data_access, side_effect_limits, specificity, raw_request); `parser/schema.py` | **Abstraction mismatch (doc only)** | Paper uses abstract (A,K,H); code uses concrete v1.1 fields. Mapping: A ≈ goals+expected_tool_categories+permitted_data_access; K ≈ side_effect_limits (financial/external_send/file_write/code_exec/system_change); H ≈ fail-closed `FAIL_CLOSED_LIMITS` + specificity. No code change; keep mapping in this table. |
| 2 | Eq. 2 `S_sem = cos(e_C, e_c)` raw cosine (`IEEE-conference.tex:125-127`) | `src/intent_gate/scoring/scorer.py:30` `s_sem = (cosine(...) + 1.0)/2.0` | **MUST-FIX (manuscript)** | Code rescales cosine [-1,1]→[0,1]; paper wrote raw cosine. Fixed in tex (eq. 2 now shows (1+cos)/2). Rebuild required. |
| 3 | Eq. 3 `S = α·S_sem + (1−α)·S_rule`, α=0.7 (`IEEE-conference.tex:129-131`) | `scorer.py:34` `s = alpha*s_sem + (1-alpha)*s_rule`, alpha default 0.7 | Match | — |
| 4 | Hard veto: S_rule=0 → S=0 (`IEEE-conference.tex:138`, eq. 4) | `scorer.py:32-33` `if triggered and s_rule==0.0: return 0.0` | Match (code folds veto into S=0) | Paper states block if S_rule=0 OR S<τ−δ; code sets S=0 then decide() blocks. Equivalent given veto. |
| 5 | Eq. 4 decision band: allow if S≥τ; escalate if τ−δ≤S<τ; block otherwise (`IEEE-conference.tex:136-143`) | `gate/decisions.py:7-11` `decide()` | Match | decide() default tau=0.6 differs from frozen 0.75 (see item 8). |
| 6 | Threshold τ=0.75, δ=0.1, α=0.7 fixed on 50-call pilot (`IEEE-conference.tex:132`) | `configs/thresholds.yaml:4-6` (tau 0.75, delta 0.1, alpha 0.7) | Match | — |
| 7 | Parser: LLM temp 0, JSON mode, one repair retry, then fail-closed minimal contract (`IEEE-conference.tex:117`) | `parser/parser.py:56-69` (max_retries=1 → 2 attempts; minimal_contract on failure) | Match | — |
| 8 | Gate middleware default tau | `gate/middleware.py:25` `tau: float = 0.6`; `decisions.py:7` `tau: float = 0.6` | **Latent default mismatch (file as issue)** | Constructor default 0.6 ≠ frozen operating point 0.75. Runs pass 0.75 via CLI/config, so results unaffected, but the default is a footgun. Recommend aligning default to 0.75 with test updates (tests at :52, :60, :74, :91, :105 in test_no_bypass.py use tau=0.6 explicitly, so change is low-risk but requires edit). Not applied here to avoid breaking frozen test expectations silently. |
| 9 | p95 latency 16–20 ms CPU (`IEEE-conference.tex:144, 255`) | `gate/middleware.py:81-84` (perf_counter around _score) | Match (gate-only) | Manuscript says "per-call gate overhead"; code measures gate-only. Good. |
| 10 | B2 coverage: InjecAgent 79/79 (100%), MCPTox 65/801 (8.1% distinct, 37.2% weighted) (`IEEE-conference.tex:218`) | `baselines/toolgate/` + `configs/b2_coverage.json` | Match | — |
| 11 | Setup cost: 0 vs 145 contracts (`IEEE-conference.tex:218, 220, 289`) | roadmap success criteria + results | Match | — |
| 12 | InjecAgent 2,108 cases; MCPTox 1,348 static-snapshot cases (`IEEE-conference.tex:225`) | Phase 5 freeze (30 jobs, 20,736 cases) | Match | Manuscript scopes MCPTox to static snapshot; limitations repeat. Good. |
| 13 | McNemar p=1.3e-33 / p=1.25e-07 on primary slices (`IEEE-conference.tex:239`) | `results/phase5/` + E14 | Match | — |
| 14 | Escalate precision 60.7% / 14.8% / 24.5% (`IEEE-conference.tex:144`) | E21 (583 escalated calls) | **Unsourced in manuscript (doc only)** | Add (n=583, E21) qualifier. No code change. |
| 15 | qwen3.5:4b replication 27.1%→2.1% (`IEEE-conference.tex:348`) | E18 (`results/phase6/qwen_pilot_{b1,ours}_full/summary_base.json`; 100 cases per condition, 50 dh + 50 ds) | **Resolved (doc only)** | Manuscript now states "n=100 attack cases per condition, E18". No code change. |
| 16 | Fail-closed on missing contract fields (`IEEE-conference.tex` abstract/limit) | `parser/schema.py:9-15` `FAIL_CLOSED_LIMITS` | Match | — |
| 17 | No-bypass: all calls through `GateMiddleware.execute()` (`IEEE-conference.tex:114`) | `gate/middleware.py:98-110` + `tests/test_no_bypass.py` | Match | — |
| 18 | Ordering invariant: parse before attacker content (`IEEE-conference.tex:114`) | `harness/common.py` OrderingGuard + tests | Match | — |
| 19 | JSONL trace per call (`IEEE-conference.tex` not explicit) | `gate/trace.py` | Match (blueprint invariant) | — |
| 20 | Conformal band [0,1] vacuous negative result (Phase 7) | `results/phase7/e30_conformal_band/report.json` | Not in manuscript (correctly omitted) | Good — kept out of conference paper. |

## Must-fix applied

- `IEEE-conference/IEEE-conference.tex` eq. 2: `S_sem` now shows the (1+cos)/2 rescaling to match `scorer.py`. **Rebuild required** (`pdflatex`+`bibtex`); verify page count stays ≤6.

## Filed as issues (not applied)

1. **Default τ mismatch** (item 8): align `GateMiddleware`/`decide` default to 0.75 with test updates. Low risk but touches frozen test expectations; recommend as a separate small PR before Phase 8 v2 work.
2. **Manuscript qualifiers** (items 14, 15, and ablation A1 utility line): add (n=...) to three lines. Should be done as a patch-rebuild per Sprint 0 Part A ("patch-rebuild only for blocking issues"). Treat as blocking for reviewer clarity.
3. **Schema naming** (item 1): document the (A,K,H)↔(goals, categories, scopes, limits) mapping in the paper's method section or keep in this audit. Recommend adding one sentence in §Method.

## Verification commands run

- `pytest -q` → 246 passed (3.78s).
- `ruff` not installed in venv; no Python files changed in this task, so no lint impact.
- No `results/` or frozen artifacts modified.

## Bottom line

The manuscript and code agree on the load-bearing invariants (scorer equation after the eq. 2 fix, veto, decision band, parser fallback, no-bypass, ordering, latency, B2 coverage, setup cost). The remaining items are documentation qualifiers and one latent default-τ footgun, none of which invalidate the frozen results. T4 is complete; next agent-executable Sprint 0 item is T5 (v2 argument-policy layer), which remains blocked on T2/T3 human gates.
