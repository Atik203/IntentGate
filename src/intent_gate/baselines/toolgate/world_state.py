"""Symbolic world-state for ToolGate B2 (blueprint Sec 5 Comp 3; minimal per Appendix G scope)."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


class WorldState:
    """Minimal symbolic state: balance, files, permissions + per-tool recorded effects.

    Contract authoring seeds ``tool_states`` keys (e.g. ``bank_transfers``) via effects;
    per-case seeding for full-suite runs is a Gate 2 harness responsibility.
    """

    def __init__(self):
        self.balance: float = 0.0
        self.files: set[str] = set()
        self.permissions: set[str] = set()
        self.tool_states: dict[str, list[Any]] = {}
        self.extra: dict[str, Any] = {}

    def snapshot(self) -> dict:
        return deepcopy(self.to_dict())

    def restore(self, snapshot: dict) -> None:
        self.balance = snapshot["balance"]
        self.files = set(snapshot["files"])
        self.permissions = set(snapshot["permissions"])
        self.tool_states = deepcopy(snapshot["tool_states"])
        self.extra = deepcopy(snapshot["extra"])

    def to_dict(self) -> dict:
        return {
            "balance": self.balance,
            "files": sorted(self.files),
            "permissions": sorted(self.permissions),
            "tool_states": self.tool_states,
            "extra": self.extra,
        }
