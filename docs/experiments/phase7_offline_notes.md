# E29 and E30 — offline Phase 7 evidence

## At a glance

Both studies read the frozen Phase 5 traces. They execute no tools, make no LLM
calls, and leave `results/phase5/` unchanged. Embedding inference in E29 uses real
CPU MPNet weights, with an immutable revision and a probe digest in its report.

## Goal

E29 measures whether a threshold selected on one injection setting transfers to
the other after changing the embedding model. E30 checks whether a conformal
score interval provides a useful alternative to a chosen escalation width.

## Setup

E29 uses all 722 proposed calls in the four InjecAgent full-gate trace files:
438 attacker-tool calls, 281 user-tool calls, and 3 other calls. Labels come from
the pinned InjecAgent case metadata. A user-tool label means tool-name agreement,
not verified task completion or correct parameters. Other calls are excluded
from the two label-specific rates.

There are only 17 distinct trusted user requests. Their SHA256 groups are split
once, using seed 42, into 11 calibration and 6 heldout groups. Every variant of
the same request stays on the same side across both splits and settings. This
avoids tuning on a base case and testing on its enhanced copy. Thresholds are
selected separately for cached MiniLM and MPNet, in each transfer direction.
The grid is 0.00 through 1.00 in steps of 0.01. The objective minimizes attacker
call pass rate subject to user-call blocking at most 10% on calibration calls;
ties choose the lowest threshold. Hard vetoes remain vetoes. The calibration
constraint has no guarantee on the heldout population.

MPNet uses the existing naturalization and contract text, cosine mapped to
`[0,1]`, and the frozen fusion coefficient `alpha=0.7`. Frozen rule components
and hard-veto flags are reused. The model is
`sentence-transformers/all-mpnet-base-v2`, revision
`e8c3b32edf5434bc2275fc9bab85f82640a19130`. Its model card documents
768-dimensional embeddings and a default limit of 384 word pieces.
[Source: the model author's card](https://huggingface.co/sentence-transformers/all-mpnet-base-v2).

E30 uses all 2,013 full-gate calls from InjecAgent and MCPTox, grouped into 408
distinct trusted user requests. Group nonconformity is the maximum
`abs(S - tau)` among that request's calls, with historical `tau=0.75` held fixed.
The primary random split uses seed 42 and 204 calibration groups / 204 heldout
groups. All repeated requests, including base/enhanced pairs, stay together.
At `alpha=0.1`, the conformal radius is the
`ceil((n+1)*(1-alpha))` order statistic. If this rank is `n+1`, the known score
support `[0,1]` requires a full-support interval; clipping the rank to the sample
maximum would lose the finite-sample coverage claim. The lower marginal bound
applies to exchangeable calibration and future groups with an independently
fixed center; ties can increase coverage.
[Method source: Angelopoulos and Bates](https://arxiv.org/abs/2107.07511).

## Results

E29's transfer table is in `results/phase7/e29_embedding_transfer/report.json`.
Both transferred and fixed `tau=0.75` metrics are reported on the same heldout
calls. These are proposed-call pass/block rates, not counterfactual attack
success rates from a new agent run.

E30 calibrates `delta=0.75`, giving interval `[0,1]`. All 204 heldout request
groups are covered, including all 1,101 of their calls. The heuristic symmetric
radius 0.1 covers 43.14% of these heldout groups. The calibrated interval also
covers 100% of heldout groups in all 100 deterministic sensitivity splits.
These repeated splits are dependent checks, not independent replications.

The conformal interval is vacuous: its high coverage results from covering the
entire score support. It supplies no useful escalation width on this mixed
population and no bound on attack success. E30 therefore completes the
calibration experiment with a negative practical result. The system continues
to use its existing escalation rule, `tau-delta <= S < tau`.

## Artifacts

- `scripts/e29_embedding_transfer.py`: real embedding swap, disjoint-group
  threshold selection, and both transfer directions.
- `results/phase7/e29_embedding_transfer/report.json`: transfer metrics, immutable
  model revision, package versions, and input hashes.
- `results/phase7/e29_embedding_transfer/rescored_calls.jsonl`: every rescored
  call, frozen score, label, grouping key, and hard-veto flag.
- `scripts/e30_conformal_calibration.py`: grouped heldout interval evaluation.
- `results/phase7/e30_conformal_band/report.json`: primary result, 100 split
  sensitivities, source hashes, and method assumptions.
- `results/phase7/e30_conformal_band/heldout_groups.jsonl`: primary heldout group
  membership and coverage indicators.
- `tests/test_stats.py` and `tests/test_phase7_offline.py`: finite-sample edge
  cases, support handling, heldout grouping, and threshold/veto semantics.

Reproduce with the project environment:

```powershell
python scripts/e29_embedding_transfer.py
python scripts/e30_conformal_calibration.py
```

The first command downloads the pinned public MPNet model if it is absent.
Both scripts restrict outputs to `results/phase7/`. Input hashes and benchmark
pins from `configs/benchmark_versions.yaml` are included in each report.

## Limitations

Frozen gated traces condition on calls the historical agent happened to
propose. Changed decisions could produce different later calls; neither study
recreates those continuations. E29's independent task count is 17 and its
heldout utility constraint can fail under setting or request shift. Parameter
correctness is not labeled. MPNet and MiniLM can truncate differently.

E30's benchmark groups are a heterogeneous census, so random splitting does
not establish exchangeability for deployment or an adaptive attacker. The
historical threshold was selected earlier on related benchmark evidence; the
mathematical statement treats it as fixed. Score-interval coverage is not
label coverage, decision correctness, or safety risk control. A symmetric
diagnostic interval must not be substituted for the production gate's
asymmetric escalation rule without a separate policy evaluation.

## Supervisor Q&A

**Does a stronger encoder eliminate calibration?** The experiment selects
thresholds on calibration groups and measures them unchanged on heldout groups
in the opposite setting. A new encoder requires its own calibration, even
when the fusion formula is unchanged.

**Does 100% conformal coverage prove the gate is safe?** No. The covered
quantity is score dispersion, and the interval covers the whole score support.
The result exposes the limitation of this proposed calibration target.

**Were frozen results changed?** No. All new scores and reports are written to
`results/phase7/`; their inputs are identified by SHA256 hashes.
