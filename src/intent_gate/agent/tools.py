"""Tool registry + schema validation (blueprint Sec 5 Comp 1)."""
from __future__ import annotations

from typing import Any, Callable, Dict

from intent_gate.types import ToolCall


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable):
        self._tools[name] = fn

    def has(self, name: str) -> bool:
        return name in self._tools

    def execute(self, name: str, parameters: Dict[str, Any]):
        if name not in self._tools:
            raise KeyError(f"unknown tool {name!r}")
        return self._tools[name](**parameters)


def parse_tool_call(raw: dict) -> ToolCall:
    """Validate a proposed tool_call dict; raises on malformed (agent failure case recovery)."""
    if not isinstance(raw, dict) or not raw.get("name"):
        raise ValueError(f"malformed tool call: {raw!r}")
    return ToolCall(name=str(raw["name"]), parameters=dict(raw.get("parameters") or {}), source=raw.get("source", "agent"))
