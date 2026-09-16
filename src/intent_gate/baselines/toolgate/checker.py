"""ToolGate B2 checker: pre/post Hoare check on symbolic world-state (blueprint Sec 5 Comp 3)."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from intent_gate.baselines.toolgate.contracts import Contract, build_contracts
from intent_gate.baselines.toolgate.world_state import WorldState
from intent_gate.types import ToolCall

Executor = Callable[[ToolCall], Any]


class ToolGateChecker:
    def __init__(
        self,
        contracts: dict[str, Contract] | None = None,
        world_state: WorldState | None = None,
        evaluated_tools: Iterable[str] | None = None,
        executor: Executor | None = None,
    ):
        self.contracts = contracts if contracts is not None else build_contracts()
        self.state = world_state or WorldState()
        self.evaluated_tools = set(evaluated_tools) if evaluated_tools is not None else None
        self.executor = executor
        self.no_contract_count = 0
        self.no_contract_tools: set[str] = set()
        self.violations = 0

    @property
    def coverage(self) -> float | None:
        """Contracted share of the evaluated tool universe; None when no universe was supplied."""
        if self.evaluated_tools is None:
            return None
        if not self.evaluated_tools:
            return 0.0
        contracted = len(set(self.contracts) & self.evaluated_tools)
        return contracted / len(self.evaluated_tools)

    def check(self, call: ToolCall) -> str:
        """Return observation string (execute or violation). Same interface as GateMiddleware.execute."""
        if call.name not in self.contracts:
            self.no_contract_count += 1
            self.no_contract_tools.add(call.name)
            return f"no_contract:{call.name}: allowed-with-flag"
        contract = self.contracts[call.name]
        if not contract.pre(self.state, call.parameters):
            self.violations += 1
            return f"ToolGate violation (pre): {call.name} params={call.parameters}"
        snapshot = self.state.snapshot()
        result = self.executor(call) if self.executor else _simulate(call)
        contract.effect(self.state, call.parameters, result)
        if not contract.post(self.state, call.parameters, result):
            self.violations += 1
            self.state.restore(snapshot)
            return f"ToolGate violation (post): {call.name}"
        return str(result)


def _simulate(call: ToolCall) -> str:
    return f"ok:{call.name}({call.parameters})"
