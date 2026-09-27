"""LLM provider interface - API first (GPT-4o-mini / Qwen OpenAI-compatible, blueprint Sec 7).

Keep the agent prompt IDENTICAL across B1/B2/ours: only the middleware differs.
Tracks token usage per client for the Phase 5 cost reports.
"""
from __future__ import annotations

import os


class LLMClient:
    """Thin OpenAI-compatible client; call() returns assistant text (temp 0)."""

    def __init__(self, model_id: str = "gpt-4o-mini", base_url: str | None = None, api_key: str | None = None):
        self.model_id = model_id
        self._base_url = base_url
        self._api_key = api_key
        self._client = None
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def _ensure(self):
        if self._client is None:
            from openai import OpenAI

            kwargs = {"api_key": self._api_key or os.getenv("OPENAI_API_KEY") or "missing-key"}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = OpenAI(**kwargs)

    def call(self, messages: list, temperature: float = 0.0, response_format: dict | None = None) -> str:
        self._ensure()
        kwargs = {"response_format": response_format} if response_format else {}
        resp = self._client.chat.completions.create(
            model=self.model_id, messages=messages, temperature=temperature, **kwargs
        )
        self.calls += 1
        usage = getattr(resp, "usage", None)
        if usage is not None:
            self.prompt_tokens += int(getattr(usage, "prompt_tokens", 0) or 0)
            self.completion_tokens += int(getattr(usage, "completion_tokens", 0) or 0)
        return resp.choices[0].message.content or ""

    @property
    def usage(self) -> dict:
        return {
            "model_id": self.model_id,
            "calls": self.calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens,
        }

    def chat(self, system: str, user: str) -> str:
        return self.call([{"role": "system", "content": system}, {"role": "user", "content": user}])
