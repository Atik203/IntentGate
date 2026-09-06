# Setup — IntentGate

How to install and run the project locally. Tested on Windows (PowerShell 7+); commands for macOS/Linux noted inline.

---

## 1. Prerequisites

- **Git** — https://git-scm.com
- **Python 3.11+** (3.12 works too) — https://www.python.org/downloads/
  - Windows: during install, tick **"Add Python to PATH"**
  - Verify: `python --version`
- No GPU required. The embedding model runs on CPU.

## 2. Clone the repo

```bash
git clone https://github.com/Atik203/IntentGate.git
cd IntentGate
```

## 3. Create virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
# PowerShell (Windows)
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

## 4. Install the package

```bash
pip install -e ".[dev]"
```

- `-e` = editable install (code changes are picked up without reinstall).
- `[dev]` = pytest and dev tools.
- First install downloads `torch` + `sentence-transformers` (~large) — can take several minutes. If it times out, run:

```bash
pip install -e . --no-deps
pip install numpy pyyaml pytest
```

The project still runs offline with this minimal set (embedding backend falls back to a deterministic hash embedding). Install the full deps later with a longer timeout for real embeddings.

## 5. Configure environment

```bash
# PowerShell: Copy-Item .env.example .env
# macOS/Linux: cp .env.example .env
```

Edit `.env` and fill in at least `OPENAI_API_KEY` (used for the agent + intent parser LLM calls).

## 6. Verify: run tests

```bash
pytest -q
```

Expected: `26 passed` (or more as phases progress).

## 7. Quick smoke test (no API key needed)

```bash
python scripts/check_parser.py      # spot-check intent parser on sample requests
python scripts/pilot_score_dist.py  # Week 1-2 scorer pilot (prints hijack vs legit S means)
```

Both run offline using the parser/embedding stand-ins.

## 8. Clone benchmark datasets (Week 1)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/clone_benchmarks.ps1
```

This clones InjecAgent, MCPTox snapshot, ToolGate, AgentDojo into `data/raw/` (gitignored). Record the exact commit hashes for reproducibility — they belong in every results log (blueprint Sec 8).

## 9. Run the harness

```bash
python harness/run_injecagent.py --cases data/raw/InjecAgent/cases.json --gate ours --threshold 0.6
python harness/run_mcptox.py --cases data/raw/mcptox/cases.json --snapshot v1
python harness/compare_b2.py --cases data/raw/InjecAgent/cases.json
```

(Paths depend on the benchmark repo layout; adjust after cloning.)

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `pip install` hangs / times out | It's downloading torch. Retry with a bigger timeout, or use `--no-deps` route in step 4. |
| `pytest` not found | Venv not activated, or install with `pip install -e ".[dev]"`. |
| `ModuleNotFoundError: intent_gate` | Run `pip install -e .` (or `--no-deps` + `numpy`/`pyyaml`) so the package is on the path. |
| No API key | Everything except real LLM calls works; parser/scorer fall back to offline stand-ins and tests stay green. |
| `.env` not read | Ensure `.env` exists in repo root (it is gitignored) and `python-dotenv` is installed. |

## Related docs

- `blueprint.md` — design (single source of truth)
- `roadmap.md` — phased tracker + current status
- `README.md` — project overview
