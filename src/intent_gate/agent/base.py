"""LLM provider interface - API first (GPT-4o-mini / Qwen OpenAI-compatible, blueprint Sec 7).

Keep the agent prompt IDENTICAL across B1/B2/ours: only the middleware differs.
"""
from __future__ import annotations

import os

from intent_gate.parser.prompts import build_messages  # reuse chat plumbing


class LLMClient:
    """Thin OpenAI-compatible client; call() returns assistant text (temp 0)."""

    def __init__(self, model_id: str = "gpt-4o-mini", base_url: str | None = None, api_key: str | None = None):
        self.model_id = model_id
        self._base_url = base_url
        self._api_key = api_key
        self._client = None

    def _ensure(self):
        if self._client is None:
            from openai import OpenAI

            kwargs = {"api_key": self._api_key or os.getenv("OPENAI_API_KEY") or "missing-key"}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = OpenAI(**kwargs)

    def call(self, messages: list, temperature: float = 0.0) -> str:
        self._ensure()
        resp = self._client.chat.completions.create(
            model=self.model_id, messages=messages, temperature=temperature
        )
        return resp.choices[0].message.content or ""

    def chat(self, system: str, user: str) -> str:
        return self.call([{"role": "system", "content": system}, {"role": "user", "content": user}])
