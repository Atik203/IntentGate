# IntentGate

**Intent-Consistency Verification at the Action Gate: A Request-Derived Alternative to Formal Contract Gating for Tool-Using LLM Agents**

> LLM Security · Agentic AI · AI Safety — Thesis Project (2026) · [github.com/Atik203/IntentGate](https://github.com/Atik203/IntentGate)

> **Status (2026-10-22):** v1 implementation and Phases 1–7 evaluation are complete; the ICEEICT
> manuscript completed its final pass on 2026-10-20. Phase 8 is a planned journal-strengthening
> study. Its research questions and candidate contributions are provisional until the related-work
> and protocol gates pass. See [`roadmap.md`](roadmap.md) and [blueprint Section 19](docs/blueprint.md#section-19--journal-extension-research-questions-and-contribution-boundary).

MCP-style agents execute real actions (email, payments, code, files). Request-derived policies and runtime action authorization now appear in several systems. Their policy representations, update lifecycles, threat models, and evaluations differ; the journal study will compare them under a shared protocol before making a novelty claim.

IntentGate v1 is a **model-agnostic middleware gate** that derives an _intent contract_ from the user's original request and scores proposed tool calls before execution. Its completed evaluation compares an unprotected agent and a ToolGate reimplementation on pinned InjecAgent and MCPTox suites. The resulting evidence is bounded to those tasks, models, and implementations.

## Setup

New to the project? Start with **[`docs/team_guide.md`](docs/team_guide.md)** — a beginner-friendly
explanation of the project, what has been done, and where it is going.

Install and verify in ~5 minutes: see **[`docs/setup.md`](docs/setup.md)** (venv + `pip install -e ".[dev]"` + `.env` + `pytest -q` + smoke-test scripts).

---

## Repository Structure

```
IntentGate\
├── README.md                      # this file
├── CONTRIBUTING.md                # branch model, PR rules, definition of done
├── SECURITY.md                    # vulnerability reporting + scope
├── CODE_OF_CONDUCT.md             # Contributor Covenant v2.1
├── CHANGELOG.md                   # Keep a Changelog; updated per PR
├── LICENSE                        # MIT
├── AGENTS.md                      # instructions for AI coding agents (+ LLM cache guidance)
├── roadmap.md                     # phased tracker (Phases 0–8, Gates 0–3, success criteria)
├── docs\
│   ├── README.md                  # docs hub (where everything lives + status snapshot)
│   ├── setup.md                   # install + verify instructions (venv, pip, .env, tests)
│   ├── blueprint.md               # single source of truth (design, Sec 0–18, indexed)
│   ├── references.bib             # BibTeX citation basis (10 verified papers)
│   └── experiments\               # experiment record: README hub + 01–05 reports (E1–E17)
├── pyproject.toml                 # intent-gate package (pip install -e .)
├── .github\                       # PR/issue templates + CI (pytest on dev/main)
├── configs\                       # intent_schema.json, parser_fewshots.json, thresholds.yaml, models.yaml
├── src\intent_gate\               # parser / scoring / gate / agent / baselines.toolgate / eval
├── harness\                       # run_injecagent.py, run_mcptox.py, compare_b2.py, common.py
├── scripts\                       # pilot_score_dist.py, check_parser.py, clone_benchmarks.ps1
├── tests\                         # pytest suite (parser, veto, no-bypass, ordering, metrics)
├── data\                          # (gitignored) benchmark clones + snapshots — scripts/clone_benchmarks.ps1
├── results\                       # tracked on purpose: JSONL traces + reports (teammates read instead of re-running evals)
├── literature_review\
│   ├── index.md                   # Master Comparison Matrix + Gap Map + Verification Log (5 anchors + Closest)
│   └── papers\
│       ├── 01-agentdojo-debenedetti-2024.md   # Anchor — dynamic 97-task/629-case injection harness
│       ├── 02-injecagent-zhan-2024.md         # Anchor — 1,054 indirect-injection cases
│       ├── 03-mcptox-wang-2025.md             # Anchor — 1,312 live-MCP poisoning cases
│       ├── 04-asb-zhang-2025.md               # Anchor — 10-scenario/27-method superset
│       └── 05-toolgate-liu-2026.md            # Closest — Hoare-contract gate (B2 baseline)
├── literature_review.md           # (local, gitignored) original 10-paper Q1–Q9 synthesis
├── mds\                           # (optional, gitignored) pasted paper markdowns for offline access
└── pdfs\                          # (optional, gitignored) paper PDFs
```

## Branch Model (5-member team)

```
feature branch (feat/, fix/, docs/, exp/, <member>/) ──PR──> dev ──PR (tested+reviewed)──> main
```

- **`main`** — production. Only merges from `dev` after all tests pass. Never commit directly.
- **`dev`** — integration branch. All feature PRs target `dev`.
- Feature branches start from `dev`, named after the feature or the member (e.g. `feat/gate-veto`, `atik/toolgate-contracts`).

Full rules: [`CONTRIBUTING.md`](CONTRIBUTING.md). Security reports: [`SECURITY.md`](SECURITY.md).

---

## Literature Review

- **Index:** [`literature_review/index.md`](literature_review/index.md) — v1 review matrix plus newly identified closest systems; the Phase 8 feature-level audit remains open
- **Papers:** 5 detailed reviews in `literature_review/papers/` — each follows the same template (badges, Summary, Relevant to Our Idea, Gap, Q1–Q9, Citation, Method, Results, Limitations, Comparison, Positioning, Reproducibility, Cross-References, Relevance to Thesis)
- **Blueprint:** [`docs/blueprint.md`](docs/blueprint.md) — completed v1 design (Sections 0–18) plus provisional journal study (Section 19)
- **Roadmap:** [`roadmap.md`](roadmap.md) — phased tracker (Phases 0–8, Gates 0–3, success criteria, current status)
- **Docs hub:** [`docs/README.md`](docs/README.md) · **Team guide (start here):** [`docs/team_guide.md`](docs/team_guide.md) · **Experiments:** [`docs/experiments/README.md`](docs/experiments/README.md) — status matrix, experiment index E1–E17, datasets, pinned models, artifact map, reproduce commands, supervisor Q&A

All 6 reviewed papers were checked against their primary full text. BibTeX: [`docs/references.bib`](docs/references.bib).

---

## Core Idea (10-point summary)

1. **Title:** Intent-Consistency Verification at the Action Gate: A Request-Derived Alternative to Formal Contract Gating
2. **Domain:** LLM Security · Agentic AI · AI Safety
3. **Motivation:** Tool-using agents can produce harmful side effects; current task-derived and runtime authorization systems need matched comparison under common threats and tasks
4. **Problem:** Injection, tool poisoning, and drift all converge to one observable — an agent executes an action the user never intended
5. **V1 study question:** whether a request-derived action gate reduces measured attack success on InjecAgent and MCPTox with acceptable utility and latency compared with the tested baselines; this does not establish uniqueness against newer systems
6. **Solution:** Parse user request → structured intent contract (goals, tool categories, data scopes, side-effect limits) → middleware gate scores every proposed `tool_call(name,params)` via `S = α·((cosine(embed(contract), embed(call))+1)/2) + (1-α)·rule_compliance` with veto; decision `allow / block / escalate` via threshold `τ` (sweep)
7. **Research status:** v1 prototype and frozen evaluation are complete; request-derived policies and action-level gates overlap with newer systems, so no “first” claim is made. The journal study's candidate contribution is a controlled comparison of policy representation and update lifecycle, subject to the Phase 8 related-work gate.
8. **Deliverables:** Pip-installable wrapper, ToolGate reimplementation (Appendix G), frozen evaluation report, and completed ICEEICT conference manuscript; journal extension is planned in `roadmap.md` Phase 8.
9. **Frozen evaluation:** B1 vs. B2 ToolGate reimplementation vs. v1 on InjecAgent (2,108) and MCPTox (1,348); results and limitations are frozen in the experiment reports. Planned studies use separate Phase 8 runs.
10. **Stack:** Open LLM (Qwen/Llama via API), ReAct/MCP client, Python middleware, `all-MiniLM-L6-v2` (CPU), no fine-tuning

---

## Frozen v1 Evaluation (abridged from `docs/blueprint.md:Section 9`)

- **B1:** Unprotected ReAct (no gate) — raw vulnerability floor
- **B2:** ToolGate reimplementation (Hoare `{P}T{Q}` per Appendix G, symbolic world-state) — validated on ToolBench/MCP-Universe subset before adversarial runs
- **Metrics:** ASR-valid, FPR, escalation rate, latency p50/p95, setup cost, utility retention on benign cases
- **Ablations:** A1 semantic-only, A2 rule-only, A3 raw-request vs structured contract, A4 threshold/escalate sweep
- **Stats:** Bootstrap 95% CI on ASR, paired McNemar per case, per-risk-category breakdown (MCPTox 11 categories, InjecAgent 17 tools)

---

## Reproduce the v1 study (completed)

```bash
# 1. Clone pinned benchmark snapshots
git clone https://github.com/uiuc-kang-lab/InjecAgent
git clone https://anonymous.4open.science/r/AAAI26-7C02  # MCPTox snapshot
git clone https://github.com/OceannTwT/ToolGate          # B2 reference
git clone https://github.com/ethz-spylab/agentdojo       # stretch

# 2. Install gate
pip install -e .  # pip wrapper around agent tool executor

# 3. Run a harness evaluation (use the exact commands/configs in the experiment reports)
python harness/run_injecagent.py --cases data/raw/InjecAgent/data/test_cases_dh_base.json --gate ours --threshold 0.6 --report results/injecagent.json
python harness/run_mcptox.py --gate ours --snapshot v1 --report results/mcptox.json
python harness/compare_b2.py --cases data/raw/InjecAgent/data/test_cases_dh_base.json --report results/comparison.json
```

> For reproduction commands and artifact integrity checks, follow [`docs/setup.md`](docs/setup.md) and
> [`docs/experiments/README.md`](docs/experiments/README.md). Do not overwrite frozen results; new
> journal experiments use the Phase 8 protocol and `results/phase8/`.

---

## Publication Status and Journal Direction

The ICEEICT conference manuscript covers the completed v1 study. A journal target has not been
selected: Phase 8 first requires a current related-work audit, a defensible extension, and verification
of journal scope, category-specific quartiles, fees, and conference-extension policy. See
[`roadmap.md`](roadmap.md) Phase 8 and [`docs/blueprint.md`](docs/blueprint.md#section-19--journal-extension-research-questions-and-contribution-boundary).

---

## Verified Papers

| #   | Paper                                | Venue                | Role                    |
| --- | ------------------------------------ | -------------------- | ----------------------- |
| 1   | AgentDojo (Debenedetti et al., 2024) | NeurIPS D&B          | Anchor benchmark        |
| 2   | InjecAgent (Zhan et al., 2024)       | Findings of ACL 2024 | Anchor benchmark        |
| 3   | MCPTox (Wang et al., 2025)           | arXiv → AAAI 2026    | Anchor benchmark (live) |
| 4   | ASB (Zhang et al., 2025)             | ICLR 2025            | Anchor superset         |
| 5   | ToolGate (Liu et al., 2026)          | arXiv 2601.04688v1   | Closest system (B2)     |

Full reviews: [`literature_review/papers/`](literature_review/papers/)

---

## Contributing

5-member team workflow: feature branch → `dev` → `main`. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before your first PR; CI runs `pytest -q` on `dev` and `main`. All contributors follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Report vulnerabilities privately per [`SECURITY.md`](SECURITY.md) (never in public issues).

## License

[MIT](LICENSE) — Copyright (c) 2026 IntentGate contributors.

---

## Citation

```bibtex
@misc{intentgate2026,
  title={Intent-Consistency Verification at the Action Gate: A Request-Derived Alternative to Formal Contract Gating for Tool-Using LLM Agents},
  year={2026},
  note={Thesis project — IntentGate, https://github.com/Atik203/IntentGate}
}
```

---

_Last updated: 2026-10-13 — blueprint is the single source of truth, roadmap.md tracks status. Phase 6 (E18–E22) complete._
