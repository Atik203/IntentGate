"""Trusted once-per-session intent parser (blueprint Sec 5 Comp 0).

Ordering invariant (load-bearing): parse() must receive ONLY the raw user request,
never tool outputs/history. Enforced + tested in tests/test_gate_ordering.py.
"""
from __future__ import annotations

import json
import os

from intent_gate.parser.prompts import build_messages, load_fewshots
from intent_gate.parser.schema import coerce_contract, minimal_contract
from intent_gate.types import IntentContract


class IntentParser:
    def __init__(self, model_id: str = "gpt-4o-mini", fewshots_path: str = "configs/parser_fewshots.json"):
        self.model_id = model_id
        self.fewshots = load_fewshots(fewshots_path)

    def parse(self, user_request: str) -> IntentContract:
        """Parse trusted request -> frozen contract. Falls back fail-closed, never raises."""
        if not user_request or not user_request.strip():
            return minimal_contract(user_request)
        raw_llm: str | None = None
        # TODO(Gate 2): wire OpenAI-compatible API call here (temp 0, JSON mode, 1 repair retry).
        # For skeleton/pilot the heuristic parser below keeps Weeks 1-2 unblocked offline.
        try:
            raw_llm = self._heuristic_json(user_request)
            data = json.loads(raw_llm)
            return coerce_contract(data, raw_request=user_request)
        except Exception:
            return minimal_contract(user_request)

    def _heuristic_json(self, user_request: str) -> str:
        """Offline stand-in so pilot + tests run without API keys. Replaced by real LLM call."""
        text = user_request.lower()
        pay = "allow" if any(w in text for w in ("pay", "purchase", "buy", "transfer")) and "don't pay" not in text and "do not pay" not in text else "no payment"
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
        _ = build_messages(user_request, self.fewshots)  # keep prompt path exercised
        _ = os.getenv("PARSER_MODEL_ID", self.model_id)
        return json.dumps(data)


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
