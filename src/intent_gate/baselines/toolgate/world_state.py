"""Symbolic world-state for ToolGate B2 (blueprint Sec 5 Comp 3; minimal per Appendix G scope)."""
from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

_PATH_RE = re.compile(r"(?<![\w])((?:~|/)[\w./~-]+)")
_QUOTED_FILE_RE = re.compile(r"['\"]([\w.-]+\.[A-Za-z0-9]{1,6})['\"]")
_HOME_RE = re.compile(r"home (?:folder|directory)", re.IGNORECASE)


class WorldState:
    """Minimal symbolic state: balance, files, directories, permissions + recorded effects.

    Contracts read ``files``/``directories`` for scope checks; ``tool_states`` records
    effects keyed by family (e.g. ``bank_transfers``). Per-case seeding for benchmark
    runs is best-effort: only paths named in the trusted request are known.
    """

    def __init__(self):
        self.balance: float = 0.0
        self.files: set[str] = set()
        self.directories: set[str] = set()
        self.permissions: set[str] = set()
        self.tool_states: dict[str, list[Any]] = {}
        self.extra: dict[str, Any] = {}

    def snapshot(self) -> dict:
        return deepcopy(self.to_dict())

    def restore(self, snapshot: dict) -> None:
        self.balance = snapshot["balance"]
        self.files = set(snapshot["files"])
        self.directories = set(snapshot["directories"])
        self.permissions = set(snapshot["permissions"])
        self.tool_states = deepcopy(snapshot["tool_states"])
        self.extra = deepcopy(snapshot["extra"])

    def to_dict(self) -> dict:
        return {
            "balance": self.balance,
            "files": sorted(self.files),
            "directories": sorted(self.directories),
            "permissions": sorted(self.permissions),
            "tool_states": self.tool_states,
            "extra": self.extra,
        }


def seed_from_request(request: str, state: WorldState | None = None) -> WorldState:
    """Best-effort state seeding from the trusted request: named paths + their directories."""
    state = state or WorldState()
    for match in _PATH_RE.findall(request or ""):
        path = match.rstrip(".,;:")
        state.files.add(path)
        parent = path.rsplit("/", 1)[0]
        if parent and parent != "/":
            state.directories.add(parent)
        elif parent == "/":
            state.directories.add("/")
    for filename in _QUOTED_FILE_RE.findall(request or ""):
        state.files.add(filename)
    if _HOME_RE.search(request or ""):
        state.directories.add("~")
    return state
