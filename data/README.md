# Benchmark data (`data/raw/`) — one-command setup

`data/raw/` holds the four benchmark suites IntentGate evaluates against. It is **gitignored**
because it is ~440 MB of third-party code and recorded agent responses. Nothing here is
committed — you fetch it locally with one script.

**You do not need to re-run the benchmarks to start work.** `results/` is committed to git
deliberately, so every teammate starts from the same measured state. Pull the repo, run the
bootstrap below, and read `results/` for where the project stands.

## Quick start

From the repo root:

```powershell
.venv\Scripts\Activate.ps1
powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1
```

That is the whole setup. It reads the pinned versions from `configs/benchmark_versions.yaml`,
clones anything missing at exactly those commits, repairs anything that drifted, and leaves
`data/raw/` byte-identical to the state every published result was measured against.

## Flags

```powershell
# Health check only. Downloads nothing, exits 1 if anything is missing or drifted.
powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1 -VerifyOnly

# Rebuild one benchmark from scratch.
powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1 -Force -Only ToolGate

# Wipe and rebuild everything.
powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1 -Force
```

| Flag | Effect |
| --- | --- |
| `-VerifyOnly` | Check every clone against its pin. No network writes. Non-zero exit on any problem. |
| `-Force` | Delete and rebuild even when the clone already matches. |
| `-Only <name>` | Limit to one of `InjecAgent`, `ToolGate`, `MCPTox`, `AgentDojo`. |

`-VerifyOnly` is the fastest way to answer "is my data directory broken?" before blaming a
benchmark run. It is also safe to add to CI or a pre-commit hook.

## Expected contents

```
data/raw/
├── InjecAgent/   github.com/uiuc-kang-lab/InjecAgent   @ f19c9f2c
├── ToolGate/     github.com/OceannTwT/ToolGate         @ 976ad3f5
├── agentdojo/    github.com/ethz-spylab/agentdojo      @ 089ed468
└── mcptox/       AAAI26-7C02 snapshot, downloaded 2026-09-11
```

Roughly 6 MB, 0.1 MB, 414 MB and 20 MB respectively. `agentdojo` is a Phase 6 stretch target
and the harness never reads it in Phases 0–5, but it is fetched by default so a full setup
matches exactly.

### What the harness actually reads

| Path | Used by |
| --- | --- |
| `InjecAgent/data/tools.json` | `harness/run_injecagent.py` (tool definitions) |
| `InjecAgent/data/test_cases_{ds,dh}_{base,enhanced}.json` | `harness/run_injecagent.py`, `scripts/run_phase5.py` |
| `mcptox/response_all.json` | `harness/run_mcptox.py`, `harness/adapters/mcptox.py` |
| `ToolGate/toolgate/` | `src/intent_gate/baselines/toolgate/` (B2 reference, Phase 3) |

The script verifies each of these exists after cloning, so a truncated download fails loudly
instead of silently poisoning a run.

### Case schema notes

- **InjecAgent** — `data/test_cases_{ds,dh}_{base,enhanced}.json`. The injected attacker
  instruction is already embedded in the `Tool Response` field; `Attacker Tools` lists the
  hijack tool; canned attacker replies live in `attacker_simulated_responses.json`.
  1,054 unique cases × 2 settings = 2,108.
- **MCPTox** — `pure_tool.json` holds poisoned tool descriptions per server (45 servers,
  485 tools); `response_all.json` holds recorded agent responses (1,348 cases);
  `def_tool/` has 485 per-tool definition scripts.
- These are adversarial research artifacts. **Never run payloads outside the sandbox.**

## Why pins matter

The clones are shallow, but pinned to an exact commit — not to a branch tip. This matters:
evaluating against `main` would mean two teammates measuring against different benchmark
bytes depending on when they cloned, which invalidates every comparison in
`docs/experiments/`.

`configs/benchmark_versions.yaml` is the single source of truth. The script reads it rather
than hardcoding hashes, so the two can never disagree. If you bump a benchmark version, edit
that file, re-run the script with `-Force`, and cite the new hash in the results log
(blueprint Sec 8).

## Troubleshooting

**`git fetch <sha> failed (server may not permit fetch-by-SHA)`**
Pinned cloning asks the remote for one specific commit. GitHub supports this; some mirrors
and self-hosted servers do not. Either switch to the canonical GitHub URL or clone the
default branch and check out the pin manually:

```powershell
git clone https://github.com/uiuc-kang-lab/InjecAgent data/raw/InjecAgent
git -C data/raw/InjecAgent checkout f19c9f2c79a41046eb13c03c51a24c567a8ffa07
```

**`INCOMPLETE missing: ...` on MCPTox**
The snapshot ZIP nests its contents one directory deep on some downloads. The script detects
and flattens this automatically, so seeing this error means the upstream archive changed
shape — re-run with `-Force -Only MCPTox` and, if it persists, compare against the layout
recorded in `configs/benchmark_versions.yaml`.

**`DRIFT` on a clone you did not touch**
Something checked out a different commit — usually `git pull` inside `data/raw/`, which
treats the clone as an independent repo. Re-run the script without flags and it re-fetches
the pin. Treat `data/raw/` as read-only output of the script, not as working copies.

**MCPTox URL returns an error**
The snapshot is served from `anonymous.4open.science` and is a frozen mirror of an anonymous
submission. If it goes away the bytes are unrecoverable from that URL — check
`configs/benchmark_versions.yaml` for the recorded snapshot date and ask a teammate who
already has `data/raw/mcptox/` to copy it to you.

## Updating a benchmark version

1. Edit the `commit:` (or snapshot reference) in `configs/benchmark_versions.yaml`.
2. `powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1 -Force -Only <name>`
3. Re-run the benchmark and record the new hash in the results log and in
   `docs/experiments/`.
