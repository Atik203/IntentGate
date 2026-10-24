# Task Shield — Feiran Jia et al. (ACL 2025)

**Source:** ACL 2025, Long Papers, pp. 29680-29697. DOI `10.18653/v1/2025.acl-long.1435`.
arXiv:2412.16682 (2024-12-21). Code available. Fetched 2026-10-24.

## What it is

Task Shield reframes agent security from preventing harmful actions to enforcing **task alignment**:
every instruction and tool call must contribute to user-specified goals. It is a test-time defense, not
a model change.

## Mechanism

Three components:
1. **Instruction extraction** - an LLM extracts all potentially actionable directives from each
   incoming message (nested or implicit), rewrites information-seeking queries as explicit
   instructions, and preserves task dependencies. User objectives are stored as a `User Task Set T_u`.
2. **Alignment check** - for each extracted instruction `e`, an LLM scores `s(e,t) in [0,1]` against
   every `t in T_u` via a `ContributesTo` predicate. Aggregate `S(e) = sum_t s(e,t)`; misaligned
   iff `S(e) = 0`. The fuzzy scale replaces a hard binary judgement.
3. **Feedback generation** - on misalignment, an alert, a risk explanation, and a reminder of current
   objectives are injected.

## Evaluation

AgentDojo (MIT license), GPT-4o and GPT-4o-mini, one trial per task. ASR 2.07% with 69.79% utility
under attack on GPT-4o; 2.23% ASR / 54.53% utility on GPT-4o-mini. Consistently outperforms baseline
defenses across the four task suites (TRAVEL, WORKSPACE, BANKING, SLACK).

## Limitations (from the paper)

- Relies on a powerful defender LLM for extraction and scoring; weak or adversarially probed models
  give false positives or false negatives.
- Adds an LLM call for every assistant response and tool output.
- Single model family (GPT) on one benchmark (AgentDojo); open-source backbones not tested.
- Proof-of-concept evidence, not an exhaustive evaluation.

## Why it matters for this study

Task Shield is the closest system on *task alignment* (semantic, not rule-based). It is evaluated on
AgentDojo only, with GPT-4o, so it is contextual related work. A direct numerical comparison would
require a faithful implementation run on this study's cases, tools, and prompts under this protocol
(see protocol section 4, baseline fairness).

## Status

Reviewed only (source verified; no local review file before this one). Not implemented in this
repository.