"""Symbolic world-state for ToolGate B2 (blueprint Sec 5 Comp 3; minimal per Appendix G scope)."""
from __future__ import annotations

from typing import Any, Dict


class WorldState:
    """Minimal symbolic state: balance, files, permissions + per-tool metadata.

    Only fields needed for evaluated tools are defined here; per-tool state
    can be stored in ``tool_states`` keyed by tool name.
    """

    def __init__(self):
        self.balance: float = 0.0
        self.files: set[str] = set()
        self.permissions: set[str] = set()
        self.tool_states: Dict[str, Dict[str, Any]] = {}
        self.extra: Dict[str, Any] = {}

    def to_dict(self) -> dict:
        return {
            "balance": self.balance,
            "files": sorted(self.files),
            "permissions": sorted(self.permissions),
            "tool_states": self.tool_states,
            "extra": self.extra,
        }
