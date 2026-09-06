# AGENTS.md — IntentGate

Instructions for AI coding agents (opencode, Claude Code, Cursor, etc.) working in this repo.

## Project overview

IntentGate = thesis project. A model-agnostic **middleware action gate** for tool-using LLM agents: it derives an *intent contract* from the user's original request (once, before any attacker content), scores every proposed `tool_call` against it (embedding similarity + hard rule veto), and decides `allow / block / escalate`.

- **Blueprint (single source of truth):** `blueprint.md` — design Sec 0–18
- **Status tracker:** `roadmap.md` — Phases 0–8, Gates 0–3, success criteria. **Update its checkboxes in the same commit that completes a task.**
- **Setup for humans:** `setup.md`

## Repo layout

```
src/intent_gate/            # package (src layout)
  parser/                   # Comp 0: trusted once-per-session intent parser
  scoring/                  # embeddings, rules (hard veto), scorer (S = alpha*sem + (1-alpha)*rule)
  gate/                     # middleware (allow/block/escalate), decisions, JSONL trace
  agent/                    # LLM client, ToolRegistry, ReAct loop
  baselines/toolgate/       # B2: Hoare-contract checker, world_state, contracts
  eval/                     # metrics, threshold sweep, ablations, stats (bootstrap/McNemar)
harness/                    # run_injecagent.py, run_mcptox.py, compare_b2.py, common.py
scripts/                    # pilot_score_dist.py, check_parser.py, clone_benchmarks.ps1
configs/                    # intent_schema.json, parser_fewshots.json, thresholds.yaml, models.yaml
tests/                      # pytest; fixtures/ has labeled hijack+legit cases
data/  results/             # gitignored (benchmarks, JSONL traces)
```

## Commands (Windows/PowerShell, pwsh)

```powershell
.venv\Scripts\Activate.ps1          # activate venv
pip install -e ".[dev]"             # install (first run downloads torch - slow)
pytest -q                           # run tests (expect 26+ passing)
python scripts/check_parser.py      # parser spot-check (offline)
python scripts/pilot_score_dist.py  # scorer pilot (offline)
powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1
python harness/run_injecagent.py --cases <path> --gate ours --threshold 0.6
```

- Lint: `ruff check .` (ruff configured in pyproject; not required to run every change, but keep lines <= 100).
- There is no Makefile/CI config; keep it venv+pip+pytest only.

## Code conventions

1. **No comments unless asked.** Docstrings OK (they document design decisions tied to blueprint sections).
2. **Everything typed.** Dataclasses in `types.py` are the I/O contract: `ToolCall`, `IntentContract`, `GateResult`.
3. **Fail-closed.** Missing/unknown contract fields default to `disallow` for high-risk side effects (`schema.py` `FAIL_CLOSED_LIMITS`).
4. **Log every gate call.** `gate/trace.py` writes JSONL (`S`, `S_sem`, `S_rule`, decision, latency) — this is load-bearing for threshold sweeps; never remove logging.
5. **No bypass.** All tool execution must go through `GateMiddleware.execute()`. Any new executor path must keep the no-bypass test green (`tests/test_no_bypass.py`).
6. **Ordering invariant.** Intent parsing happens *before* tool definitions/attacker content load (`harness/common.py` `OrderingGuard`). Never pass tool outputs to the parser.
7. **Same agent prompt across B1/B2/ours.** Only the middleware differs; measured delta = gate effect.
8. **Deterministic.** Seed everything, `temperature=0` for parser/agent, pin model IDs, log hashes (embedding model, benchmark commits) in every result.
9. **Scope discipline.** B2 contracts only for the *evaluated tool subset* (not all 353 MCPTox tools). Missing contract = `no_contract` counter, never silently allowed.
10. **Blueprint-faithful naming.** Keep blueprint terms: `S_sem`, `S_rule`, `tau`, `delta`, `escalate`, `Gate N` milestones.

## LLM model notes + cache-hit guidance

Backbones used for agent/parser (config `configs/models.yaml`, override via `.env`): GPT-4o-mini (default), DeepSeek V4, MiMo 2.5, Muse Spark, Qwen/Llama via OpenAI-compatible endpoints.

To maximize context cache hits (DeepSeek context caching, OpenAI automatic prompt caching, vLLM prefix caching for local MiMo/Muse Spark):

1. **Stable prefix, dynamic suffix.** System prompt + few-shot examples first and byte-identical every call; only the trailing user message changes. Do not reorder or reword the system prompt between steps.
2. **Cache the intent contract, not the prompt.** The contract is parsed once per session and frozen; embed it once and reuse the embedding (never re-embed per call).
3. **Don't inject contract text into the agent prompt.** It stays out-of-band (gate only) — avoids prompt-injecting the gate and keeps the agent prompt cacheable.
4. **Pin model IDs.** Cache keys include the model name; switching `gpt-4o-mini` → `deepseek-v4` mid-run destroys cache and invalidates comparability. Log `model_id` per run.
5. **Keep tool definitions stable within a run.** They sit in the agent prompt prefix; reordering them (e.g., poisoned defs loaded per case) is expected across cases but must be identical for all baselines on the same case.
6. **Batch embeddings** (one `encode([...])` call per step, not per string) and reuse `EmbeddingBackend` instance — model load is the expensive part.
7. **Repair retry only on parse failure.** The retry re-sends the same messages (cache still hits); the fallback `minimal_contract` needs no LLM call at all.
8. **Local models (MiMo 2.5, Muse Spark via vLLM):** keep `temperature=0`, `max_steps=15` (step cap), and use a single chat template string for the whole run so vLLM prefix cache stays valid.

## Workflow

- Blueprint (`blueprint.md`) is the design source of truth; roadmap (`roadmap.md`) is the status source. If they conflict, flag it — don't silently pick one.
- Check the roadmap before starting work: a `[ ]` item in the current phase is the next thing to do. Mark `[~]` while working, `[x]` when done + tested.
- Before touching `src/` or `harness/`, run `pytest -q` and keep it green.
- Do not commit `.env`, `data/raw/`, `results/*.jsonl`, `.venv/`, `*.egg-info/` (gitignore already covers these).
- Security-relevant code paths (parser ordering, no-bypass, veto logic) have dedicated tests — add/extend them with any change.
