# Contributing to IntentGate

Thanks for working on IntentGate. This is a 5-member thesis team; read this before your first push.

## Branch model

```
feature branch (you) ──PR──> dev ──PR (tested, reviewed)──> main (production)
```

- **`main`** — production branch. Only accepts merges from `dev` after all tests pass. Never commit directly.
- **`dev`** — main development/integration branch. All feature work lands here first.
- **Feature branches** — created from `dev`, named after the member or the feature:
  - `feat/<topic>` e.g. `feat/gate-veto`, `feat/toolgate-contracts`
  - `fix/<topic>` e.g. `fix/escalate-band`
  - `docs/<topic>` e.g. `docs/setup-typos`
  - `exp/<topic>` e.g. `exp/pilot-scoring` (experiments/notebooks)
  - Personal form (optional): `<member>/<topic>` e.g. `atik/gate-veto`

```bash
git checkout dev
git pull origin dev
git checkout -b feat/your-topic
# ... work ...
git push -u origin feat/your-topic
```

Open a Pull Request **into `dev`**, not `main`. When a release milestone (Gate) is fully tested, a maintainer merges `dev` into `main`.

## Pull request rules

- Target branch: `dev` (except release PRs `dev` → `main`).
- Minimum **1 approving review** before merge; 2 for gate-critical code (`src/intent_gate/gate/`, `parser/`, `scoring/`).
- CI must be green (`pytest -q` via GitHub Actions).
- Keep PRs focused: one topic per PR; rebase/merge `dev` before requesting review.
- Reference the roadmap phase/item you are completing (e.g. "Phase 4 — Gate 2").
- Update `roadmap.md` checkboxes (`[ ]` → `[x]`) in the same PR that completes the task.

Use the PR template checklist.

## Definition of done

A task is done when:

1. `pytest -q` passes (26+ tests; add tests for new behavior).
2. New behavior is typed and exported through `src/intent_gate/types.py` dataclasses when it is gate I/O.
3. Gate-call logging is preserved (`gate/trace.py` JSONL must keep `S`, `S_sem`, `S_rule`, decision, latency).
4. No-bypass and ordering tests stay green (`tests/test_no_bypass.py`, `tests/test_gate_ordering.py`).
5. `roadmap.md` updated; `CHANGELOG.md` entry added under `[Unreleased]`.

## Commit messages

Conventional Commits, imperative, concise:

```
feat(gate): add escalate band to middleware
fix(scorer): clamp cosine mapping to [0,1]
docs(setup): add Windows troubleshooting
test(parser): cover vague-request fail-closed
chore(ci): run pytest on pull requests
```

## Code style

- Python 3.11+, fully typed, dataclasses for I/O contracts.
- **No comments** unless asked; docstrings document design decisions tied to blueprint sections.
- Line length <= 100; run `ruff check .` before pushing.
- Deterministic: seed randomness, `temperature=0`, pin model IDs, log hashes.
- Fail-closed: unknown/missing contract fields default to `disallow` for high-risk side effects.

## Security and secrets

- Never commit `.env`, API keys, `data/raw/`, or `results/*.jsonl` (gitignored; verify with `git status`).
- Benchmark attack payloads are research artifacts — never run them outside the sandbox.
- Report vulnerabilities per `SECURITY.md`, not in public issues.

## Experiment discipline

- One variable per experiment; lock benchmark commit hashes and model IDs in the results log.
- Raw results stay in `results/` (gitignored); summarize only the final tables/figures in PRs and papers.
- If a result invalidates a blueprint assumption, flag it in the PR and to the team — do not silently adapt results.

## Code of Conduct

All contributors follow `CODE_OF_CONDUCT.md`. Be direct about the science, generous with the people.

## Releases

Maintainers only:

1. Freeze at a Gate milestone (results freeze = Gate 3).
2. Move `[Unreleased]` → version section in `CHANGELOG.md`.
3. PR `dev` → `main`, tag `vX.Y.Z`, push the tag.
4. Announce in the team channel with the evaluation summary.
