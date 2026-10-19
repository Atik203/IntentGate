"""Shared orchestrator utilities (blueprint Sec 5/6): seeding, case loading, ordering guard."""
from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any, Dict


def set_seed(seed: int = 42):
    random.seed(seed)


def load_cases(path: str | Path) -> list[Dict[str, Any]]:
    """Load benchmark case file: {case_id, user_request, attacker_content, ground_truth}."""
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("cases", [])


class OrderingGuard:
    """Enforces: parse happens BEFORE any tool definitions/attacker content are loaded (Sec 10).

    Usage:
      guard = OrderingGuard()
      contract = parser.parse(request)     # step 1
      guard.assert_clean()
      load_tools(poisoned_defs)            # step 2 (attacker content enters)
    """

    def __init__(self):
        self.attacker_content_loaded = False

    def load_tool_definitions(self, defs):
        self.attacker_content_loaded = True
        return defs

    def assert_clean(self):
        if self.attacker_content_loaded:
            raise RuntimeError("ordering violated: intent must be parsed before attacker content")


def add_endpoint_args(ap):
    """Phase 6 P0-1: per-role OpenAI-compatible endpoint overrides (CLI > env)."""
    ap.add_argument("--agent-base-url", default=None, help="agent LLM base_url (else AGENT_BASE_URL/QWEN_BASE_URL)")
    ap.add_argument("--parser-base-url", default=None, help="parser LLM base_url (else PARSER_BASE_URL)")
    ap.add_argument("--agent-api-key", default=None, help="agent LLM api key (else AGENT_API_KEY/QWEN_API_KEY)")
    ap.add_argument("--parser-api-key", default=None, help="parser LLM api key (else PARSER_API_KEY)")
    ap.add_argument(
        "--agent-reasoning-effort",
        default=None,
        help="agent LLM reasoning_effort (e.g. 'none' disables Qwen thinking on Ollama); "
        "else AGENT_REASONING_EFFORT",
    )
    return ap


def build_run_parser(mode: str = "llm", llm=None):
    """Select the parser backend for a run: LLM (default) or deterministic heuristic (E28)."""
    from intent_gate.parser.parser import build_parser

    if mode == "llm":
        return build_parser(llm=llm)
    if mode == "heuristic":
        return build_parser(offline=True)
    raise ValueError(f"unknown parser mode: {mode}")


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:  # empty string counts as unset
            return value
    return None


def resolve_base_url(cli_value: str | None, role: str) -> str | None:
    """CLI flag wins; agent falls back to AGENT_BASE_URL then legacy QWEN_BASE_URL.

    Parser has no QWEN fallback on purpose: Phase 6 isolates the variable by holding
    the parser on the default endpoint unless explicitly overridden.
    """
    if cli_value:
        return cli_value
    if role == "agent":
        return _first_env("AGENT_BASE_URL", "QWEN_BASE_URL")
    return _first_env("PARSER_BASE_URL")


def resolve_api_key(cli_value: str | None, role: str) -> str | None:
    if cli_value:
        return cli_value
    if role == "agent":
        return _first_env("AGENT_API_KEY", "QWEN_API_KEY")
    return _first_env("PARSER_API_KEY")


def resolve_reasoning_effort(cli_value: str | None, role: str) -> str | None:
    """Agent reasoning-effort override (CLI > env); unset keeps provider default.

    Used to disable Qwen "thinking" on local Ollama (`reasoning_effort=none`), which
    otherwise returns empty `content` and breaks tool-call parsing.
    """
    if cli_value:
        return cli_value
    if role == "agent":
        return _first_env("AGENT_REASONING_EFFORT")
    return _first_env("PARSER_REASONING_EFFORT")
