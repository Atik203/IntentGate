"""Optional verbatim-echo guard for free-text tool arguments (E26c).

The frozen scorer embeds full call text. A trusted-request span copied into a free-text
argument can therefore raise the semantic score above tau. This module adds a post-hoc,
deterministic guard that flags long verbatim spans from the contract request inside
free-text arguments. It is evaluated offline and does not change the frozen Phase 5 gate.
"""
from __future__ import annotations

import re

from intent_gate.types import IntentContract, ToolCall

FREE_TEXT_KEYS = {
    "body",
    "caption",
    "comment",
    "content",
    "description",
    "keyword",
    "keywords",
    "message",
    "note",
    "prompt",
    "q",
    "query",
    "search",
    "search_term",
    "search_terms",
    "subject",
    "term",
    "terms",
    "text",
    "title",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens; punctuation is ignored."""
    return _TOKEN_RE.findall((text or "").lower())


def find_verbatim_span(request: str, value: str) -> int:
    """Return the longest contiguous token span shared by request and value."""
    left, right = tokenize(request), tokenize(value)
    if not left or not right:
        return 0
    previous = [0] * (len(right) + 1)
    best = 0
    for i in range(1, len(left) + 1):
        current = [0] * (len(right) + 1)
        for j in range(1, len(right) + 1):
            if left[i - 1] == right[j - 1]:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current
    return best


def _iter_text_values(call: ToolCall):
    for key, value in call.parameters.items():
        if key not in FREE_TEXT_KEYS:
            continue
        if isinstance(value, str):
            yield key, value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    yield key, item


def echo_guard(
    contract: IntentContract,
    call: ToolCall,
    min_tokens: int = 8,
) -> dict:
    """Return guard evidence for one call; triggered means a long request span was copied."""
    parts = [contract.raw_request or "", *contract.goals, *contract.permitted_data_access]
    request = " ".join(part for part in parts if part).strip()
    if not request or min_tokens <= 0:
        return {"triggered": False, "min_tokens": min_tokens, "hits": []}
    hits = []
    for key, value in _iter_text_values(call):
        span = find_verbatim_span(request, value)
        if span >= min_tokens:
            hits.append({"key": key, "span": span})
    return {"triggered": bool(hits), "min_tokens": min_tokens, "hits": hits}
