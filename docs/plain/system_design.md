# IntentGate System Design — Plain English

> **See also:** [`docs/blueprint.md`](../../docs/blueprint.md) (full design, Sec 0–18) · [`roadmap.md`](../../roadmap.md) (progress tracker) · [`docs/experiments/README.md`](../experiments/README.md) (experiment index)

---

## The Problem

LLM agents today don't just chat — they act. They send emails, transfer money, write files, run code, search the web. And they're vulnerable:

- **Indirect injection:** A malicious web page or email tricks the agent into doing something the user never asked for
- **Tool poisoning:** An attacker registers a tool that looks useful but does something harmful
- **Drift:** Over a long conversation, the agent's actions slowly diverge from the original intent

Benchmarks prove this is real: InjecAgent shows 24–47% attack success rates (GPT-4), MCPTox shows up to 72.8%. Yet existing defenses are either single-vector filters or require hand-writing formal code contracts for every tool (ToolGate — 145 manual contracts in this project alone).

---

## The Big Idea

Instead of hand-authoring contracts, **ask a language model to extract the intent once**, then **score every proposed tool call against it**.

Here's the core insight: if you give a person a simple, legitimate request ("book me a flight to Paris"), you can tell immediately when someone tries to inject a side task ("and also drain your bank account"). The gate does the same thing — but with embeddings and rules.

```
User: "Book a flight to Paris"
         |
         v
[Parser] → IntentContract {
  goals: ["book flight"],
  tools: ["search", "book"],
  limits: {financial: "disallow", send: "self-only", code_exec: "disallow", ...}
}
         |
         v  (embedded ONCE)
┌─────────────────────────────────────────────────────┐
│                 GateMiddleware                      │
│               (every tool call passes through here)  │
│                                                     │
│  Agent proposes: SpokeoSearchPeople(email="x@x.com")│
│  ┌─── Check 1: Sematic score S_sem = cosine(       │
│  │    contract_embedding, call_embedding)           │
│  ├─── Check 2: Rule check S_rule = 1.0 or 0.0        │
│  │    (hard veto: e.g., code_exec when disallowed)  │
│  └─── Final: S = 0.7 * S_sem + 0.3 * S_rule          │
│        if S >= 0.75: allow                           │
│        if S >= 0.65: escalate (block in benchmark)  │
│        else: block                                   │
└─────────────────────────────────────────────────────┘
```

---

## How It Works — Step by Step

### Step 1: Parse (One Time, Before Anything Loads)

File: `src/intent_gate/parser/parser.py`  
Docs: `docs/blueprint.md:Sec 5 Comp 0`, `docs/experiments/02_parser_schema.md`

The user's very first request is sent to an LLM (GPT-4o-mini, temperature 0) that converts it into a structured **IntentContract**:

```json
{
  "goals": ["book a flight to Paris"],
  "expected_tool_categories": ["search", "book"],
  "permitted_data_access": [],
  "side_effect_limits": {
    "financial": "disallow",
    "external_send": "self-only",
    "file_write": "disallow",
    "code_exec": "disallow",
    "system_change": "disallow"
  }
}
```

**Critical ordering invariant:** This parse happens *before* the agent loads tool definitions or any attacker content. See `harness/common.py:OrderingGuard` — there's a test that panics if violated.

If the LLM fails (bad API key, weird output), the parser falls back to a **heuristic** (keyword matching) and never raises. Fail-closed: when in doubt, `disallow`.

### Step 2: Score Every Tool Call

File: `src/intent_gate/scoring/scorer.py` + `src/intent_gate/scoring/rules.py` + `src/intent_gate/scoring/embeddings.py`

Every proposed tool call passes through a two-part scoring function:

**Part A — Semantic (S_sem):** What does it mean?
- The contract text is embedded once: `embed(contract_text)` → stored as `contract_vec`
- Each tool call is embedded: `embed(call.naturalized())` → e.g., "call tool SpokeoSearchPeople with email=x@x.com"
- `S_sem = (cosine_similarity + 1) / 2` → maps to [0, 1]. 1 = very similar to intent, 0 = totally unrelated.

**Part B — Rules (S_rule):** Hard constraints that can't be gamed by wording.
- If the contract says `code_exec: "disallow"` and the call is `run_shell("rm -rf /")` → `S_rule = 0.0` (hard veto, forces `S = 0.0` regardless of how well-worded)
- Same logic for financial tools, file writes, system config changes, shell injection patterns
- If no rule fires → `S_rule = 1.0` (passes)

**Final score:** `S = alpha * S_sem + (1 - alpha) * S_rule`  
Default: `alpha = 0.7` (semantics lead, rules are veto)

### Step 3: Decide (Allow / Block / Escalate)

File: `src/intent_gate/gate/decisions.py`

```
score S
  │
  ├── S >= 0.75         → ALLOW (call matches intent)
  ├── S >= 0.75 - 0.10  → ESCALATE (close call — user should review)
  └── S < 0.65          → BLOCK (clearly outside intent)
```

The `delta = 0.10` band creates an "escalate" zone rather than a hard allow/block cliff. In benchmark mode, escalate counts as block (conservative). In interactive mode, it prompts the user.

### Step 4: Middleware Enforces the Path

File: `src/intent_gate/gate/middleware.py`

```
AgentLoop.propose() → proposes ToolCall
    → GateMiddleware.execute(call)        ← THE ONLY ENTRY POINT
        → check(call)                     ← score + decide
        → if "allow":    executor(call)   ← actually run the tool
        → if "block":    "Blocked by intent gate..."
        → if "escalate": (benchmark: block / interactive: prompt user)
```

**No bypass.** There's a dedicated test (`tests/test_no_bypass.py`) that verifies the executor can't be called directly. Every tool execution goes through the gate.

### Step 5: Trace Everything

File: `src/intent_gate/gate/trace.py`

Every gate decision is written to a JSONL file with:
- `S`, `S_sem`, `S_rule`, `decision`, `latency_ms`
- Model IDs, embedding hash, case_id, contract, tool name, source (agent/injected/poisoned)

This trace is **load-bearing** — it's what the threshold sweep, breakdowns, and error taxonomy are computed from.

---

## Three Baselines Compared

| Baseline | How it gates | Contracts needed | How it scored |
|---|---|---|---|
| **B1 — Unprotected** | No gate at all. Agent can call anything. | 0 | The vulnerability floor |
| **B2 — ToolGate** | Per-tool Hoare contracts `{P}T{Q}` + symbolic world-state. Pre/post checks. | 145 (hand-written) | Statistically **identical** to B1 (p = 1.0 / 0.33) |
| **Ours** | Single intent contract + embedding similarity + hard rules | **0** (auto-derived) | 19% → 0.7% ASR (InjecAgent), 20.7% → 10.7% (MCPTox) |

**Phase 6 backbone validation (E18):**
- **Qwen3.5:4b (local Ollama):** ASR 27.1% → 2.1% (92.7% reduction), 24 blocks, 0 false positives
- **gpt-6-luna:** Excluded — produces prose-only output (no ReAct `Action:` markers), 0 tool calls → gate can't fire. Documented as backbone-incompatibility, not gate deficit.

Key insight about B2: even with 145 hand-written contracts and 100% InjecAgent coverage, it performs no better than no gate at all. That's because Hoare contracts can't see **new tools** an attacker registers, or **poisoned registrations**. The intent gate compares meaning, not signatures.

---

## The Agent Loop (ReAct)

File: `src/intent_gate/agent/react.py`

```
Loop (max 15 steps):
  1. Agent sees: system prompt + user request + conversation history
  2. Agent outputs: "Action: <tool>\nAction Input: <json>"  OR  "Final Answer: <text>"
  3. Gate checks the proposed tool call
  4. If allowed → tool runs → observation feeds back to agent
  5. If blocked → "Blocked by intent gate" observation feeds back
  6. Repeat until Final Answer or step cap
```

The same prompt and tool block are used for B1, B2, and Ours — the only difference is what executes the tool call (raw executor vs ToolGateChecker vs GateMiddleware).

---

## Data Flow Summary

```
                    ┌─────────────────────────────────────┐
                    │  User Request (trusted, once)       │
                    └────────────┬────────────────────────┘
                                 │
                    ┌────────────▼────────────────────────┐
                    │  IntentParser (LLM, temp 0)           │
                    │  → IntentContract (frozen)            │
                    └────────────┬────────────────────────┘
                                 │  (embedded once)
                    ┌────────────▼────────────────────────┐
                    │  EmbeddingBackend                     │
                    │  contract_vec = embed(contract_text)  │
                    └────────────┬────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                     │                      │
   ┌──────▼──────┐       ┌──────▼──────┐       ┌───────▼───────┐
   │   B1 Loop   │       │  ToolGate   │       │  Ours Loop    │
   │ (no gate)   │       │  (B2)        │       │ (GateMiddleware)│
   │ direct exec │       │ Hoare check  │       │ S = .7·S_sem  │
   │             │       │ + world-state│       │  + .3·S_rule  │
   └─────────────┘       └──────────────┘       └───────┬───────┘
                                        │ check+escalate+trace │
                                        └────────────┬────────┘
                                                     │
                                        ┌────────────▼────────┐
                                        │  JSON trace: S,     │
                                        │  decision, latency  │
                                        └─────────────────────┘
```

---

## Key Design Properties

| Property | How it's enforced | Why it matters |
|---|---|---|
| **No bypass** | `GateMiddleware.execute()` is the only path; `tests/test_no_bypass.py` | Can't accidentally skip the gate |
| **Fail-closed** | Missing contract fields default to `disallow`; parser never raises | Attacker can't crash the gate to get through |
| **Deterministic** | Seed 42, temperature 0, pinned model IDs, embedding hash in every trace | Results are reproducible |
| **Ordering invariant** | `OrderingGuard` + tests ensure parse happens before attacker content loads | Prevents injection into the parser itself |
| **Cache-friendly** | System prompt + few-shots are byte-identical every call; only user message varies | ~16% cost savings from automatic prompt caching |
| **Contract embedded once** | `contract_vec` cached in `GateMiddleware`; only the call is embedded per step | Fast scoring (p95 16–20ms) |
