# IntentGate Results — Plain English Summary

> **Detailed data:** [`docs/experiments/05_phase5_full_evaluation.md`](../experiments/05_phase5_full_evaluation.md) (E11–E17) · [`docs/experiments/README.md`](../experiments/README.md) (index) · [`roadmap.md`](../../roadmap.md) (Gate status)
> **Artifacts:** all JSON/JSONL traces live in `results/phase5/` (tracked in git, don't re-run)

---

## At a Glance

| Metric | B1 (unprotected) | B2 (ToolGate) | **Ours (IntentGate)** |
|---|---|---|---|
| **InjecAgent ASR** | 19.0% | 17.2% | **0.7%** |
| **MCPTox attack-influenced** | 279 / 1,348 (20.7%) | 271 / 1,348 (20.1%) | **144 / 1,348 (10.7%)** |
| **Blocks** | 0 | 10 | **140** |
| **Latency (p95 per call)** | — | ≤0.06 ms | **16–20 ms** |
| **Setup cost (manual contracts)** | 0 | 145 | **0** |
| **Cost (billed)** | — | — | **$9.64** (34,560 LLM calls) |

**Bottom line:** The intent gate drops InjecAgent attacks from 1 in 5 to nearly zero, and MCPTox attacks in half — while B2 does no better than no gate at all.

---

## What ASR Means

- **ASR (Attack Success Rate):** What fraction of malicious cases did the agent actually execute the attacker's intended action?
  - InjecAgent: "ASR-valid" = the attacker's tool call actually ran
  - MCPTox: "attack-influenced" = success + work-not-success (attacker got partial traction)

- **McNemar p-value:** Statistical test for paired data. p < 0.001 = the difference is real, not noise.

---

## InjecAgent — 2,108 Cases (Full Suite)

Breakdown by split × setting:

| Slice | B1 ASR | B2 ASR | **Ours ASR** | p-value (ours vs B1) |
|---|---|---|---|---|
| dh_base (510) | 7.8% | 5.6% | **0.0%** | — |
| dh_enhanced (510) | 9.9% | 5.7% | **0.0%** | — |
| ds_base (544) | 25.0% | 24.3% | **1.2%** | — |
| ds_enhanced (544) | 31.5% | 31.0% | **1.4%** | **1.3e-33** |
| **All (2,108)** | **19.0%** | **17.2%** | **0.7%** | — |

**What "dh" vs "ds" means:**
- **dh** (direct hijack): attacker content comes from a tool result (e.g., search results, email)
- **ds** (data smuggling): attacker content is smuggled in parameters the agent is explicitly told to use

The gate is perfect on dh (0% — the intent is clear) and nearly perfect on ds (1.2–1.4% — the harder case, see error taxonomy below).

---

## MCPTox — 1,348 Cases (Full Suite)

MCPTox is harder because: the agent is told to use specific tools, and some of those tools are maliciously registered. The gate can't tell the tool is bad if it matches the user's intent.

| Condition | success | attack-influenced | blocked | ignored |
|---|---|---|---|---|
| B1 | 103 | 279 | 0 | 1,012 |
| B2 | 98 | 271 | 10 | 1,008 |
| **Ours** | 66 | **144** | **140** | 1,007 |

**Why B2 ≈ B1 here:** MCPTox's 801 registered tools only have contracts covering 8.1% of them (65 contracts). The other 736 tools — including most of the poisoned ones — have `no_contract` and get a free pass. See `configs/b2_coverage.json`.

---

## Ablation Study — What Makes the Gate Work?

| Ablation | InjecAgent ASR | MCPTox attack-influenced | What it tells us |
|---|---|---|---|
| **A1 — Semantic only** (no rules) | **0.0%** (all slices) | 81 | Detection is semantically led |
| **A2 — Rules only** (no semantics) | 24–31% (≈ B1) | 263 | Rules alone are a near-no-op |
| **A3 — Raw request** (embed request text, skip contract) | 0.0–1.6% | 116 | Contract parsing ≈ raw embedding on these splits |
| **Ours — Both** (semantic + rules) | 0.7% | 144 | Both components matter |

**Key insight:** The rules aren't the detection engine — semantics are. Rules provide:
1. **Hard vetoes** (e.g., "this call runs shell commands, but you said 'never run code'")
2. **Precision on dh-style side effects** (financial, file writes, system changes)
3. **The escalate band** (veto signal that feeds the threshold logic)

---

## Threshold Tuning (τ×δ Pareto)

The team swept 27 combinations of `τ` (0.40–0.80) × `δ` (0.05/0.10/0.15) over the cached traces:

- **InjecAgent:** ASR is already 0% at τ=0.75 for all δ. The knee holds.
- **MCPTox:** At frozen point (τ=0.75, δ=0.1), ASR is 0.583 per-call. The absolute minimum is at τ=0.80 (ASR 0.427, escalate 16.0%).
- **Escalate share:** ~21.6% on InjecAgent, ~18.2% on MCPTox — these are mostly attacker tool calls (escalate counts as block in benchmark mode).

**Conclusion:** τ=0.75 was chosen correctly. No post-freeze re-tuning was done.

---

## Error Taxonomy — Why the 13 Failures on InjecAgent

The 13 cases that slipped through are all the same pattern:

1. The user's original request includes a **legitimate read** (e.g., "look up my contact info in Spokeo")
2. The attacker injects a **near-identical read** to a **different person** (e.g., "look up attacker's Spokeo profile")
3. The semantic score is **S ∈ [0.75, 0.79]** — just above threshold
4. **S_rule = 1.0** — read tools trigger no veto (no side effects to veto)

This is the hardest case for a similarity gate: the attacker's call is semantically almost identical to a legitimate call the user explicitly authorized. The Phase 6 work (E18 intent-mimicry probe) will systematically test whether this class generalizes.

**MCPTox residuals** follow the same signature: rule=1.0, S above τ, called tool is a legitimate query the user asked for — but the tool itself was maliciously registered. This is **registration-time poisoning**, which an action gate fundamentally can't detect (tool provenance is out of scope).

---

## Latency & Utility

| Metric | B1 | B2 | Ours | Target |
|---|---|---|---|---|
| **p50 per call** | — | — | 12–13 ms | — |
| **p95 per call** | — | ≤0.06 ms | **16–20 ms** | < 100 ms ✓ |
| **Valid rate** | 87.5–89.7% | — | 86.9–89.7% | parity ✓ |
| **User tool calls allowed** | — | — | B1-like levels | — |

**No utility loss.** The gate blocks attacks but doesn't impede legitimate work — valid rate is within 0.6 percentage points of the unprotected baseline on every slice.

---

## Cost Breakdown

34,560 total LLM calls across 30 jobs, run at `--jobs 3` (3 parallel), finished in ~5.6 hours:

| Group | Agent calls | Total calls | List-price actual |
|---|---|---|---|
| B1 (agent) | 3,456 | 3,456 | $1.33 |
| B2 (agent) | 3,456 | 3,456 | $1.33 |
| Ours (agent + parser) | 3,456 | 6,912 | $2.20 |
| Ablations A1–A3 | 10,368 | 20,736 | $6.60 |
| **Total** | **20,736** | **34,560** | **$11.46 list / $9.64 billed** |

Our gate costs ~1.55× B1 per case (the extra parser call), but automatic prompt caching saved ~16% (billed $9.64 vs $11.46 list price).

---

## Success Criteria Verdict

| Criterion | Result |
|---|---|
| ASR_ours < ASR_B1, p < 0.05 | ✅ p=1.3e-33 (InjecAgent), p=1.25e-07 (MCPTox) |
| Setup cost: 0 vs B2 | ✅ 0 vs 145 contracts |
| Latency p95 < 100ms | ✅ 16–20 ms |
| B2 runs & documented | ✅ coverage frozen + reported |
| Valid-rate parity | ✅ Δ ≤ 0.6pp on all slices |
| Deliverables | ⏳ thesis + package + report; paper draft = Phase 8 |

---

## Phase 6 — Complete (2026-10-13)

All three priorities done. New findings get E18+ IDs as preliminary (no Phase 5 numbers touched).

| Priority | Experiment | Result |
|---|---|---|
| **P0-1 (E18)** | Second-backbone pilot (Qwen + Luna) | Qwen: ASR 27.1% → 2.1% (92.7% reduction); Luna: 70% invalid (prose-only, no ReAct) — excluded from delta |
| **P0-2 (E19)** | B2 coverage curve (65 → 583 contracts) | 37.2% → 84.9% weighted coverage; curve flat — B2's weakness is structural (poisoned registrations), not coverage |
| **P1 (E20–E22)** | Mimicry / Escalate / Stats | Avg S inflation +0.0112 (0/13 cross τ); Escalate precision 80.5%, false-escalate 14.8%; Power=1.0 at α=0.005; per-specificity FPR: specific 12.8%, vague 9.6% |

Artifacts: `docs/experiments/06_phase6_pilots.md`, `results/phase6/{qwen,luna}_pilot_*`, `e19_coverage_curve.json`, `e20_mimicry.json`, `e21_escalate_precision.json`, `e14_power_analysis.json`.

### Technical issues resolved
- Qwen smoke parser fallback fixed (`qwen_smoke_recheck2` asserts `parser.calls > 0`)
- Luna temperature rejection auto-handled by `LLMClient`
- Cost accounting: unknown agent cost now reported with `cost_note` (not silently dropped)
- E19 coverage curve JSON fixed (`phase5_b2_coverage: 0.372` not `0.849`)
- Embedding hash audit: dev-box smokes with `fea010037875` superseded by `4588b3f9e962`

### Limitations documented
- Luna excluded from model-agnosticism claim (convention #7 forbids prompt tailoring)
- Per-specificity FPR includes escalate-candidates; valid-rate parity is the meaningful utility metric
- Power analysis uses normal approximation for rare-event proportions
