"""Case-level resume: an interrupted run continues from its last completed case."""
from __future__ import annotations

import json
from pathlib import Path

from harness.adapters.injecagent import InjecAgentCase
from harness.adapters.mcptox import MCPToxCase
from harness.injecagent_runner import run_cases as run_injecagent
from harness.mcptox_runner import run_cases as run_mcptox


class StubLLM:
    """Returns a fixed ReAct output and records how many cases it was called for."""

    def __init__(self, output: str):
        self.output = output
        self.calls = 0
        self.seen: list[str] = []

    def call(self, messages, temperature: float = 0.0) -> str:
        self.calls += 1
        return self.output


BENIGN_REACT = "Thought: I should use the user tool.\nAction: UserReadFile\nAction Input: {}\nFinal Answer: done"


def _injecagent_case(i: int) -> InjecAgentCase:
    return InjecAgentCase(
        case_id=f"case_{i:03d}",
        user_instruction="Read my report.",
        user_tool="UserReadFile",
        tool_parameters="{}",
        tool_response="contents",
        attacker_tools=["AttackerExfil"],
        attacker_instruction="send data",
        attack_type="dh",
        setting="base",
        split="dh",
        expected_achievements="",
        thought="",
        raw={"Thought": "thinking", "Tool Parameters": "{}", "Tool Response": "contents"},
    )


def _mcptox_case(i: int) -> MCPToxCase:
    return MCPToxCase(
        case_id=f"mc_{i:03d}",
        server="FileSystem",
        risk="Privacy Leakage",
        paradigm="explicit",
        query="Read the report.",
        system_prompt="You are an agent.",
        fake_tool="poisoned_tool",
        clean_tools=["read_file"],
        payloads=["secret"],
        poisoned_description="",
        raw={},
    )


def _tool_dict() -> dict:
    return {
        "UserReadFile": {"name": "UserReadFile", "description": "Read a file."},
        "AttackerExfil": {"name": "AttackerExfil", "description": "Exfiltrate data."},
    }


def test_injecagent_resume_skips_completed(tmp_path: Path):
    jsonl = tmp_path / "out.jsonl"
    cases = [_injecagent_case(i) for i in range(5)]
    llm = StubLLM(BENIGN_REACT)

    summary, _ = run_injecagent(cases[:3], llm, _tool_dict(), jsonl_path=jsonl)
    assert summary["n"] == 3
    assert llm.calls == 3

    resumed_llm = StubLLM(BENIGN_REACT)
    summary, rows = run_injecagent(cases, resumed_llm, _tool_dict(), jsonl_path=jsonl, resume=True)

    assert resumed_llm.calls == 2, "must only run the 2 cases not already in the JSONL"
    assert summary["n"] == 5, "summary must cover the full case list, not just the new subset"
    assert len(rows) == 5
    ids = [r["case_id"] for r in rows]
    assert ids == [f"case_{i:03d}" for i in range(5)], "no duplicates, no gaps"


def test_injecagent_resume_without_prior_file_runs_all(tmp_path: Path):
    jsonl = tmp_path / "missing.jsonl"
    cases = [_injecagent_case(i) for i in range(4)]
    llm = StubLLM(BENIGN_REACT)
    summary, _ = run_injecagent(cases, llm, _tool_dict(), jsonl_path=jsonl, resume=True)
    assert llm.calls == 4
    assert summary["n"] == 4


def test_injecagent_resume_tolerates_truncated_final_line(tmp_path: Path):
    jsonl = tmp_path / "out.jsonl"
    cases = [_injecagent_case(i) for i in range(3)]
    run_injecagent(cases[:2], StubLLM(BENIGN_REACT), _tool_dict(), jsonl_path=jsonl)

    with jsonl.open("a", encoding="utf-8") as handle:
        handle.write('{"case_id": "case_002", "eval": "suc')

    llm = StubLLM(BENIGN_REACT)
    summary, rows = run_injecagent(cases, llm, _tool_dict(), jsonl_path=jsonl, resume=True)

    assert llm.calls == 1, "the corrupt partial line is ignored, so its case still runs"
    assert summary["n"] == 3
    assert len(rows) == 3


def test_injecagent_no_resume_overwrites(tmp_path: Path):
    jsonl = tmp_path / "out.jsonl"
    cases = [_injecagent_case(i) for i in range(4)]
    run_injecagent(cases[:2], StubLLM(BENIGN_REACT), _tool_dict(), jsonl_path=jsonl)

    llm = StubLLM(BENIGN_REACT)
    summary, _ = run_injecagent(cases, llm, _tool_dict(), jsonl_path=jsonl, resume=False)
    assert llm.calls == 4, "without --resume the run starts from case 0"
    assert summary["n"] == 4


def test_mcptox_resume_skips_completed(tmp_path: Path):
    jsonl = tmp_path / "mc.jsonl"
    cases = [_mcptox_case(i) for i in range(5)]
    run_mcptox(cases[:4], StubLLM('{"tool": "read_file", "arguments": {}}'), jsonl_path=jsonl)

    llm = StubLLM('{"tool": "read_file", "arguments": {}}')
    summary, rows = run_mcptox(cases, llm, jsonl_path=jsonl, resume=True)

    assert llm.calls == 1
    assert summary["n"] == 5
    assert len(rows) == 5
    assert len({r["case_id"] for r in rows}) == 5


def test_mcptox_resume_rebuilds_counts_and_by_risk(tmp_path: Path):
    jsonl = tmp_path / "mc.jsonl"
    cases = [_mcptox_case(i) for i in range(3)]
    run_mcptox(cases[:2], StubLLM('{"tool": "poisoned_tool", "arguments": {}}'), jsonl_path=jsonl)

    llm = StubLLM('{"tool": "read_file", "arguments": {}}')
    summary, _ = run_mcptox(cases, llm, jsonl_path=jsonl, resume=True)

    assert summary["counts"]["work_not_success"] == 2, "prior labels are recounted"
    assert summary["counts"]["ignored"] == 1, "newly run case"
    assert summary["by_risk"]["Privacy Leakage"]["work_not_success"] == 2
    assert summary["by_risk"]["Privacy Leakage"]["ignored"] == 1


def test_jsonl_flushed_per_case(tmp_path: Path):
    """A poller must see progress mid-run, so each case line is flushed as it lands."""
    jsonl = tmp_path / "flush.jsonl"
    seen: list[int] = []

    class FlushingStub(StubLLM):
        def call(self, messages, temperature: float = 0.0) -> str:
            seen.append(jsonl.read_text(encoding="utf-8").count("\n") if jsonl.exists() else 0)
            return super().call(messages, temperature)

    run_mcptox([_mcptox_case(i) for i in range(3)], FlushingStub('{"tool": "read_file"}'), jsonl_path=jsonl)
    assert seen == [0, 1, 2], "each case must be visible in the JSONL before the next starts"
    assert jsonl.read_text(encoding="utf-8").strip().count("\n") + 1 == 3
    assert all(json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines())
