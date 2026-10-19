# Phase 7 method formalism and evidence audit

At a glance: the Chapter 3 method draft is in
[`docs/thesis/chapter3_method.md`](../thesis/chapter3_method.md).
This is a writing and source-verification task. It creates no new evaluation
result and does not change frozen Phase 5 evidence.

## Goal

State the threshold-selection objective, the trust assumptions, and the
reference-monitor connection without claiming unmeasured guarantees.

## Setup

The draft follows `docs/prompt.md` and `docs/writing-guideline.md`.
Implementation details were checked against `scoring/scorer.py`,
`gate/middleware.py`, and the committed trace format.
The reviewed benchmark pins are InjecAgent
`f19c9f2c79a41046eb13c03c51a24c567a8ffa07` and the MCPTox snapshot downloaded
2026-09-11, as recorded in `configs/benchmark_versions.yaml`.

The source check was performed on 2026-10-18. No paper content was inferred
from a search title alone.

## Results

The Chapter 3 draft defines fused scores, hard veto, and the one-sided
`[tau-delta, tau)` interval. It states an ASR-minimization objective subject
to a measured clean-call blocking budget. The Neyman-Pearson connection is
an error-budget framing, not an optimality or finite-sample guarantee.
The historical Pareto sweep was not prospectively calibrated under that
procedure. Four assumption rows distinguish request trust, untrusted tool
content, frozen session scope, and backbone participation.

## Artifacts and integration pointers

The integration owner should add a pointer under blueprint Section 9:

> Method formalism: `docs/thesis/chapter3_method.md` states the empirical
> ASR-minimization objective subject to a clean-call blocking budget,
> documents the original pilot-based threshold selection, and lists the
> trust and session assumptions. Its reference-monitor framing concerns
> enforcement placement. No Neyman-Pearson optimality, global security
> guarantee, or multi-turn guarantee is claimed.

The method-formalism row in `07_phase7_pilots.md` can cite the Chapter 3 file.
The roadmap checkbox is satisfied after that pointer is integrated with the
Chapter 3 draft. The same integration should update CHANGELOG, README, and
the literature index as required by the repository's design-document rule.

The following verified references can be added centrally before copying
`docs/references.bib` to `IEEE-conference/references.bib`:

```bibtex
@article{neyman1933efficient,
  author = {Neyman, Jerzy and Pearson, Egon S.},
  title = {On the Problem of the Most Efficient Tests of Statistical Hypotheses},
  journal = {Philosophical Transactions of the Royal Society of London. Series A},
  volume = {231},
  pages = {289--337},
  year = {1933},
  doi = {10.1098/rsta.1933.0009}
}

@techreport{anderson1972security,
  author = {Anderson, James P.},
  title = {Computer Security Technology Planning Study, Volume I},
  institution = {Electronic Systems Division, Air Force Systems Command},
  number = {ESD-TR-73-51, Vol. I},
  year = {1972},
  month = oct,
  url = {https://csrc.nist.gov/files/pubs/conference/1998/10/08/proceedings-of-the-21st-nissc-1998/final/docs/early-cs-papers/ande72a.pdf}
}
```

Neyman and Pearson's DOI is verified through its publisher-linked record.
The publisher rejects direct retrieval with HTTP 403 in this environment.
The original paper's indexed full-text copy is at
[stats.org.uk](https://stats.org.uk/statistical-inference/NeymanPearson1933.pdf).
Anderson's official NIST-hosted original report gives the report metadata
and reference-validation requirements in Section 3.2.2, printed pages 9-10.
It has no DOI identified in the original report.

## Limitations and corrections identified in existing reports

These findings refer to the report and scripts as read before integration.
The E27 and E31 sections and E31 runner now contain the corrections described
below. The original E31 JSON remains as a historical artifact, superseded by
`results/phase7/e31_contract_vs_semantic/e31_corrected_report.json`.

1. E24 compares prompt-defense ASR on a 50-case sample to the 0.7% frozen
   full-benchmark gate result. That comparison does not estimate a matched
   treatment effect. The current prompt report also infers a causal reason
   for Instructional Prevention's result without a separate causal test.
   Report sample counts and denominators, and use a gate run on the same
   slice before claiming superiority.

2. E31 matches `(case_id, tool_name)` and ignores arguments. A dictionary
   collapses repeated tools. It increments `total` for unmatched records,
   so 2,013 is not the number of decision comparisons. The current decision
   counts sum to 1,838. Its `veto_saves` condition is `S_rule == 1`, which
   indicates passing rules, and the aggregate adds those counts twice.
   The 322/32 decision flips have no benign/attack labels in that script.
   They cannot be called legitimate over-blocks or caught attacks without
   matching arguments and attaching ground truth. On matched full-gate
   calls, a same-call counterfactual replay is a clearer component test.

3. E23's user-tool-allowed rate measures execution of a designated user
   tool. It is not end-to-end task completion. The benign gate condition's
   clean-call blocking rate is direct utility evidence and should retain
   its observed denominator. Low valid-output counts limit any broad
   utility claim.

4. E27's Progent table needs a pinned source version. The current
   [arXiv v3](https://arxiv.org/abs/2504.11703v3), revised 2026-05-14,
   automatically generates a policy from the user task and uses an SMT
   solver for policy updates. Narrowing applies automatically, while
   expansion needs approval. The existing unqualified claim that its
   update model can silently widen the allowlist conflicts with v3.
   A port can be scoped out because of adapter and evaluation differences.
   Mandatory manual per-tool authoring and measured setup counts on this
   repository's tools should not be asserted without supporting evidence.
   The v3 author list has seven authors: Tianneng Shi, Jingxuan He, Zhun
   Wang, Hongwei Li, Linyu Wu, Wenbo Guo, and Dawn Song.

The blueprint describes raw cosine similarity, while the current scorer
uses `(cosine + 1) / 2`. The Chapter 3 draft states the implementation's
formula. This normalization matters for threshold transfer and should be
made explicit in the blueprint.

## Supervisor Q&A

Q: Does the new formulation prove that the frozen threshold meets an FPR bound?

A: No. It defines the objective for selecting a threshold. The historical
threshold came from a pilot Pareto tradeoff. A population error bound needs
its own calibration assumptions and held-out evidence.

Q: Does the gate qualify as a verified reference monitor?

A: The execution wrapper follows the mediation placement. Python tests do
not prove resistance to arbitrary process tampering or complete semantic
correctness of the learned policy.

Q: Does an adaptive score search establish end-to-end adaptive ASR?

A: A score-query search tests the gate on crafted calls. A live attacker
success rate also requires the attacked agent and the benchmark evaluator.
The final E26 report must identify which setting each result measures.
