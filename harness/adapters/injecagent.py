"""InjecAgent case loader (blueprint Sec 8).

Case schema verified 2026-09-11 against injecagent @ f19c9f2c:
  User Instruction, User Tool, Tool Parameters (str repr), Tool Response (injection embedded),
  Attacker Tools (list), Attacker Instruction, Attack Type, Expected Achievements, Thought.
"""
from __future__ import annotations

import ast
import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CASE_FILE_RE = re.compile(r"test_cases_(?P<split>ds|dh)_(?P<setting>base|enhanced)\.json$")


@dataclass
class InjecAgentCase:
    case_id: str
    user_instruction: str
    user_tool: str
    tool_parameters: dict
    tool_response: str
    attacker_tools: list
    attacker_instruction: str
    attack_type: str
    setting: str
    split: str
    expected_achievements: str = ""
    thought: str = ""
    raw: dict = field(default_factory=dict, repr=False)


def parse_tool_parameters(raw: Any) -> dict:
    """Tool Parameters is a Python-dict repr string; parse safely (no eval)."""
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        parsed = ast.literal_eval(str(raw))
        return dict(parsed) if isinstance(parsed, dict) else {}
    except (ValueError, SyntaxError):
        return {}


def infer_split_setting(path: str | Path) -> tuple[str, str]:
    match = CASE_FILE_RE.search(str(path))
    if not match:
        return "unknown", "unknown"
    return match.group("split"), match.group("setting")


def load_injecagent_cases(
    path: str | Path, limit: int | None = None, seed: int = 42
) -> list[InjecAgentCase]:
    """Load one test-case file; optional deterministic subset (limit, seed)."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    split, setting = infer_split_setting(p)
    cases = []
    for i, raw in enumerate(data):
        cases.append(
            InjecAgentCase(
                case_id=f"{split}_{setting}_{i:04d}",
                user_instruction=raw.get("User Instruction", ""),
                user_tool=raw.get("User Tool", ""),
                tool_parameters=parse_tool_parameters(raw.get("Tool Parameters")),
                tool_response=raw.get("Tool Response", ""),
                attacker_tools=list(raw.get("Attacker Tools") or []),
                attacker_instruction=raw.get("Attacker Instruction", ""),
                attack_type=raw.get("Attack Type", ""),
                setting=setting,
                split=split,
                expected_achievements=raw.get("Expected Achievements", ""),
                thought=raw.get("Thought", ""),
                raw=raw,
            )
        )
    if limit is not None and limit < len(cases):
        cases = random.Random(seed).sample(cases, limit)
    return cases


def load_tool_definitions(path: str | Path = "data/raw/InjecAgent/data/tools.json") -> list:
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def load_simulated_responses(
    path: str | Path = "data/raw/InjecAgent/data/attacker_simulated_responses.json",
) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))
