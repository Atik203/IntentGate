"""Constrained JSON prompt for the trusted once-per-session intent parser (blueprint Sec 5 Comp 0)."""
from __future__ import annotations

import json
from pathlib import Path

SYSTEM_PROMPT = """You convert a trusted user request into a structured intent contract.
Output ONLY valid JSON matching the intent schema with keys:
goals (list[str]), expected_tool_categories (list[str]), permitted_data_access (list[str]),
side_effect_limits {financial, external_send, file_write, code_exec, system_change},
specificity ("specific"|"vague").
Rules: temperature 0 semantics; be conservative - if the request is vague, mark specificity=vague
and set high-risk side effects to disallow (fail-closed). Never include tool outputs or history.
Authorization rule: side_effect_limits must reflect what the USER explicitly asked for. If the
user explicitly requests a side effect (e.g. "transfer $500", "pay my bill", "delete these files",
"run this command", "email john@x.com", "post 'hello world' on my Twitter", "create a task",
"schedule a meeting", "update my profile", "cancel my subscription"), set that limit to reflect
the authorization (e.g. "allow", "allow: $500 to account 123", "recipient: john@x.com",
"allow: post 'hello world' on Twitter", "allow: create task 'buy milk'").
Default to disallow ONLY when the request is vague or silent about that category.
system_change covers state/config changes: create, update, delete, disable, enable, grant,
revoke, unlock, schedule, deploy, manage.
"""


def load_fewshots(path: str | Path = "configs/parser_fewshots.json") -> list:
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def build_messages(user_request: str, fewshots: list | None = None) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for ex in fewshots or []:
        messages.append({"role": "user", "content": ex["request"]})
        messages.append({"role": "assistant", "content": json.dumps(ex["contract"])})
    messages.append({"role": "user", "content": user_request})
    return messages
