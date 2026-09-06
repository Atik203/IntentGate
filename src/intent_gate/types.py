"""Shared dataclasses (blueprint Sec 4-6). All gate I/O flows through these types."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal

Decision = Literal["allow", "block", "escalate"]


@dataclass
class ToolCall:
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    source: str = "agent"  # agent | injected | poisoned (for analysis only)

    def naturalized(self) -> str:
        """Human sentence used for embedding (blueprint Sec 5: naturalize before embed)."""
        if not self.parameters:
            return f"call tool {self.name}"
        params = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"call tool {self.name} with {params}"


@dataclass
class IntentContract:
    goals: list
    expected_tool_categories: list
    permitted_data_access: list
    side_effect_limits: Dict[str, str]
    specificity: str = "specific"
    raw_request: str = ""

    def contract_text(self) -> str:
        goals = "; ".join(self.goals)
        cats = ", ".join(self.expected_tool_categories)
        limits = ", ".join(f"{k}:{v}" for k, v in self.side_effect_limits.items())
        return f"goals: {goals} | tools: {cats} | limits: {limits} | request: {self.raw_request}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goals": self.goals,
            "expected_tool_categories": self.expected_tool_categories,
            "permitted_data_access": self.permitted_data_access,
            "side_effect_limits": self.side_effect_limits,
            "specificity": self.specificity,
            "raw_request": self.raw_request,
        }


@dataclass
class GateResult:
    decision: Decision
    score: float
    score_sem: float
    score_rule: float
    latency_ms: float
    rule_triggered: bool = False
    would_escalate: bool = False
    reason: str = ""
