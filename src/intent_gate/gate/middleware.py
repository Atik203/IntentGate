"""Synchronous action gate middleware (blueprint Sec 5 Comp 2).

Enforcement contract: every tool call must pass through GateMiddleware.execute().
No bypass path - integration test asserts direct executor access fails in harness.
"""
from __future__ import annotations

import time

from intent_gate.gate.decisions import decide
from intent_gate.gate.trace import TraceLogger
from intent_gate.scoring.scorer import score_call
from intent_gate.types import Decision, GateResult, IntentContract, ToolCall


class GateMiddleware:
    def __init__(
        self,
        contract: IntentContract,
        executor,
        trace: TraceLogger | None = None,
        alpha: float = 0.7,
        tau: float = 0.6,
        delta: float = 0.1,
        benchmark_mode: bool = True,
        interactive_prompt=None,
    ):
        self.contract = contract
        self.executor = executor  # callable(name, parameters) -> observation
        self.trace = trace or TraceLogger()
        self.alpha = alpha
        self.tau = tau
        self.delta = delta
        self.benchmark_mode = benchmark_mode
        self.interactive_prompt = interactive_prompt

    def check(self, call: ToolCall) -> GateResult:
        t0 = time.perf_counter()
        s, s_sem, s_rule, triggered, reason = score_call(self.contract, call, alpha=self.alpha)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        d = decide(s, tau=self.tau, delta=self.delta)
        result = GateResult(
            decision=d,
            score=s,
            score_sem=s_sem,
            score_rule=s_rule,
            latency_ms=latency_ms,
            rule_triggered=triggered,
            would_escalate=(d == "escalate" and self.benchmark_mode),
            reason=reason,
        )
        self.trace.log(call, result)
        return result

    def execute(self, call: ToolCall):
        """THE only entry point from the agent loop. Returns observation string."""
        result = self.check(call)
        if result.decision == "allow":
            return self.executor(call.name, call.parameters)
        if result.decision == "escalate" and not self.benchmark_mode and self.interactive_prompt:
            answer = self.interactive_prompt(call, result)
            if answer:
                return self.executor(call.name, call.parameters)
            return f"Blocked by intent gate: user declined (S={result.score:.2f})"
        if result.decision == "escalate" and not self.benchmark_mode:
            return f"Escalate (no prompt available): {result.reason} (S={result.score:.2f})"
        return f"Blocked by intent gate: {result.reason} (S={result.score:.2f})"
