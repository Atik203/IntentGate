# Plan: ICEEICT 2027 submission — parallel validation + paper drafting

## Goal
Submit a 6-page IEEE double-blind paper by 2026-10-25 (target submission-ready by 2026-10-22) using existing frozen results (E11–E17) plus the most critical Phase 7 validation experiments named by the supervisor.

## Strategy
Do both tracks in parallel, but let the paper draft lead with frozen findings while validation results are appended as they land. Keep preliminary (E18+) numbers clearly labeled and never overwrite frozen Phase 5 numbers.

## Track A — Paper drafting (start immediately)
1. Use `IEEE-conference/IEEE-conference.tex` (already compiles with pdflatex; `.vscode/settings.json` added) as the IEEE double-column template base.
2. Outline for ≤6 pages:
   - Abstract + Intro (problem, OWASP excessive agency, action gate)
   - Method (intent parser, contract schema, scorer S = α·S_sem + (1−α)·S_rule, veto, gate middleware, escalate band)
   - ToolGate B2 baseline (coverage %, setup cost 0 vs 145 contracts)
   - Evaluation (metrics, baselines, ablations, stats)
   - Results (ASR/FPR/latency/setup-cost tables, Pareto, error taxonomy)
   - Limitations + Conclusion
3. Anonymize for double-blind: no author names/affiliations/emails, no direct self-citation wording, no identifying repo paths.
4. Add LLM-usage acknowledgement in the Acknowledgement section (per ICEEICT rules).
5. Distinguish established (E11–E17) vs preliminary (E18+) results explicitly.

## Track B — Critical validation (Phase 7 P0, highest supervisor priority)
Run in parallel, writing to `results/phase7/` and `docs/experiments/07_phase7_pilots.md`:
- **E23 benign-task utility suite** — ~100 benign tasks, gate ON vs OFF; report completion rate Δ (pp) and clean-call block rate. Relabel E22's 12.4% stratum metric from "FPR" to block-rate-by-stratum.
- **E24 prompt-level baselines** — delimiters / instructional prevention / sandwich defenses on the 100-case slice; 5-metric panel (ASR, utility, latency, setup cost, backbone).
- **E25 third backbone** — DeepSeek/Claude/Llama-70B-class, 100-case protocol, parser stays gpt-4o-mini; per-backbone delta table.
- **E26 adaptive attacker** — (a) ASB's 5 paraphrase phrasings re-scored live; (b) threshold-aware attacker targeting S ∈ [0.75, 0.79]; report ASR-under-adaptation.
- **E31 contract-vs-semantic** — offline on cached traces: per-category/per-risk flips (ours vs A1), escalate-band ablation without S_rule/veto, cost/latency parity.

## Stretch (time permitting)
- **E27 Progent comparison** — read Progent + scope-out table or faithful-mini port; cite in `literature_review/` + `references.bib`.
- Artifact packaging (Dockerfile + repro) — lower priority given deadline.

## Affected boundaries
- New run outputs under `results/phase7/` only; no edits to frozen `results/phase5/`.
- `docs/experiments/07_phase7_pilots.md` (new) following the established template.
- `roadmap.md` checkboxes + `CHANGELOG.md` `[Unreleased]` updated per completed task.
- Paper source: `IEEE-conference/IEEE-conference.tex` + `references.bib`.

## Failure modes / risks
- Running out of time before E25/E26 → scope the paper's generality/adaptive-robustness claims to measured evidence only.
- Benign task set (ToolBench/AgentDojo benign) may need a new loader under `harness/adapters/` — budget for that.
- Double-blind violations (self-citation wording, author metadata) → checklist review before submission.
- IEEE 6-page limit → keep results tables compact; move detailed breakdowns to supplementary if needed.

## Validation
- `pytest -q` stays green (199 passing) before/after any `src/` or `harness/` change.
- No-bypass and ordering tests remain green.
- PDF builds cleanly with `pdflatex` + `bibtex` (verified).
- Integrity: `scripts/run_phase5.py --check` for frozen runs; new runs use explicit `--out`/`--report`.

## Step-by-step execution (do in this order)

### Week 1 (validation + draft skeleton)
1. Freeze a 100-case InjecAgent pilot slice (dh+ds, base) and document the exact case IDs used by E18.
2. Draft paper outline + section stubs in `IEEE-conference/IEEE-conference.tex` (Intro, Method, Evaluation, Results, Limitations, Conclusion) with placeholder tables; keep ≤6 pages.
3. Implement E23 benign-utility harness run (gate ON vs OFF) and record completion-rate Δ + clean-call block rate.
4. Implement E24 prompt-baseline modes in `harness/gate_policy.py` and run on the 100-case slice.
5. Run `pytest -q` after any harness change.

### Week 2 (generality + adaptive + contract value)
6. Run E25 on DeepSeek (recommended) using `--model-name`/base URL flags; record per-backbone delta table.
7. Run E26 (a) paraphrase-delivery with ASB's 5 phrasings; (b) threshold-aware attacker targeting S ∈ [0.75,0.79].
8. Run E31 offline on cached Phase 5 traces: flip table, escalate-band ablation, cost/latency parity.
9. Relabel E22's 12.4% stratum metric from "FPR" to block-rate-by-stratum in `docs/experiments/06_phase6_pilots.md`.
10. Update `docs/experiments/07_phase7_pilots.md` with results as they land.

### Week 3 (baselines + formalism + freeze)
11. E27: read Progent; produce scope-out table or faithful-mini port; cite in `literature_review/` + `docs/references.bib`.
12. Method formalism: Neyman–Pearson τ-selection paragraph, assumption-violation table, Anderson reference-monitor framing (2 sentences) in Ch 3.
13. Finalize all tables/figures; check double-blind anonymization and IEEE 6-page limit.
14. Final PDF build via `pdflatex` + `bibtex`; verify fonts embedded and file ≤3 MB.
15. Update `roadmap.md` checkboxes + `CHANGELOG.md` `[Unreleased]`; submit via CMT by 2026-10-25.

### Daily guardrails
- Never edit frozen `results/phase5/`.
- All new runs use explicit `--out`/`--report` under `results/phase7/`.
- `pytest -q` must stay green (199 passing).
- Keep static-attack scope claim prominent if E26 is incomplete.

## Validation
- `pytest -q` (199 passing) before/after `src/` or `harness/` changes.
- No-bypass and ordering tests green.
- PDF builds cleanly; double-blind check; ≤6 pages; ≤3 MB; fonts embedded.
- Integrity: `scripts/run_phase5.py --check` for frozen runs.

## Open questions (recommended defaults)
1. Third backbone: DeepSeek (recommended) vs Claude/Llama-70B. Default DeepSeek.
2. Benign task source: AgentDojo benign tasks (recommended) vs ToolBench benign slice.
3. E27: scope-out table unless time remains after E23–E26/E31.
4. Adaptive robustness claim: report E26 honestly; keep static-attack scope claim prominent.
1. Which third backbone is reachable via API — DeepSeek (recommended, already in model notes) or Claude/Llama-70B? Default: DeepSeek.
2. Benign task source — AgentDojo benign tasks (recommended, already in repo data) vs ToolBench benign slice.
3. E27 Progent port vs scope-out — recommend scope-out table unless time remains after E23–E26/E31.
4. Should the paper claim adaptive robustness now, or defer to future work? Recommend: report E26 numbers honestly and keep the static-attack scope claim prominent.