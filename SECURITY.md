# Security Policy — IntentGate

## Scope

IntentGate is a security **research** project (thesis): a middleware gate that protects LLM agents from prompt-injection and tool-poisoning hijacks. We take the security of this codebase itself seriously.

In scope for reports:

- Gate bypass: any tool call path that executes without passing through `GateMiddleware.execute()`.
- Ordering violation: attacker content reaching the intent parser or the contract being mutated after freeze.
- Fail-open behavior: unknown/missing contract fields that allow high-risk side effects instead of failing closed.
- Secret leakage in logs, traces, or results (`.env`, API keys, benchmark credentials).
- Vulnerabilities in the harness that could execute untrusted benchmark content on the host.

Out of scope:

- The benchmark attack payloads themselves (`data/raw/`, InjecAgent/MCPTox cases). These are intentionally malicious artifacts used in a sandbox for evaluation. Never run them against systems you do not own.
- Model outputs / jailbreaks of the LLM backbones — report those upstream to the model provider.
- Findings that require an attacker who can already modify the gate's own source code.

## Supported versions

| Version | Supported |
|---|---|
| `main` (production) | Yes |
| `dev` (integration) | Yes |
| Feature branches | No — report against `dev` |

## Reporting a vulnerability

**Do not open a public issue.** Use GitHub's private vulnerability reporting:

1. Go to the repository's **Security** tab → **Advisories** → **Report a vulnerability**.
2. Include: affected file/function, reproduction steps, impact, and a suggested fix if you have one.

If private reporting is unavailable, contact a maintainer directly (GitHub: [@Atik203](https://github.com/Atik203)).

## Response targets

- Acknowledge within **72 hours**.
- Triage + severity assessment within **7 days**.
- Fix or documented mitigation before the next `dev` → `main` merge.

## Research ethics

This project evaluates attacks only against benchmark environments and simulated tools. Do not use anything in this repo to attack real systems, accounts, or users. Report findings responsibly; academic credit follows normal citation practice (see `README.md` citation block).
