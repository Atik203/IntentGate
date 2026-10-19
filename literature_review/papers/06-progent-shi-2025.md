# Progent: Securing AI Agents with Privilege Control

Verified 2026-10-18. Source version: arXiv:2504.11703v3, revised 2026-05-14.
The first submission was in 2025. Citation key: `shi2025progent`.

Progent derives symbolic permissions from the user task and checks tool
names and arguments. Its updater uses runtime information. An SMT check
separates narrowing from expansion, with approval for expansion.
The source is the [authors' v3 paper](https://arxiv.org/html/2504.11703v3).
The [released artifact](https://github.com/sunblaze-ucb/progent) includes
AgentDojo and ASB experiment adapters plus MCP integration.

IntentGate instead freezes a request contract and uses embedding scores
with deterministic vetoes. Both systems derive task policies automatically.
This study has not measured Progent's authoring cost on InjecAgent or MCPTox.
A claim of mandatory manual policies or silent policy expansion is not justified
by the inspected v3 method. E27 is a positional comparison with no benchmark port.
