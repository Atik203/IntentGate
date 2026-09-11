"""Trusted once-per-session intent parser (blueprint Sec 5 Comp 0).

Ordering invariant (load-bearing): parse() must receive ONLY the raw user request,
never tool outputs/history. Enforced + tested in tests/test_gate_ordering.py.

Backends:
  LLM (primary)      -> constrained JSON, temperature 0, one repair retry, then
                        fail-closed minimal contract (blueprint Sec 5 recovery).
  Heuristic (offline)-> deterministic stand-in so tests/CI run without API keys.
`last_backend` records which path served the last parse.
"""
from __future__ import annotations

import json
import os

from intent_gate.parser.prompts import build_messages, load_fewshots
from intent_gate.parser.schema import coerce_contract, minimal_contract
from intent_gate.types import IntentContract

REPAIR_PROMPT = (
    "Your previous response was not valid JSON matching the schema. "
    "Return ONLY the corrected JSON object, no prose, no markdown fences."
)


class IntentParser:
    def __init__(
        self,
        llm=None,
        model_id: str = "gpt-4o-mini",
        fewshots_path: str = "configs/parser_fewshots.json",
        max_retries: int = 1,
    ):
        self.llm = llm
        self.model_id = model_id
        self.fewshots = load_fewshots(fewshots_path)
        self.max_retries = max_retries
        self.last_backend = "heuristic"

    def parse(self, user_request: str) -> IntentContract:
        """Parse trusted request -> frozen contract. Falls back fail-closed, never raises."""
        if not user_request or not user_request.strip():
            self.last_backend = "minimal"
            return minimal_contract(user_request)
        if self.llm is not None:
            parsed, backend = self._parse_llm(user_request)
            if parsed is not None:
                self.last_backend = backend
                return parsed
        self.last_backend = "heuristic"
        return self._parse_heuristic(user_request)

    def _parse_llm(self, user_request: str) -> tuple[IntentContract | None, str]:
        messages = build_messages(user_request, self.fewshots)
        for _ in range(self.max_retries + 1):
            try:
                raw = self.llm.call(messages, temperature=0.0, response_format={"type": "json_object"})
            except Exception:
                return None, "heuristic"
            try:
                data = json.loads(raw or "")
                return coerce_contract(data, raw_request=user_request), "llm"
            except (json.JSONDecodeError, TypeError):
                messages = messages + [
                    {"role": "assistant", "content": raw or ""},
                    {"role": "user", "content": REPAIR_PROMPT},
                ]
        return minimal_contract(user_request), "minimal"

    def _parse_heuristic(self, user_request: str) -> IntentContract:
        text = user_request.lower()
        pay = (
            "allow"
            if any(w in text for w in ("pay", "purchase", "buy", "transfer"))
            and "don't pay" not in text
            and "do not pay" not in text
            else "no payment"
        )
        ext = "self-only" if ("email" in text and "me" in text) else "disallow"
        vague = len(user_request.split()) <= 3
        data = {
            "goals": [user_request],
            "expected_tool_categories": _guess_categories(text),
            "permitted_data_access": [],
            "side_effect_limits": {
                "financial": pay,
                "external_send": ext,
                "file_write": "disallow",
                "code_exec": "disallow",
            },
            "specificity": "vague" if vague else "specific",
        }
        return coerce_contract(data, raw_request=user_request)


def build_parser(offline: bool | None = None, model_id: str | None = None) -> IntentParser:
    """Factory: LLM parser when an API key is available, else offline heuristic."""
    if offline is None:
        offline = not os.getenv("OPENAI_API_KEY")
    model_id = model_id or os.getenv("PARSER_MODEL_ID", "gpt-4o-mini")
    llm = None
    if not offline:
        from intent_gate.agent.base import LLMClient

        llm = LLMClient(model_id=model_id)
    return IntentParser(llm=llm, model_id=model_id)


def _guess_categories(text: str) -> list:
    cats = []
    for kw, cat in (
        ("flight", "search"), ("search", "search"), ("summar", "summarize"),
        ("email", "send"), ("send", "send"), ("hold", "hold"), ("book", "book"),
        ("sheet", "read"), ("read", "read"),
    ):
        if kw in text and cat not in cats:
            cats.append(cat)
    return cats
