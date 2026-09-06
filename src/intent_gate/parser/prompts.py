"""Constrained JSON prompt for the trusted once-per-session intent parser (blueprint Sec 5 Comp 0)."""
from __future__ import annotations

import json
from pathlib import Path

SYSTEM_PROMPT = """You convert a trusted user request into a structured intent contract.
Output ONLY valid JSON matching the intent schema with keys:
goals (list[str]), expected_tool_categories (list[str]), permitted_data_access (list[str]),
side_effect_limits {financial, external_send, file_write, code_exec, irreversible},
specificity ("specific"|"vague").
Rules: temperature 0 semantics; be conservative - if the request is vague, mark specificity=vague
and set high-risk side effects to disallow (fail-closed). Never include tool outputs or history.
"""


def load_fewshots(path: str | Path = "configs/parser_fewshots.json") -> list:
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def build_messages(user_request: str, fewshots: list | None = None) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for ex in (fewshots or [])[:3]:
        messages.append({"role": "user", "content": ex["request"]})
        messages.append({"role": "assistant", "content": json.dumps(ex["contract"])})
    messages.append({"role": "user", "content": user_request})
    return messages
