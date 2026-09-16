"""AgentLoop x GateMiddleware integration: ReAct -> gate -> executor (blueprint Sec 5/11)."""
from __future__ import annotations

import json

from intent_gate.agent.react import AgentLoop, parse_proposal
from intent_gate.agent.tools import ToolRegistry
from intent_gate.gate.middleware import GateMiddleware
from intent_gate.gate.trace import TraceLogger
from intent_gate.types import ToolCall
from tests.fixtures.cases import FLIGHT_CONTRACT


class FakeLLM:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def call(self, messages, temperature=0.0, response_format=None):
        self.calls.append({"messages": messages, "temperature": temperature})
        return self.outputs.pop(0)


class Recorder:
    def __init__(self):
        self.calls = []

    def __call__(self, name, params):
        self.calls.append((name, params))
        return f"ok:{name}"


def build_loop(outputs, tmp_path, max_steps=15):
    executor = Recorder()
    gate = GateMiddleware(FLIGHT_CONTRACT, executor, TraceLogger(tmp_path / "trace.jsonl"))
    registry = ToolRegistry()
    registry.register("search_flights", lambda **kw: "flights", "Search flights by destination/date")
    registry.register("read_results", lambda **kw: "results", "Read the latest search results")
    loop = AgentLoop(FakeLLM(outputs), registry, gate.execute, FLIGHT_CONTRACT.raw_request, max_steps=max_steps)
    return loop, gate, executor


def test_legit_react_action_executes_and_stops(tmp_path):
    outputs = [
        'Thought: search\nAction: search_flights\nAction Input: {"to": "Berlin", "date": "next Friday"}',
        "Thought: done\nFinal Answer: cheapest flight held",
    ]
    loop, _, executor = build_loop(outputs, tmp_path)
    result = loop.run()
    assert result.stopped == "final_answer"
    assert executor.calls and executor.calls[0][0] == "search_flights"
    assert result.steps[0].observation.startswith("ok:")
    assert result.final_answer == "cheapest flight held"


def test_hijack_action_blocked_before_executor(tmp_path):
    outputs = [
        'Thought: pay\nAction: transfer_money\nAction Input: {"amount": 500, "to": "attacker"}',
        "Final Answer: cannot do that",
    ]
    loop, _, executor = build_loop(outputs, tmp_path)
    result = loop.run()
    assert executor.calls == []
    assert "Blocked" in result.steps[0].observation


def test_step_cap_stops_runaway_loop(tmp_path):
    outputs = ['Action: read_results\nAction Input: {"query": "x"}'] * 3
    loop, _, executor = build_loop(outputs, tmp_path, max_steps=3)
    result = loop.run()
    assert result.stopped == "step_cap"
    assert len(result.steps) == 3
    assert len(executor.calls) == 3


def test_unparsed_output_stops_loop(tmp_path):
    loop, _, executor = build_loop(["no action here"], tmp_path)
    result = loop.run()
    assert result.stopped == "unparsed"
    assert executor.calls == []


def test_system_prompt_stable_and_contains_tools(tmp_path):
    outputs = [
        'Action: read_results\nAction Input: {"query": "x"}',
        "Final Answer: done",
    ]
    loop, _, _ = build_loop(outputs, tmp_path)
    loop.run()
    first = loop.llm.calls[0]["messages"][0]["content"]
    second = loop.llm.calls[1]["messages"][0]["content"]
    assert first == second
    assert "search_flights" in first and "read_results" in first


def test_one_trace_record_per_executed_call(tmp_path):
    outputs = [
        'Action: search_flights\nAction Input: {"to": "Berlin"}',
        "Final Answer: ok",
    ]
    loop, gate, _ = build_loop(outputs, tmp_path)
    loop.run()
    lines = gate.trace.path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_trace_records_embedding_metadata_per_call(tmp_path):
    outputs = [
        'Action: search_flights\nAction Input: {"to": "Berlin"}',
        "Final Answer: ok",
    ]
    loop, gate, _ = build_loop(outputs, tmp_path)
    loop.run()
    row = json.loads(gate.trace.path.read_text(encoding="utf-8").strip())
    assert row["embedding"]["backend"] == "hash-fallback"
    assert row["embedding"]["model_hash"]


def test_parse_proposal_json_fallback():
    call, final = parse_proposal('{"name": "read_results", "parameters": {"query": "x"}}')
    assert call is not None and call.name == "read_results"
    assert final is None


def test_parse_proposal_final_answer_wins():
    call, final = parse_proposal("Action: read_results\nFinal Answer: done")
    assert call is None
    assert final == "done"


class CountingBackend:
    def __init__(self):
        self.batches = []

    def embed(self, texts):
        import numpy as np

        self.batches.append(list(texts))
        return np.asarray([[1.0, 0.0] for _ in texts], dtype=float)

    @property
    def metadata(self) -> dict:
        return {"model_id": "counting", "model_hash": "test", "backend": "test"}


def test_contract_embedding_is_cached_across_calls(tmp_path):
    backend = CountingBackend()
    gate = GateMiddleware(FLIGHT_CONTRACT, Recorder(), TraceLogger(tmp_path / "t.jsonl"), backend=backend)
    gate.check(ToolCall(name="search_flights", parameters={"to": "Berlin"}))
    gate.check(ToolCall(name="read_results", parameters={"query": "x"}))
    contract_text = FLIGHT_CONTRACT.contract_text()
    embedded_contract = [t for batch in backend.batches for t in batch if t == contract_text]
    assert len(embedded_contract) == 1
    assert all(len(batch) == 1 for batch in backend.batches)


def test_immediate_final_answer_makes_no_calls(tmp_path):
    loop, _, executor = build_loop(["Final Answer: nothing to do"], tmp_path)
    result = loop.run()
    assert result.steps == []
    assert result.stopped == "final_answer"
    assert executor.calls == []
