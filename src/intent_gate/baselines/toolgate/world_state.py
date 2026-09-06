"""Symbolic world-state for ToolGate B2 (blueprint Sec 5 Comp 3; minimal per Appendix G scope)."""
from __future__ import annotations

from typing import Any, Dict


class WorldState:
    """Minimal symbolic state: balance, files, permissions. Only fields needed for evaluated tools."""

    def __init__(self):
        self.balance: float = 0.0
        self.files: set[str] = set()
        self.permissions: set[str] = set()
        self.extra: Dict[str, Any] = {}

    def to_dict(self) -> dict:
        return {
            "balance": self.balance,
            "files": sorted(self.files),
            "permissions": sorted(self.permissions),
            "extra": self.extra,
        }
