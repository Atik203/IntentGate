"""Phase 6 P0-1: per-role endpoint resolution (CLI > env) + flag wiring."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from harness.common import (
    add_endpoint_args,
    resolve_api_key,
    resolve_base_url,
    resolve_reasoning_effort,
)

ROOT = Path(__file__).resolve().parents[1]


def test_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("AGENT_BASE_URL", "http://env:11434/v1")
    assert resolve_base_url("http://cli:11434/v1", "agent") == "http://cli:11434/v1"


def test_agent_falls_back_to_qwen_legacy(monkeypatch):
    monkeypatch.delenv("AGENT_BASE_URL", raising=False)
    monkeypatch.setenv("QWEN_BASE_URL", "http://qwen:11434/v1")
    assert resolve_base_url(None, "agent") == "http://qwen:11434/v1"


def test_agent_prefers_agent_base_url(monkeypatch):
    monkeypatch.setenv("AGENT_BASE_URL", "http://agent:11434/v1")
    monkeypatch.setenv("QWEN_BASE_URL", "http://qwen:11434/v1")
    assert resolve_base_url(None, "agent") == "http://agent:11434/v1"


def test_parser_has_no_qwen_fallback(monkeypatch):
    monkeypatch.delenv("PARSER_BASE_URL", raising=False)
    monkeypatch.setenv("QWEN_BASE_URL", "http://qwen:11434/v1")
    assert resolve_base_url(None, "parser") is None


def test_empty_string_counts_as_unset(monkeypatch):
    monkeypatch.setenv("AGENT_BASE_URL", "")
    monkeypatch.delenv("QWEN_BASE_URL", raising=False)
    assert resolve_base_url(None, "agent") is None


def test_api_key_fallback_mirrors_base_url(monkeypatch):
    monkeypatch.delenv("AGENT_API_KEY", raising=False)
    monkeypatch.setenv("QWEN_API_KEY", "qwen-key")
    assert resolve_api_key(None, "agent") == "qwen-key"
    monkeypatch.setenv("QWEN_API_KEY", "qwen-key")
    assert resolve_api_key(None, "parser") is None


def test_endpoint_flags_registered_with_none_defaults():
    ap = add_endpoint_args(argparse.ArgumentParser())
    args = ap.parse_args([])
    assert args.agent_base_url is None
    assert args.parser_base_url is None
    assert args.agent_api_key is None
    assert args.parser_api_key is None
    assert args.agent_reasoning_effort is None
    args = ap.parse_args(["--agent-base-url", "http://x/v1"])
    assert args.agent_base_url == "http://x/v1"


def test_reasoning_effort_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("AGENT_REASONING_EFFORT", "low")
    assert resolve_reasoning_effort("none", "agent") == "none"


def test_reasoning_effort_agent_env(monkeypatch):
    monkeypatch.setenv("AGENT_REASONING_EFFORT", "none")
    assert resolve_reasoning_effort(None, "agent") == "none"


def test_reasoning_effort_parser_isolated(monkeypatch):
    monkeypatch.setenv("AGENT_REASONING_EFFORT", "none")
    monkeypatch.delenv("PARSER_REASONING_EFFORT", raising=False)
    assert resolve_reasoning_effort(None, "parser") is None


def test_reasoning_effort_unset_returns_none(monkeypatch):
    monkeypatch.delenv("AGENT_REASONING_EFFORT", raising=False)
    assert resolve_reasoning_effort(None, "agent") is None


def test_llm_client_forwards_reasoning_effort(monkeypatch):
    from intent_gate.agent.base import LLMClient

    captured = {}

    class _FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)

            class _Msg:
                content = "{}"

            class _Choice:
                message = _Msg()

            class _Resp:
                choices = [_Choice()]
                usage = None

            return _Resp()

    client = LLMClient(model_id="qwen3.5:4b", reasoning_effort="none")
    client._client = type("_C", (), {"chat": type("_Chat", (), {"completions": _FakeCompletions()})()})()
    client.call([{"role": "user", "content": "hi"}])
    assert captured["reasoning_effort"] == "none"


def test_llm_client_omits_reasoning_effort_when_unset():
    from intent_gate.agent.base import LLMClient

    captured = {}

    class _FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)

            class _Msg:
                content = "{}"

            class _Choice:
                message = _Msg()

            class _Resp:
                choices = [_Choice()]
                usage = None

            return _Resp()

    client = LLMClient(model_id="gpt-4o-mini")
    client._client = type("_C", (), {"chat": type("_Chat", (), {"completions": _FakeCompletions()})()})()
    client.call([{"role": "user", "content": "hi"}])
    assert "reasoning_effort" not in captured


def test_llm_client_omits_temperature_when_model_rejects_it():
    from intent_gate.agent.base import LLMClient

    calls = []

    class _FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            if "temperature" in kwargs:
                raise Exception(
                    "Error code: 400 - Unsupported value: 'temperature' does not support 0.0 "
                    "with this model."
                )

            class _Msg:
                content = "ok"

            class _Choice:
                message = _Msg()

            class _Resp:
                choices = [_Choice()]
                usage = None

            return _Resp()

    client = LLMClient(model_id="gpt-6-luna")
    client._client = type("_C", (), {"chat": type("_Chat", (), {"completions": _FakeCompletions()})()})()
    assert client.call([{"role": "user", "content": "hi"}]) == "ok"
    assert "temperature" in calls[0]
    assert "temperature" not in calls[1]
    assert client._send_temperature is False


def test_llm_client_reraises_other_errors():
    import pytest

    from intent_gate.agent.base import LLMClient

    class _FakeCompletions:
        def create(self, **kwargs):
            raise Exception("Error code: 429 - rate limit exceeded")

    client = LLMClient(model_id="gpt-4o-mini")
    client._client = type("_C", (), {"chat": type("_Chat", (), {"completions": _FakeCompletions()})()})()
    with pytest.raises(Exception, match="rate limit"):
        client.call([{"role": "user", "content": "hi"}])
    assert client._send_temperature is True


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_injecagent_ours_requires_out():
    result = _run("scripts/run_injecagent_ours.py", "--per-split", "1")
    assert result.returncode != 0
    assert "--out" in result.stderr


def test_mcptox_ours_requires_out():
    result = _run("scripts/run_mcptox_ours.py", "--limit", "1")
    assert result.returncode != 0
    assert "--out" in result.stderr


def test_harness_injecagent_requires_report():
    result = _run("harness/run_injecagent.py", "--cases", "x")
    assert result.returncode != 0
    assert "--report" in result.stderr


def test_harness_mcptox_requires_report():
    result = _run("harness/run_mcptox.py")
    assert result.returncode != 0
    assert "--report" in result.stderr
