# AgentSpec — Haoyu Wang, Christopher M. Poskitt, Jun Sun (ICSE 2026)

**Source:** ICSE 2026 (48th IEEE/ACM International Conference on Software Engineering),
April 12-18 2026, Rio de Janeiro. DOI `10.1145/3744916.3764546`, pp. 2938-2950.
ACM ISBN 979-8-4007-2025-3. Fetched 2026-10-24.

## What it is

AgentSpec is a lightweight domain-specific language for specifying and enforcing runtime
constraints on LLM agents. The authors describe it as the first framework to systematically
enforce customizable safety constraints on LLM agents at runtime.

## Mechanism

Each rule has five parts:
1. `rule` - keyword plus a unique identifier.
2. `trigger` - the event that activates the rule: before an action (e.g. a bank transfer), on a
   detected state change, or on task completion.
3. `check` - a conjunction of predicates (e.g. `!is_to_family_member`).
4. `enforce` - the action on trigger: user inspection, LLM self-reflection, or a predefined action.
5. `end` - closing keyword.

Rules may be authored manually or generated automatically by an LLM for user review and approval.
Implementation hooks into the agent's decision pipeline (LangChain primary; AutoGen and Apollo noted as
adaptable) and evaluates proposed actions before execution. Enforcement mechanisms: action
termination, user inspection, corrective invocation, and self-reflection.

## Evaluation

Three domains: code execution, embodied agents, and autonomous driving.
- Code agent: prevents unsafe execution in over 90% of cases.
- Embodied agents: eliminates all hazardous actions.
- Autonomous vehicles: 100% compliance.
- LLM-generated rules (OpenAI o1): precision 95.56%, recall 70.96% for embodied agents; identifies
  87.26% of risky code; prevents AV law-breaking in 5 of 8 scenarios.
- Overhead: milliseconds.

## Why it matters for this study

AgentSpec is a *constraint DSL* applied uniformly across a deployment, not a policy induced from a
single user request. Its trusted input, lifecycle, datasets, and metrics are not recoverable from the
fetched abstract alone. It is therefore contextual related work, and a full-text review is pending
before it can be cited as a baseline.

## Status

Reviewed only (source verified; full-text review pending). Not implemented in this repository.