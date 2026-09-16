# Gate 1 — ToolGate B2 contract coverage + validation (fallback)

**Date:** 2026-09-16 · **Purpose:** close Phase 3 with a frozen B2 contract set, honest
coverage numbers for both benchmarks, and a documented validation fallback
(blueprint Sec 10/13, roadmap Phase 3).

## Setup

| Item | Value |
|---|---|
| Contracts | `contracts.py` (+ `mcptox_contracts.py`) — manual Appendix-G-style pre/post/effect |
| Naming | harness `ToolCall` names (`<Toolkit><Tool>` for InjecAgent; snapshot names for MCPTox) |
| World-state | `balance`, `files`, `directories`, `permissions`, recorded effects + rollback on post violation |
| State seeding | `world_state.seed_from_request` — paths/dirs named in the *trusted* request |
| Frozen artifact | `configs/b2_coverage.json` |
| Coverage report | `python scripts/freeze_b2_coverage.py` |
| Replay report | `python harness/compare_b2.py --cases <case files> --replay results/injecagent_ours/*.jsonl` |

## Coverage — frozen 2026-09-16

| Benchmark | Universe | Contracted | Coverage |
|---|---|---|---|
| InjecAgent (dh/ds, base+enhanced; 2,108 cases) | 79 tools | 79 | **100.0%** |
| MCPTox snapshot (1,348 cases) | 801 registered tools | 65 | **8.1% distinct / 37.2% availability-weighted** |

InjecAgent families: 43 read-only shape checks, 6 balance-debit money tools, 2 positive-amount
order tools, 4 file-presence/removal tools, 24 recorded side-effect tools. MCPTox families:
filesystem read/write (path-scoped), mail, GitHub, process/shell, DB/Prisma, misc tools
(65 contracts, `mcptox_contracts.py`). Effects mutate symbolic state and are rolled back when a
post check fails.

The MCPTox long tail (736 uncontracted registered tools, including every poisoned registration)
is counted as `no_contract` (allow-with-flag) — this is exactly ToolGate's per-tool setup cost
made visible. Only the path-scoped file contracts have real blocking power on this benchmark;
mail/GitHub/DB contracts are effect-recording because the snapshot ships no environment state
to check against.

## Validation — ToolBench fallback

ToolBench/MCP-Universe is not cloned, so the blueprint Sec 10 risk fallback applies: validate B2
on benchmark samples with manual contract review instead of the ToolBench fidelity subset.

1. **Manual review** — InjecAgent contracts authored against the official `tools.json` schemas;
   MCPTox contracts authored against the per-server tool families in the snapshot prompts.
2. **Recorded-call replay** — the 20-case B1 run's recorded `tool_calls`
   (`results/injecagent_ours/`) replayed through the checker: 4 calls, 0 violations, 0
   `no_contract` (mechanics check, not adversarial power).
3. **Adversarial comparison** — B2 now runs in the same gated loop as ours
   (`docs/experiments/gate2_integration.md`): InjecAgent 8/100 succ, MCPTox 1 malicious call
   blocked (the path-scope `write_file`), everything else uncontracted or state-less.

## Divergence from ToolGate paper behavior (honest notes)

- Translated from the paper's described Hoare mechanism (Sec 5/Appendix G); the authors' private
  code is not public, so this is a minimal reimplementation, not bit-identical.
- State seeding is best-effort from the trusted request: only paths named there (and "home
  folder") are known. Unseeded cases fall back to shape checks, so file contracts may pass
  out-of-scope operations the request never named. Phase 5 reports this as a limitation.
- Postconditions verify recorded state effects and result presence; checks against rich returned
  payloads need the real executor wiring at Gate 2.
- `no_contract` is allow-with-flag (blueprint Sec 10 risk row), so out-of-universe tools stay
  visible in reports instead of being silently blocked or allowed.
- Registration-time tool poisoning (MCPTox's core threat) is invisible to per-tool contracts:
  the poisoned tool is simply undocumented, and only the argument-level checks (file paths,
  amounts) can catch damage. This is reported as a scope boundary in
  `docs/experiments/gate2_errors.md`.

## Artifacts

- `configs/b2_coverage.json` — frozen coverage numbers for both benchmarks
- `results/comparison_b2.json`, `results/gated/toolgate_*.json` — coverage + run reports (gitignored)
- `tests/test_toolgate_baseline.py`, `tests/test_mcptox_contracts.py` — contract/coverage/seed tests
