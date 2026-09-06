"""Ablations A1-A4 (blueprint Sec 9): isolate each component."""
from __future__ import annotations

import numpy as np

from intent_gate.scoring.embeddings import EmbeddingBackend, cosine
from intent_gate.scoring.rules import evaluate_rules
from intent_gate.types import IntentContract, ToolCall


def ablation_semantic_only(contract: IntentContract, call: ToolCall, backend: EmbeddingBackend | None = None) -> float:
    """A1: rule engine removed - pure embedding similarity (mapped to [0,1])."""
    backend = backend or EmbeddingBackend()
    v = backend.embed([contract.contract_text(), call.naturalized()])
    return float(np.clip((cosine(v[0], v[1]) + 1.0) / 2.0, 0.0, 1.0))


def ablation_rule_only(contract: IntentContract, call: ToolCall) -> float:
    """A2: semantic scorer removed - deterministic rules only."""
    s_rule, _, _ = evaluate_rules(contract, call)
    return s_rule


def ablation_raw_request(contract: IntentContract, call: ToolCall, backend: EmbeddingBackend | None = None) -> float:
    """A3: raw request embedding instead of structured contract text."""
    backend = backend or EmbeddingBackend()
    v = backend.embed([contract.raw_request or contract.goals[0], call.naturalized()])
    return float(np.clip((cosine(v[0], v[1]) + 1.0) / 2.0, 0.0, 1.0))
