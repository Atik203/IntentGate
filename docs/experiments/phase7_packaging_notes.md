# Phase 7 artifact packaging validation

## At a glance

The image definition, CPU dependency lock and automatic frozen-result verification are
implemented. The clean-container check passed in GitHub Actions run `39299936752`
(PR #44): the image built on `ubuntu-latest`, `pytest -q` passed inside the container, and
the offline reporter ran. Local Docker Desktop remains unavailable on the author's Windows
host.

## Goal

Provide a single image that checks the published artifacts before running the test suite
or an offline analysis command. Paid model evaluation remains an explicit command that
needs runtime credentials and benchmark clones.

## Setup

The image uses Python 3.11.11 on Debian Bookworm and the exact package versions in
`requirements-repro.txt`, including a CPU-only Torch wheel. These are the artifact
environment pins, rather than a reconstruction of the historical Phase 5 host.

The benchmark identifiers remain unchanged: InjecAgent
`f19c9f2c79a41046eb13c03c51a24c567a8ffa07`, ToolGate
`976ad3f5528f89e248cbdf55840347b445934155`, AgentDojo
`089ed468cf3ed0322acc66b0211f26d9d90dbf60`, and the MCPTox AAAI26-7C02 snapshot
downloaded on 2026-09-11. Full provenance is in `configs/benchmark_versions.yaml`.

```powershell
docker build --tag intentgate:phase7 .
docker run --rm intentgate:phase7 pytest -q
docker run --rm intentgate:phase7 python scripts/run_phase5.py --check --artifacts-only
docker run --rm intentgate:phase7 python scripts/report_phase5.py --dir results/phase5 --out /tmp/phase5_report.json
```

The entrypoint always runs `scripts/run_phase5.py --check --artifacts-only` first.
This mode derives case counts from `configs/benchmark_versions.yaml`, verifies frozen
settings/configuration/matrix, checks report consistency, and verifies every recorded
Phase 5 artifact hash. It loads no raw datasets, model weights or credentials. The
original `--check` command retains its dataset-dependent behavior.

The build copies only the project source, configuration, scripts, tests, published
results and documentation. `.dockerignore` excludes `.env`, raw benchmarks, local
environments, Git metadata and editor files. Runtime credentials are supplied with
`--env-file .env` only when an API experiment is deliberately requested. The published
Phase 5 outputs should never be mounted writable during new experiments.

To update the lock intentionally:

```powershell
uv pip compile requirements-repro.in --python-version 3.11 --python-platform x86_64-manylinux_2_28 --no-python-downloads --index https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match --default-index https://pypi.org/simple --emit-index-url --no-annotate --output-file requirements-repro.txt --no-header
```

## Results

- `pytest -q tests/test_phase5_freeze.py`: 8 passed.
- `python scripts/run_phase5.py --check --artifacts-only`: integrity check passed.
- `git diff --check`: passed for the packaging changes.
- GitHub Actions `container` job (run `39299936752`): `docker build` passed,
  `docker run --rm -e INTENT_GATE_OFFLINE_EMBEDDINGS=1 intentgate:phase7 pytest -q`
  passed, and `report_phase5.py` ran inside the container.
- Local Docker Desktop remains unavailable on the Windows host. The Linux engine fails
  before startup, so the clean GitHub Actions runner provides the validation.

## Artifacts

- `Dockerfile`
- `.dockerignore`
- `.github/workflows/tests.yml` (container job)
- `requirements-repro.in` and `requirements-repro.txt`
- `scripts/container_entrypoint.py`
- `scripts/run_phase5.py --check --artifacts-only`
- `configs/phase5_artifact_hashes.json`
- `tests/test_phase5_freeze.py`

## Limitations

The roadmap's packaging completion criterion requires an actual successful image build
and test run. The GitHub Actions container job provides that clean-machine evidence. Local
Docker Desktop remains unavailable on the author's Windows host, so the validation path is
the CI runner, not the local machine. No factory reset or Docker data deletion was performed
during diagnosis.

Offline unit tests use the deterministic test embedding backend. They do not establish
embedding-model numerical equivalence across platforms or replicate paid model results.

## Supervisor Q&A

**Does the image include API keys or third-party benchmark clones?**
No. Its integrity check runs without either. Live experiment commands require explicit
runtime inputs.

**Does the artifact check replace the frozen experiment manifest?**
No. The Phase 5 manifest and results remain unchanged. The new hash manifest records the
published bytes so later accidental edits are detected.

**Is clean-machine reproduction already verified?**
Yes. The GitHub Actions container job built the image and ran `pytest -q` plus the offline
reporter on a clean `ubuntu-latest` runner (run `39299936752`, PR #44). Local Docker Desktop
is still unavailable on the author's Windows host.
