"""Schema validation + fail-closed defaults (blueprint Sec 5 Comp 0 recovery)."""
from __future__ import annotations

from typing import Any, Dict

from intent_gate.types import IntentContract

REQUIRED_LIMIT_KEYS = ("financial", "external_send", "file_write", "code_exec")
FAIL_CLOSED_LIMITS = {
    "financial": "no payment",
    "external_send": "disallow",
    "file_write": "disallow",
    "code_exec": "disallow",
}


def coerce_contract(data: Dict[str, Any], raw_request: str = "") -> IntentContract:
    """Validate LLM JSON; on missing/invalid fields fall back fail-closed.

    Schema frozen v1 (2026-09-11): see configs/intent_schema.json and
    docs/experiments/parser_spotcheck_v1.md.
    """
    if not isinstance(data, dict):
        return minimal_contract(raw_request)
    goals = data.get("goals") or ([raw_request] if raw_request else ["unspecified"])
    if isinstance(goals, str):
        goals = [goals]
    cats = data.get("expected_tool_categories") or []
    if isinstance(cats, str):
        cats = [cats]
    scopes = data.get("permitted_data_access") or []
    if isinstance(scopes, str):
        scopes = [scopes]
    limits = dict(data.get("side_effect_limits") or {})
    for k in REQUIRED_LIMIT_KEYS:
        if k not in limits or not limits[k]:
            limits[k] = FAIL_CLOSED_LIMITS[k]
    specificity = data.get("specificity", "specific")
    if specificity not in ("specific", "vague"):
        specificity = "specific"
    # Vague contracts fail closed on high-risk effects
    if specificity == "vague":
        for k, v in FAIL_CLOSED_LIMITS.items():
            limits.setdefault(k, v)
    return IntentContract(
        goals=list(goals),
        expected_tool_categories=list(cats),
        permitted_data_access=list(scopes),
        side_effect_limits=limits,
        specificity=specificity,
        raw_request=raw_request or data.get("raw_request", ""),
    )


def minimal_contract(raw_request: str) -> IntentContract:
    """Fallback when parser returns invalid JSON after one repair retry."""
    return IntentContract(
        goals=[raw_request] if raw_request else ["unspecified"],
        expected_tool_categories=[],
        permitted_data_access=[],
        side_effect_limits=dict(FAIL_CLOSED_LIMITS),
        specificity="vague",
        raw_request=raw_request,
    )
