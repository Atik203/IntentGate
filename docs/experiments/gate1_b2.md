# Gate 1 — ToolGate B2 contract coverage + validation (fallback)

**Date:** 2026-09-16 · **Purpose:** close Phase 3 with a frozen B2 contract set, an honest
coverage number, and a documented validation fallback (blueprint Sec 10/13, roadmap Phase 3).

## Setup

| Item | Value |
|---|---|
| Contracts | `src/intent_gate/baselines/toolgate/contracts.py` — manual Appendix-G-style pre/post/effect |
| Naming | harness `ToolCall` names `<Toolkit><Tool>` (e.g. `GmailSendEmail`, `BankManagerTransferFunds`) |
| World-state | `balance`, `files`, `permissions`, per-tool recorded effects (`tool_states`) + rollback on post violation |
| Evaluated universe | InjecAgent dh/ds base+enhanced (2,108 cases; user + attacker tools) |
| Frozen artifact | `configs/b2_coverage.json` |
| Coverage report | `python scripts/freeze_b2_coverage.py` |
| Replay report | `python harness/compare_b2.py --cases <case files> --replay results/injecagent_ours/*.jsonl` |

## Coverage — frozen 2026-09-16

| Metric | Value |
|---|---|
| Evaluated tools (InjecAgent universe) | 79 |
| Contracted tools | 79 |
| **Coverage** | **100.0%** |
| Missing contracts | none |
| Extra contracts (MCPTox pilot) | `transfer_money`, `read_file` |
| Total contracts | 81 |

Contract families: 43 read-only shape checks (required parameters only), 6 balance-debit money
tools (`BankManager*`, `VenmoWithdrawMoney`, `BinanceWithdraw`), 2 positive-amount order tools
(`BinanceDeposit`, `BinancePlaceOrder`), 4 file-presence/removal tools (`Dropbox*`,
`SpokeoDownloadPublicRecord`, `EpicFHIRDownloadFiles`, `GitHubDeleteRepository`), 24 recorded
side-effect tools (send/share/unlock/dispatch/policy/profile/schedule). Every contract pairs a
pre condition with a post condition; effects mutate symbolic state and are rolled back when the
post check fails.

## Validation — ToolBench fallback

ToolBench/MCP-Universe is not cloned, so the blueprint Sec 10 risk fallback applies: validate B2
on an InjecAgent sample with manual contract review instead of the ToolBench fidelity subset.

1. **Manual review** — all 79 contracts authored against the official InjecAgent `tools.json`
   parameter schemas (required vs optional) and reviewed against Appendix-G-style state checks.
2. **Recorded-call replay** — the 20-case B1 run's recorded `tool_calls`
   (`results/injecagent_ours/`) were replayed through the checker:
   4 calls, 0 pre violations, 0 post violations, 0 `no_contract`. These calls were shape-valid
   and state-consistent, so replay validates contract mechanics, not adversarial blocking power.
3. **Adversarial comparison** is Phase 4–5 work: B2 must run inside the same agent loop as B1 and
   ours (Gate 2) before any ASR/FPR claim is made.

## Divergence from ToolGate paper behavior (honest notes)

- Translated from the paper's described Hoare mechanism (Sec 5/Appendix G); the authors' private
  code is not public, so this is a minimal reimplementation, not bit-identical.
- Per-case world-state seeding is **not yet wired** (Gate 2). Until then `balance=0` and
  `files=empty` make state preconditions fail-closed, which can over-block legitimate calls; this
  will show up in FPR during Phase 5 and must be reported, not hidden.
- Postconditions currently verify recorded state effects and result presence; checks against rich
  returned payloads need the real executor wiring at Gate 2.
- `no_contract` is allow-with-flag (blueprint Sec 10 risk row), so out-of-universe tools stay
  visible in the report instead of being silently blocked or allowed.
- MCPTox subset contracts are still pending (only the two pilot contracts exist); coverage on
  MCPTox is not claimed by this freeze.

## Artifacts

- `configs/b2_coverage.json` — frozen coverage numbers
- `results/comparison_b2.json` — coverage + replay report (gitignored)
- `tests/test_toolgate_baseline.py` — 11 tests (naming, pre/post, rollback, coverage, replay universe)
