# 03 — B2 ToolGate baseline: contracts, coverage & validation (E7)

> **Status: COMPLETE (2026-09-16) · Gate 1 = PASS (fallback validation).** B2 is the paper's
> defining comparison: the closest published gate (ToolGate, arXiv 2601.04688) reimplemented
> faithfully enough to run adversarially on the same cases as ours.

| ID | Experiment | Scope | Headline result | Artifacts |
|---|---|---|---|---|
| E7 | B2 contracts + coverage freeze + gated B2 runs | InjecAgent 79 tools; MCPTox 801-tool registered snapshot | Coverage: **InjecAgent 79/79 (100%)**; **MCPTox 65 contracts (8.1% distinct / 37.2% availability-weighted)**; gated B2 blocks only the out-of-scope `write_file` on MCPTox | `configs/b2_coverage.json`, `results/gated/toolgate_*.json` |

Downstream: `04_gate2_gated_eval.md` (E8 compares B1 vs ours vs B2 side by side).

---

## What B2 is

A minimal, faithful reimplementation of ToolGate's mechanism (blueprint Sec 5 Comp 3 /
Appendix G): per-tool Hoare-style `{pre}T{post}` contracts over a symbolic world-state. Same gate
placement as ours, but the policy source is **manual contracts** instead of an auto-derived intent
contract — that difference is the thesis comparison.

| Item | Value |
|---|---|
| Contracts | `contracts.py` (InjecAgent, keyed `<Toolkit><Tool>`) + `mcptox_contracts.py` (snapshot tool names) |
| World-state | `balance`, `files`, `directories`, `permissions`, recorded effects (`tool_states`); snapshot/rollback on post violation |
| State seeding | `world_state.seed_from_request` — paths/dirs named in the *trusted* request (best effort) |
| Freeze script | `scripts/freeze_b2_coverage.py` → `configs/b2_coverage.json` |
| Replay/coverage report | `python harness/compare_b2.py --cases <case files> --replay results/injecagent_ours/*.jsonl` |

## Coverage (frozen 2026-09-16)

| Benchmark | Universe | Contracted | Coverage |
|---|---|---|---|
| InjecAgent (dh/ds base+enhanced, 2,108 cases) | 79 tools | 79 | **100.0%** |
| MCPTox snapshot (1,348 cases) | 801 registered tools | 65 | **8.1% distinct / 37.2% availability-weighted** |

**InjecAgent families:** 43 read-only shape checks, 6 balance-debit money tools, 2 positive-amount
order tools, 4 file-presence/removal tools, 24 recorded side-effect tools.

**MCPTox families:** filesystem read/write (path-scoped), mail, GitHub, process/shell, DB/Prisma,
misc (65 contracts). The 736 uncontracted registered tools — **including every poisoned
registration** — are counted as `no_contract` (allow-with-flag): this is ToolGate's per-tool setup
cost made visible. Only the path-scoped file contracts have real blocking power on MCPTox; mail/
GitHub/DB contracts are effect-recording because the snapshot ships no environment state to check.

## Validation (Gate 1 fallback)

ToolBench/MCP-Universe is not cloned, so the blueprint Sec 10 fallback applies.

1. **Manual review** — InjecAgent contracts authored against the official `tools.json` schemas;
   MCPTox contracts against the per-server tool families in the snapshot prompts.
2. **Recorded-call replay** — the 20-case B1 run's recorded `tool_calls` replayed through the
   checker: 4 calls, 0 violations, 0 `no_contract` (mechanics only, not adversarial power).
3. **Adversarial comparison** — B2 runs in the same gated loop as ours (E8): InjecAgent 8/100 succ;
   MCPTox blocks 1 malicious call (the out-of-scope `write_file`), everything else uncontracted or
   state-less.

## Divergence from the ToolGate paper (honest notes)

- Translated from the paper's described Hoare mechanism; the authors' private code is not public,
  so this is a minimal reimplementation, not bit-identical.
- State seeding is best-effort from the trusted request; unseeded cases fall back to shape checks,
  so file contracts may pass operations the request never named.
- Postconditions verify recorded state effects and result presence; checks against rich returned
  payloads need real executor wiring.
- `no_contract` is allow-with-flag (blueprint Sec 10 risk row) — the coverage gap stays visible.
- **Registration-time tool poisoning (MCPTox's core threat) is invisible to per-tool contracts**:
  the poisoned tool is simply undocumented, and only argument-level checks (paths, amounts) can
  catch damage. Reported as a scope boundary in `04_gate2_gated_eval.md` (E10).

---

## Reproduce

```powershell
.venv\Scripts\Activate.ps1
python scripts/freeze_b2_coverage.py                                  # coverage freeze
python harness/run_injecagent.py --cases data/raw/InjecAgent/data/test_cases_dh_base.json --gate toolgate --limit 50 --seed 42 --report results/gated/toolgate_dh50.json
python harness/run_injecagent.py --cases data/raw/InjecAgent/data/test_cases_ds_base.json --gate toolgate --limit 50 --seed 42 --report results/gated/toolgate_ds50.json
python harness/run_mcptox.py --gate toolgate --limit 100 --seed 42 --report results/gated/toolgate_mcptox100.json
```

## Related files

- Code: `src/intent_gate/baselines/toolgate/` (`contracts.py`, `mcptox_contracts.py`,
  `checker.py`, `world_state.py`), `harness/gate_policy.py`
- Configs: `configs/b2_coverage.json`
- Scripts: `scripts/freeze_b2_coverage.py`, `harness/compare_b2.py`
- Tests: `tests/test_toolgate_baseline.py`, `tests/test_mcptox_contracts.py`,
  `tests/test_gate_policy.py`

## Limitations

- MCPTox coverage is low by construction (801-tool long tail); this is the setup-cost argument,
  not a quality claim about the reimplementation.
- ToolBench fidelity validation was skipped (blueprint fallback); divergence is documented above.
- Effect-recording contracts on non-file MCPTox families never block (no environment state).

## Supervisor Q&A

**Q: Is B2 a strawman?**
A: Its mechanism is faithfully implemented and its coverage is frozen and reported (100% on
InjecAgent). What limits it on MCPTox is structural — manual per-tool contracts cannot cover an
801-tool, attacker-registered toolset — and that is precisely the gap the thesis measures.

**Q: Why is MCPTox coverage only 8.1%?**
A: 801 distinct registered tools across 45 servers; we contracted the 65 that dominate usage
(37.2% availability-weighted). The long tail stays `no_contract` and is counted, not hidden.

**Q: Why does B2 block almost nothing on MCPTox?**
A: Malicious calls use poisoned/fake tools that per-tool contracts cannot know about, and the
snapshot ships no world-state for the effect-recording families. The one catch is a path-scope
violation (`write_file` → `~/.ssh/id_rsa`).

**Q: Did you measure B2's setup cost?**
A: Yes — 79 + 65 manual contracts (144 total), versus 0 for ours. This is the C2 setup-cost metric.

**Q: Could B2 do better with more contracts?**
A: Only where state exists to check (paths, balances). More mail/GitHub/DB contracts would record
effects but not block. Phase 5 includes an ablation with seeded file state as a sensitivity check.
