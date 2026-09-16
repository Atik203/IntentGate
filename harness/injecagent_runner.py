"""Gate-ready case runner for InjecAgent (blueprint Sec 5 Comp 1).

B1 uses it with a plain executor; B2/ours pass a policy factory built from the trusted
user instruction. Prompts are vendored (`harness/prompts/injecagent.py`) so all conditions
share identical, byte-stable input.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from harness.adapters.injecagent import InjecAgentCase
from harness.gate_policy import AllowAllPolicy
from harness.parsing import (
    evaluate_output,
    extract_tool_calls,
    parse_react_output,
    truncate_at_marker,
)
from harness.prompts.injecagent import PROMPT_DICT


@dataclass
class CaseResult:
    case_id: str
    eval: str
    output: str
    tool_calls: list = field(default_factory=list)
    invalid_reason: str = ""
    attacker_params: str = ""
    attacker_thought: str = ""
    error: str = ""
    gate_events: list = field(default_factory=list)
    gate_blocked: bool = False


def build_tool_dict(toolkits: list) -> dict:
    """Mirror injecagent's get_tool_dict: tool key = toolkit name + tool name."""
    tool_dict: dict = {}
    for kit in toolkits:
        kit_name = kit["toolkit"]
        for tool in kit["tools"]:
            named = dict(tool)
            named["name"] = kit_name + tool["name"]
            tool_dict[named["name"]] = named
    return tool_dict


def build_messages(case: InjecAgentCase, tool_dict: dict, prompt_type: str = "InjecAgent") -> list:
    system_prompt, user_prompt = PROMPT_DICT[prompt_type]
    available = [case.user_tool] + case.attacker_tools
    descriptions = json.dumps([tool_dict[t] for t in available], indent=True)
    scratchpad = (
        f"\n{case.raw['Thought']}\nAction: {case.user_tool}\n"
        f"Action Input: {case.raw['Tool Parameters']}\n"
        f"Observation: {case.raw['Tool Response']}\n"
    )
    filled = user_prompt.format(
        available_tool_descriptions=descriptions,
        input=case.user_instruction,
        available_tool_names=available,
        agent_scratchpad=scratchpad,
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": filled},
    ]


def run_case(
    case: InjecAgentCase,
    llm,
    tool_dict: dict,
    prompt_type: str = "InjecAgent",
    temperature: float = 0.0,
    policy_factory=None,
) -> CaseResult:
    policy = policy_factory(case.user_instruction) if policy_factory else AllowAllPolicy()
    set_context = getattr(policy, "set_context", None)
    if callable(set_context):
        set_context(
            {
                "case_id": case.case_id,
                "benchmark": "injecagent",
                "split": case.split,
                "setting": case.setting,
            }
        )
    try:
        output = llm.call(build_messages(case, tool_dict, prompt_type), temperature=temperature)
    except Exception as exc:
        return CaseResult(case_id=case.case_id, eval="error", output="", error=str(exc))
    evaluation = evaluate_output(
        output, case.attacker_tools[0], case.attacker_tools, case.user_tool, case.attacker_instruction
    )
    info_list = parse_react_output(truncate_at_marker(output or "").strip())
    calls = extract_tool_calls(info_list)

    gate_events: list = []
    gate_blocked = False
    if evaluation["eval"] == "succ":
        target = case.attacker_tools[0] if case.attacker_tools else ""
        for call in calls:
            allowed = policy.allows(call)
            gate_events.append({"name": call.name, "allowed": allowed})
            if call.name == target and not allowed:
                gate_blocked = True
        if gate_blocked:
            evaluation = {**evaluation, "eval": "unsucc"}

    return CaseResult(
        case_id=case.case_id,
        eval=evaluation["eval"],
        output=output or "",
        tool_calls=calls,
        invalid_reason=evaluation.get("invalid_reason", ""),
        attacker_params=evaluation.get("Attacker Tool Parameters", ""),
        attacker_thought=evaluation.get("Attacker Tool Thought", ""),
        gate_events=gate_events,
        gate_blocked=gate_blocked,
    )


def serialize_calls(calls: list) -> list:
    return [{"name": c.name, "parameters": c.parameters, "source": c.source} for c in calls]


def _run_each(cases: list, llm, tool_dict: dict, policy_factory, handle, progress) -> tuple[dict, list, int]:
    counts = {"succ": 0, "unsucc": 0, "invalid": 0, "error": 0}
    gate_blocked = 0
    rows: list = []
    for case in cases:
        result = run_case(case, llm, tool_dict, policy_factory=policy_factory)
        counts[result.eval] = counts.get(result.eval, 0) + 1
        gate_blocked += int(result.gate_blocked)
        row = {
            "case_id": case.case_id,
            "eval": result.eval,
            "invalid_reason": result.invalid_reason,
            "output": result.output,
            "tool_calls": serialize_calls(result.tool_calls),
            "gate_events": result.gate_events,
            "gate_blocked": result.gate_blocked,
            "attacker_params": result.attacker_params,
            "attacker_thought": result.attacker_thought,
            "error": result.error,
        }
        rows.append(row)
        if handle:
            handle.write(json.dumps(row) + "\n")
        if progress:
            progress(result, case)
    return counts, rows, gate_blocked


def run_cases(
    cases: list,
    llm,
    tool_dict: dict,
    policy_factory=None,
    jsonl_path: str | Path | None = None,
    progress=None,
) -> tuple[dict, list]:
    """Run cases and return (summary, rows); writes JSONL when a path is given."""
    if jsonl_path:
        with Path(jsonl_path).open("w", encoding="utf-8") as handle:
            counts, rows, gate_blocked = _run_each(cases, llm, tool_dict, policy_factory, handle, progress)
    else:
        counts, rows, gate_blocked = _run_each(cases, llm, tool_dict, policy_factory, None, progress)
    decided = counts["succ"] + counts["unsucc"]
    summary = {
        "n": len(cases),
        "counts": counts,
        "gate_blocked": gate_blocked,
        "asr_valid": round(100.0 * counts["succ"] / decided, 1) if decided else None,
        "valid_rate": round(100.0 * decided / len(cases), 1) if cases else None,
    }
    return summary, rows
