"""Phase 6 P0-1: per-role endpoint resolution (CLI > env) + flag wiring."""
from __future__ import annotations

import argparse

from harness.common import add_endpoint_args, resolve_api_key, resolve_base_url


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
    args = ap.parse_args(["--agent-base-url", "http://x/v1"])
    assert args.agent_base_url == "http://x/v1"
