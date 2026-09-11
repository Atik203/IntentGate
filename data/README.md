# Benchmark clones + snapshots (gitignored)

Re-clone via `scripts/clone_benchmarks.ps1`. MCPTox is a ZIP snapshot:
`https://anonymous.4open.science/api/repo/AAAI26-7C02/zip` → extract to `data/raw/mcptox`.

**Pinned versions (recorded 2026-09-11): see `configs/benchmark_versions.yaml`.**
Every results log must cite the benchmark commit hash / snapshot date (blueprint Sec 8).

## Current contents

```
data/raw/
├── InjecAgent/          # github.com/uiuc-kang-lab/InjecAgent @ f19c9f2c
├── ToolGate/            # github.com/OceannTwT/ToolGate @ 976ad3f5 (B2 reference, Phase 3)
├── agentdojo/           # github.com/ethz-spylab/agentdojo @ 089ed468 (stretch, Phase 6)
└── mcptox/              # AAAI26-7C02 snapshot, downloaded 2026-09-11 (1,348 cases, 45 servers)
```

## Case schema quick notes

- InjecAgent: `data/test_cases_{ds,dh}_{base,enhanced}.json` — the injected attacker
  instruction is already embedded in the `Tool Response`; `Attacker Tools` lists the
  hijack tool; simulated attacker responses live in `attacker_simulated_responses.json`.
- MCPTox: `pure_tool.json` holds poisoned tool descriptions per server; `response_all.json`
  holds recorded agent responses; `def_tool/` has per-tool definition scripts.
- These are adversarial research artifacts — never run payloads outside the sandbox.
