"""Ablation modes (blueprint Sec 9 A1-A3): component isolation in the gate middleware."""
from __future__ import annotations

import numpy as np

from harness.gate_policy import build_policy_factory
from intent_gate.gate.middleware import GateMiddleware
from intent_gate.gate.trace import TraceLogger
from intent_gate.parser.parser import IntentParser
from intent_gate.types import ToolCall
from tests.fixtures.cases import FLIGHT_CONTRACT, HIJACK_CALLS


class NoEmbedBackend:
    def __init__(self):
        self.batches = []

    def embed(self, texts):
        self.batches.append(list(texts))
        raise AssertionError("embeddings must not be called in rule-only mode")

    @property
    def metadata(self) -> dict:
        return {"model_id": "none", "model_hash": "none", "backend": "none"}


class CountingBackend:
    def __init__(self):
        self.batches = []

    def embed(self, texts):
        self.batches.append(list(texts))
        return np.asarray([[1.0, 0.0] for _ in texts], dtype=float)

    @property
    def metadata(self) -> dict:
        return {"model_id": "counting", "model_hash": "test", "backend": "test"}


def _gate(tmp_path, **kwargs):
    return GateMiddleware(FLIGHT_CONTRACT, lambda name, params: "ok", TraceLogger(tmp_path / "t.jsonl"), **kwargs)


def test_semantic_only_ignores_rule_veto(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "intent_gate.gate.middleware.score_call",
        lambda *args, **kwargs: (0.0, 0.9, 0.0, True, "veto"),
    )
    normal = _gate(tmp_path).check(HIJACK_CALLS[0][1])
    assert normal.decision == "block"

    semantic = _gate(tmp_path, ablation="semantic-only").check(HIJACK_CALLS[0][1])
    assert semantic.decision == "allow"
    assert semantic.score == 0.9


def test_rule_only_skips_embeddings_and_uses_rules(tmp_path):
    backend = NoEmbedBackend()
    gate = GateMiddleware(
        FLIGHT_CONTRACT,
        lambda name, params: "ok",
        TraceLogger(tmp_path / "t.jsonl"),
        backend=backend,
        ablation="rule-only",
    )
    blocked = gate.check(ToolCall(name="transfer_money", parameters={"amount": 500}))
    assert blocked.decision == "block" and blocked.score == 0.0
    allowed = gate.check(ToolCall(name="search_flights", parameters={"to": "Berlin"}))
    assert allowed.decision == "allow" and allowed.score == 1.0
    assert backend.batches == []


def test_raw_request_ablation_uses_raw_request_vector(tmp_path):
    backend = CountingBackend()
    gate = GateMiddleware(
        FLIGHT_CONTRACT,
        lambda name, params: "ok",
        TraceLogger(tmp_path / "t.jsonl"),
        backend=backend,
        ablation="raw-request",
    )
    gate.check(ToolCall(name="search_flights", parameters={"to": "Berlin"}))
    assert backend.batches[0] == [FLIGHT_CONTRACT.raw_request]


def test_normal_mode_uses_contract_text(tmp_path):
    backend = CountingBackend()
    gate = GateMiddleware(
        FLIGHT_CONTRACT,
        lambda name, params: "ok",
        TraceLogger(tmp_path / "t.jsonl"),
        backend=backend,
    )
    gate.check(ToolCall(name="search_flights", parameters={"to": "Berlin"}))
    assert backend.batches[0] == [FLIGHT_CONTRACT.contract_text()]


def test_build_policy_factory_passes_ablation():
    factory = build_policy_factory("ours", parser=IntentParser(), ablation="semantic-only")
    policy = factory("Find the cheapest flight to Berlin and hold it - don't pay yet.")
    assert policy.gate.ablation == "semantic-only"


def test_build_policy_factory_rejects_unknown_ablation_combination():
    import pytest

    with pytest.raises(ValueError):
        build_policy_factory("ours", parser=IntentParser(), ablation="bogus")
