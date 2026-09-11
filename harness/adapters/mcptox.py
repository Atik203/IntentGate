"""MCPTox snapshot loader (blueprint Sec 8; snapshot 2026-09-11).

Snapshot layout (`response_all.json`): 45 live servers -> `malicious_instance` x1,348.
Each instance carries a poisoned tool description and exactly one `datas` entry
(query + poisoned system prompt + recorded model responses). Static snapshot only —
live-server dynamics may differ (documented limitation).
"""
from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path

_FAKE_TOOL_RE = re.compile(r"^Tool:\s*(\S+)", re.M)
_CLEAN_TOOL_RE = re.compile(r"^Tool:\s*([\w.-]+)\s*$", re.M)
_QUOTED_RE = re.compile(r"'([^']{20,})'|\"([^\"]{20,})\"")


@dataclass
class MCPToxCase:
    case_id: str
    server: str
    risk: str
    paradigm: str
    query: str
    system_prompt: str
    fake_tool: str
    clean_tools: list
    payloads: list
    poisoned_description: str
    raw: dict = field(default_factory=dict, repr=False)


def extract_fake_tool(poisoned_tool: str) -> str:
    match = _FAKE_TOOL_RE.search(poisoned_tool or "")
    return match.group(1) if match else ""


def extract_clean_tools(system_prompt: str) -> list:
    tools = [t for t in _CLEAN_TOOL_RE.findall(system_prompt or "") if t]
    return list(dict.fromkeys(tools))


def extract_payloads(poisoned_tool: str, limit: int = 5) -> list:
    found = []
    for a, b in _QUOTED_RE.findall(poisoned_tool or ""):
        value = a or b
        if value not in found:
            found.append(value)
    return sorted(found, key=len, reverse=True)[:limit]


def load_mcptox_cases(
    path: str | Path = "data/raw/mcptox/response_all.json",
    limit: int | None = None,
    seed: int = 42,
    risk: str | None = None,
) -> list[MCPToxCase]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cases: list[MCPToxCase] = []
    for server_name, server in (data.get("servers") or {}).items():
        for idx, instance in enumerate(server.get("malicious_instance") or []):
            entry = (instance.get("datas") or [{}])[0]
            poisoned = instance.get("poisoned_tool") or ""
            metadata = instance.get("metadata") or {}
            if not entry.get("query") or not poisoned:
                continue
            cases.append(
                MCPToxCase(
                    case_id=f"{server_name}_{idx:03d}",
                    server=server_name,
                    risk=metadata.get("security risk", "Other"),
                    paradigm=metadata.get("paradigm", "Other"),
                    query=entry.get("query", ""),
                    system_prompt=entry.get("system", ""),
                    fake_tool=extract_fake_tool(poisoned),
                    clean_tools=extract_clean_tools(entry.get("system", "")),
                    payloads=extract_payloads(poisoned),
                    poisoned_description=poisoned,
                    raw=instance,
                )
            )
    if risk:
        cases = [c for c in cases if c.risk == risk]
    if limit is not None and limit < len(cases):
        cases = random.Random(seed).sample(cases, limit)
    return cases
