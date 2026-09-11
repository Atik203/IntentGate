"""Gate-ready case runner for InjecAgent (blueprint Sec 5 Comp 1).

B1 uses it with a plain executor; B2/ours will wrap the executor with middleware.
Prompts are vendored (`harness/prompts/injecagent.py`) so all conditions share
identical, byte-stable input.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from harness.adapters.injecagent import InjecAgentCase
from harness.parsing import evaluate_output, extract_tool_calls, parse_react_output, truncate_at_marker
from harness.prompts.injecagent import PROMPT_DICT
from intent_gate.types import ToolCall


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
    case: InjecAgentCase, llm, tool_dict: dict, prompt_type: str = "InjecAgent", temperature: float = 0.0
) -> CaseResult:
    try:
        output = llm.call(build_messages(case, tool_dict, prompt_type), temperature=temperature)
    except Exception as exc:
        return CaseResult(case_id=case.case_id, eval="error", output="", error=str(exc))
    evaluation = evaluate_output(
        output, case.attacker_tools[0], case.attacker_tools, case.user_tool, case.attacker_instruction
    )
    info_list = parse_react_output(truncate_at_marker(output or "").strip())
    return CaseResult(
        case_id=case.case_id,
        eval=evaluation["eval"],
        output=output or "",
        tool_calls=extract_tool_calls(info_list),
        invalid_reason=evaluation.get("invalid_reason", ""),
        attacker_params=evaluation.get("Attacker Tool Parameters", ""),
        attacker_thought=evaluation.get("Attacker Tool Thought", ""),
    )


def serialize_calls(calls: list) -> list:
    return [{"name": c.name, "parameters": c.parameters, "source": c.source} for c in calls]
