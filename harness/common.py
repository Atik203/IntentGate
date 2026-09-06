"""Shared orchestrator utilities (blueprint Sec 5/6): seeding, case loading, ordering guard."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict


def set_seed(seed: int = 42):
    random.seed(seed)


def load_cases(path: str | Path) -> list[Dict[str, Any]]:
    """Load benchmark case file: {case_id, user_request, attacker_content, ground_truth}."""
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("cases", [])


class OrderingGuard:
    """Enforces: parse happens BEFORE any tool definitions/attacker content are loaded (Sec 10).

    Usage:
      guard = OrderingGuard()
      contract = parser.parse(request)     # step 1
      guard.assert_clean()
      load_tools(poisoned_defs)            # step 2 (attacker content enters)
    """

    def __init__(self):
        self.attacker_content_loaded = False

    def load_tool_definitions(self, defs):
        self.attacker_content_loaded = True
        return defs

    def assert_clean(self):
        if self.attacker_content_loaded:
            raise RuntimeError("ordering violated: intent must be parsed before attacker content")
