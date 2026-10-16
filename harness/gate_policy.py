"""Gate policies for benchmark conditions: none / ours / toolgate (blueprint Sec 6/9).

A policy answers one question per proposed call: ``decide(call)`` returns the decision record
(``allowed`` + condition-specific evidence such as ``S``/``latency_ms``/``no_contract``), used
for per-case JSONL events in Phase 5. ``allows`` keeps the boolean convenience API.

Policies are built from the *trusted* user request BEFORE any attacker content (tool definitions,
injected observations) is assembled - the ordering invariant from blueprint Sec 10.
"""
from __future__ import annotations

import time
from collections.abc import Callable

from intent_gate.baselines.toolgate.checker import ToolGateChecker
from intent_gate.gate.middleware import GateMiddleware
from intent_gate.gate.trace import TraceLogger
from intent_gate.parser.parser import IntentParser
from intent_gate.scoring.embeddings import EmbeddingBackend
from intent_gate.types import ToolCall


class AllowAllPolicy:
    name = "none"

    def decide(self, call: ToolCall) -> dict:
        return {"name": call.name, "allowed": True, "decision": "allow", "latency_ms": 0.0}

    def allows(self, call: ToolCall) -> bool:
        return True


class OursPolicy:
    name = "ours"

    def __init__(self, gate: GateMiddleware):
        self.gate = gate

    def decide(self, call: ToolCall) -> dict:
        result = self.gate.check(call)
        return {
            "name": call.name,
            "allowed": result.decision == "allow",
            "decision": result.decision,
            "S": result.score,
            "S_sem": result.score_sem,
            "S_rule": result.score_rule,
            "rule_triggered": result.rule_triggered,
            "reason": result.reason,
            "latency_ms": result.latency_ms,
        }

    def allows(self, call: ToolCall) -> bool:
        return self.decide(call)["allowed"]

    def set_context(self, context: dict) -> None:
        self.gate.set_context(context)


class ToolGatePolicy:
    name = "toolgate"

    def __init__(self, checker: ToolGateChecker | None = None):
        self.checker = checker or ToolGateChecker()

    def decide(self, call: ToolCall) -> dict:
        started = time.perf_counter()
        observation = self.checker.check(call)
        latency_ms = (time.perf_counter() - started) * 1000.0
        allowed = "violation" not in observation
        event = {
            "name": call.name,
            "allowed": allowed,
            "decision": "allow" if allowed else "block",
            "no_contract": observation.startswith("no_contract:"),
            "latency_ms": latency_ms,
        }
        if not allowed:
            event["reason"] = observation
        return event

    def allows(self, call: ToolCall) -> bool:
        return self.decide(call)["allowed"]


def decide_call(policy, call: ToolCall) -> dict:
    """Uniform decision record; supports custom policies that only implement ``allows``."""
    decider = getattr(policy, "decide", None)
    if callable(decider):
        return decider(call)
    return {"name": call.name, "allowed": bool(policy.allows(call))}


def _noop_executor(name: str, params: dict) -> str:
    return f"ok:{name}"


def build_policy_factory(
    gate: str,
    parser: IntentParser | None = None,
    backend: EmbeddingBackend | None = None,
    trace: TraceLogger | None = None,
    tau: float = 0.6,
    delta: float = 0.1,
    alpha: float = 0.7,
    benchmark_mode: bool = True,
    state_factory=None,
    ablation: str = "none",
) -> Callable[[str], OursPolicy | ToolGatePolicy] | None:
    """Returns ``factory(trusted_request) -> policy``; None for the unprotected condition.

    ``ablation`` (ours only): ``none`` | ``semantic-only`` (A1: no rule veto) |
    ``rule-only`` (A2: no embeddings) | ``raw-request`` (A3: raw request embedding).
    """
    if ablation not in ("none", "semantic-only", "rule-only", "raw-request"):
        raise ValueError(f"unknown ablation {ablation!r}")
    if gate == "none":
        return None
    if gate == "toolgate":

        def toolgate_factory(user_request: str) -> ToolGatePolicy:
            state = state_factory(user_request) if state_factory else None
            return ToolGatePolicy(ToolGateChecker(world_state=state))

        return toolgate_factory
    if gate != "ours":
        raise ValueError(f"unknown gate {gate!r}")

    intent_parser = parser or IntentParser()
    shared_backend = backend or EmbeddingBackend()

    def factory(user_request: str) -> OursPolicy:
        contract = intent_parser.parse(user_request)
        middleware = GateMiddleware(
            contract,
            _noop_executor,
            trace=trace,
            alpha=alpha,
            tau=tau,
            delta=delta,
            benchmark_mode=benchmark_mode,
            backend=shared_backend,
            ablation=ablation,
        )
        middleware.set_context(
            {
                "contract": contract.to_dict(),
                "parser_backend": intent_parser.last_backend,
                "ablation": ablation,
            }
        )
        return OursPolicy(middleware)

    return factory
