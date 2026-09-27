"""API cost estimation for run reports (Phase 5). List-price estimates, not billing."""
from __future__ import annotations

PRICES_PER_MILLION_TOKENS = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


def estimate_cost_usd(model_id: str, prompt_tokens: int, completion_tokens: int) -> float | None:
    """Return estimated USD cost for a model, or None when the model is not priced."""
    price = PRICES_PER_MILLION_TOKENS.get(model_id)
    if price is None:
        return None
    return prompt_tokens / 1_000_000 * price["input"] + completion_tokens / 1_000_000 * price["output"]


def estimate_usage_cost(usage: dict | None) -> float | None:
    """Estimate USD cost from an ``LLMClient.usage`` dict (None when unknown/unpriced)."""
    if not usage:
        return None
    return estimate_cost_usd(
        str(usage.get("model_id", "")),
        int(usage.get("prompt_tokens", 0) or 0),
        int(usage.get("completion_tokens", 0) or 0),
    )
