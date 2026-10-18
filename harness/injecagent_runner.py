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
from harness.gate_policy import decide_call
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
    policy = policy_factory(case.user_instruction) if policy_factory else None
    if policy is not None:
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
    if policy is not None:
        target = case.attacker_tools[0] if case.attacker_tools else ""
        target_blocked = False
        for call in calls:
            event = decide_call(policy, call)
            gate_events.append(event)
            if call.name == target and not event["allowed"]:
                target_blocked = True
        if target_blocked and evaluation["eval"] == "succ":
            gate_blocked = True
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


def _run_each(
    cases: list,
    llm,
    tool_dict: dict,
    policy_factory,
    handle,
    progress,
    counts: dict,
    gate_blocked: int,
    rows: list,
    prompt_type: str = "InjecAgent",
) -> tuple[dict, list, int]:
    for case in cases:
        result = run_case(case, llm, tool_dict, prompt_type=prompt_type, policy_factory=policy_factory)
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
            handle.flush()
        if progress:
            progress(result, case)
    return counts, rows, gate_blocked


def _read_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def run_cases(
    cases: list,
    llm,
    tool_dict: dict,
    policy_factory=None,
    jsonl_path: str | Path | None = None,
    progress=None,
    resume: bool = False,
    prompt_type: str = "InjecAgent",
) -> tuple[dict, list]:
    """Run cases and return (summary, rows); writes JSONL when a path is given.

    resume=True skips cases already recorded in the JSONL and appends, so an interrupted
    run continues from its last completed case instead of restarting. The returned summary
    always covers the full case list, not just the newly run subset.
    """
    counts = {"succ": 0, "unsucc": 0, "invalid": 0, "error": 0}
    gate_blocked = 0
    rows: list = []
    remaining = list(cases)
    mode = "w"
    if jsonl_path and resume and Path(jsonl_path).exists():
        done = _read_jsonl(jsonl_path)
        seen = {r.get("case_id") for r in done}
        for row in done:
            counts[row.get("eval")] = counts.get(row.get("eval"), 0) + 1
            gate_blocked += int(bool(row.get("gate_blocked")))
        rows.extend(done)
        remaining = [c for c in cases if c.case_id not in seen]
        mode = "a"
    if jsonl_path:
        with Path(jsonl_path).open(mode, encoding="utf-8") as handle:
            counts, rows, gate_blocked = _run_each(
                remaining, llm, tool_dict, policy_factory, handle, progress, counts, gate_blocked, rows,
                prompt_type=prompt_type,
            )
    else:
        counts, rows, gate_blocked = _run_each(
            remaining, llm, tool_dict, policy_factory, None, progress, counts, gate_blocked, rows,
            prompt_type=prompt_type,
        )
    decided = counts["succ"] + counts["unsucc"]
    summary = {
        "n": len(cases),
        "counts": counts,
        "gate_blocked": gate_blocked,
        "asr_valid": round(100.0 * counts["succ"] / decided, 1) if decided else None,
        "valid_rate": round(100.0 * decided / len(cases), 1) if cases else None,
    }
    return summary, rows
