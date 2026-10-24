# MELON — Kaijie Zhu et al. (ICML 2025)

**Source:** arXiv:2502.05174 (v1 2025-02-07, last revised v4 2026-06-10); proceedings version at
`proceedings.mlr.press/v267/zhu25z.html`. Code: `github.com/kaijiezhu11/MELON`. Fetched 2026-10-24.

## What it is

MELON (Masked re-Execution and TooL comparisON) is an indirect-prompt-injection defense. It builds
on the observation that, under a successful attack, the agent's next action becomes less dependent on
the user task and more on the malicious task. It re-executes the agent's trajectory with the user
prompt masked (replaced by a task-neutral prompt `T_f`) and compares tool calls between the original
and masked executions: if the tool calls are similar, an attack is inferred.

## Mechanism

- Masking function `M(T_u, A_1:t, O_1:t) = (T_f, empty, consolidated tool outputs)`.
- Detection criterion: `sim(tools(A^o_{t+1}), tools(A^m_{t+1})) > theta`, comparing tool calls only
  (not full actions), because text responses can differ while tool calls stay identical under attack.
- A tool-call cache `H` records masked-run calls so a delayed attack (user task first, then malicious
  task) is still caught.
- Two few-shot samples guide the masked run toward focusing on embedded instructions rather than
  mimicking tool-call patterns.

## Evaluation

AgentDojo (MIT license). Outperforms SOTA defenses on both attack prevention and utility preservation;
MELON-Aug (combined with a prompt-augmentation defense) further improves results. Ablation study
validates the three key designs.

## Why it matters for this study

MELON is a re-execution defense: it needs a second full agent trajectory per step, so its cost profile
(an extra model pass per action) differs qualitatively from a pre-execution score gate. It is also
evaluated on AgentDojo only, not on InjecAgent or MCPTox. It is therefore contextual related work for
Phase 8, not a candidate for a same-protocol numerical comparison unless a faithful port is approved
(see protocol section 4, baseline fairness).

## Status

Reviewed only. Full feature-level depth pending. Not implemented in this repository.