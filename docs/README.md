# Docs — index

> Documentation hub for the IntentGate thesis. Start with the **blueprint** for the design, then
> the **experiments** folder for what has been run and measured.

## What lives where

| Document | What it is | When to read it |
|---|---|---|
| [`blueprint.md`](blueprint.md) | Design source of truth (Sec 0–18): problem, pipeline, scorer, B2 baseline, datasets, evaluation plan, risks, roadmap, supervisor/team explanations, Reviewer #2 critique | Before touching design decisions |
| [`setup.md`](setup.md) | Install & verify guide (venv, deps, `.env`, tests, benchmark clones, harness commands) | First day / fresh machine |
| [`experiments/README.md`](experiments/README.md) | Experiment hub: status matrix, E1–E10 index, datasets, pinned models, artifact map, reproduce commands, merge map, cross-cutting Q&A | To see what is done and how to reproduce it |
| [`experiments/01_gate0_foundation.md`](experiments/01_gate0_foundation.md) | E1–E4: B1 reference/parity, MCPTox B1, Gate 0 scorer pilot (GO) | Understanding the trust checks and Assumption 2 |
| [`experiments/02_parser_schema.md`](experiments/02_parser_schema.md) | E5–E6: parser v1 freeze and schema v1.1 unfreeze (`system_change`) | Parser/contract questions |
| [`experiments/03_b2_toolgate.md`](experiments/03_b2_toolgate.md) | E7: ToolGate B2 contracts, coverage freeze, validation, divergence | Baseline-fairness questions |
| [`experiments/04_gate2_gated_eval.md`](experiments/04_gate2_gated_eval.md) | E8–E10: gated integration run, threshold sweep/Pareto, error taxonomy | The main results and their caveats |
| [`references.bib`](references.bib) | BibTeX citation basis (10 verified papers) | Writing/citing |

Related roots outside `docs/`:

- [`roadmap.md`](../roadmap.md) — status tracker (Phases 0–8, Gates 0–3, success criteria).
- [`literature_review/`](../literature_review/) — frozen paper reviews + index (5 anchors + ToolGate).
- [`CHANGELOG.md`](../CHANGELOG.md) — change log (`[Unreleased]` for the current PR window).
- [`AGENTS.md`](../AGENTS.md) — conventions for AI coding agents working in this repo.

## Status snapshot (2026-09-16)

| Gate | Definition | Status |
|---|---|---|
| Gate 0 | B1 reproduces + 50-case pilot passes | ✅ 2026-09-11 |
| Gate 1 | B2 reimpl validated (coverage reported) | ✅ 2026-09-16 |
| Gate 2 | Gate integrated; tests green; p95 latency measured | ✅ 2026-09-16 |
| Gate 3 | Full-suite results freeze | ⏳ Phase 5 |

Headline dev-set result: on 100 InjecAgent cases the gate reduced attack success **9/100 → 0/100**
(0 false-positive blocks) and on 100 MCPTox cases **22 → 10** attack-influenced calls, at
**≤ 23 ms p95** overhead. Details and caveats in
[`experiments/04_gate2_gated_eval.md`](experiments/04_gate2_gated_eval.md).

## Conventions

- The blueprint is the design source of truth; the roadmap is the status source. If they conflict,
  flag it — do not silently pick one.
- Experiment reports follow one template: **At a glance → Goal → Setup → Results → Artifacts →
  Limitations → Supervisor Q&A** (see `experiments/README.md`).
- Design or literature-review changes must update the affected docs **and** `roadmap.md` +
  `CHANGELOG.md` in the same PR.
