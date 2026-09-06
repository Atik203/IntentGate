"""Thresholding: allow / block / escalate band (blueprint Sec 5 Comp 2)."""
from __future__ import annotations

from intent_gate.types import Decision


def decide(score: float, tau: float = 0.6, delta: float = 0.1) -> Decision:
    if score >= tau:
        return "allow"
    if score >= tau - delta:
        return "escalate"
    return "block"
