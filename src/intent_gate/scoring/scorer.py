"""Score fusion: S = alpha*S_sem + (1-alpha)*S_rule with critical veto (blueprint Sec 5 Comp 2)."""
from __future__ import annotations

import numpy as np

from intent_gate.scoring.embeddings import EmbeddingBackend, cosine
from intent_gate.scoring.rules import evaluate_rules
from intent_gate.types import IntentContract, ToolCall


def score_call(
    contract: IntentContract,
    call: ToolCall,
    backend: EmbeddingBackend | None = None,
    alpha: float = 0.7,
    contract_vec: np.ndarray | None = None,
) -> tuple[float, float, float, bool, str]:
    """Return (S, S_sem, S_rule, rule_triggered, reason). S in [0,1], deterministic.

    ``contract_vec`` is the cached, frozen contract embedding (blueprint Sec 5/6): the gate
    embeds the contract once per session and passes it here, so only the call is embedded.
    """
    backend = backend or EmbeddingBackend()
    s_rule, triggered, reason = evaluate_rules(contract, call)
    if contract_vec is None:
        vecs = backend.embed([contract.contract_text(), call.naturalized()])
        contract_vec, call_vec = vecs[0], vecs[1]
    else:
        call_vec = backend.embed([call.naturalized()])[0]
    s_sem = (cosine(contract_vec, call_vec) + 1.0) / 2.0  # map [-1,1] -> [0,1]
    s_sem = float(np.clip(s_sem, 0.0, 1.0))
    if triggered and s_rule == 0.0:
        return 0.0, s_sem, s_rule, triggered, reason  # hard veto
    s = float(np.clip(alpha * s_sem + (1.0 - alpha) * s_rule, 0.0, 1.0))
    return s, s_sem, s_rule, triggered, reason
