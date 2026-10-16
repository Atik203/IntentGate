"""Cost estimation + LLMClient usage tracking (Phase 5 reports)."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from intent_gate.agent.base import LLMClient
from intent_gate.eval.cost import estimate_cost_usd, estimate_usage_cost


def test_estimate_cost_known_model():
    assert estimate_cost_usd("gpt-4o-mini", 1_000_000, 1_000_000) == pytest.approx(0.75)


def test_estimate_cost_unknown_model():
    assert estimate_cost_usd("mystery-model", 1000, 1000) is None


def test_estimate_usage_cost_from_usage_dict():
    usage = {"model_id": "gpt-4o-mini", "prompt_tokens": 1000, "completion_tokens": 500}
    assert estimate_usage_cost(usage) == pytest.approx(0.00015 + 0.0003)


def test_estimate_usage_cost_empty():
    assert estimate_usage_cost(None) is None
    assert estimate_usage_cost({}) is None


class _FakeCompletions:
    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="hi"))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
        )


def test_llm_client_tracks_usage():
    client = LLMClient(model_id="gpt-4o-mini")
    client._client = SimpleNamespace(chat=SimpleNamespace(completions=_FakeCompletions()))
    assert client.call([{"role": "user", "content": "x"}]) == "hi"
    assert client.usage == {
        "model_id": "gpt-4o-mini",
        "calls": 1,
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
    }
