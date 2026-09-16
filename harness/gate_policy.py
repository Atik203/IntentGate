"""Gate policies for benchmark conditions: none / ours / toolgate (blueprint Sec 6/9).

A policy answers one question per proposed call: ``allows(call)``. The runner builds the
policy from the *trusted* user request BEFORE any attacker content (tool definitions,
injected observations) is assembled - the ordering invariant from blueprint Sec 10.
"""
from __future__ import annotations

from collections.abc import Callable

from intent_gate.baselines.toolgate.checker import ToolGateChecker
from intent_gate.gate.middleware import GateMiddleware
from intent_gate.gate.trace import TraceLogger
from intent_gate.parser.parser import IntentParser
from intent_gate.scoring.embeddings import EmbeddingBackend
from intent_gate.types import ToolCall


class AllowAllPolicy:
    name = "none"

    def allows(self, call: ToolCall) -> bool:
        return True


class OursPolicy:
    name = "ours"

    def __init__(self, gate: GateMiddleware):
        self.gate = gate

    def allows(self, call: ToolCall) -> bool:
        return self.gate.check(call).decision == "allow"


class ToolGatePolicy:
    name = "toolgate"

    def __init__(self, checker: ToolGateChecker | None = None):
        self.checker = checker or ToolGateChecker()

    def allows(self, call: ToolCall) -> bool:
        return "violation" not in self.checker.check(call)


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
) -> Callable[[str], OursPolicy | ToolGatePolicy] | None:
    """Returns ``factory(trusted_request) -> policy``; None for the unprotected condition."""
    if gate == "none":
        return None
    if gate == "toolgate":
        return lambda user_request: ToolGatePolicy()
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
        )
        return OursPolicy(middleware)

    return factory
