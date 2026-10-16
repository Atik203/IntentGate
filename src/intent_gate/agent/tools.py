"""Tool registry + schema validation (blueprint Sec 5 Comp 1)."""
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from intent_gate.types import ToolCall


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._descriptions: dict[str, str] = {}

    def register(self, name: str, fn: Callable, description: str = ""):
        self._tools[name] = fn
        self._descriptions[name] = description

    def has(self, name: str) -> bool:
        return name in self._tools

    def describe(self) -> str:
        """Stable tool block for the agent prompt prefix (sorted; cache-friendly)."""
        if not self._tools:
            return "(no tools registered)"
        entries = [
            {"name": name, "description": self._descriptions.get(name, "")}
            for name in sorted(self._tools)
        ]
        return json.dumps(entries, indent=1)

    def execute(self, name: str, parameters: dict[str, Any]):
        if name not in self._tools:
            raise KeyError(f"unknown tool {name!r}")
        return self._tools[name](**parameters)


def parse_tool_call(raw: dict) -> ToolCall:
    """Validate a proposed tool_call dict; raises on malformed (agent failure case recovery)."""
    if not isinstance(raw, dict) or not raw.get("name"):
        raise ValueError(f"malformed tool call: {raw!r}")
    return ToolCall(
        name=str(raw["name"]),
        parameters=dict(raw.get("parameters") or {}),
        source=raw.get("source", "agent"),
    )
