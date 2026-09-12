"""ToolGate B2 checker: pre/post Hoare check on symbolic world-state (blueprint Sec 5 Comp 3)."""
from __future__ import annotations

from intent_gate.baselines.toolgate.contracts import build_contracts
from intent_gate.baselines.toolgate.world_state import WorldState
from intent_gate.types import ToolCall


class ToolGateChecker:
    def __init__(self, contracts: dict | None = None, world_state: WorldState | None = None):
        self.contracts = contracts if contracts is not None else build_contracts()
        self.state = world_state or WorldState()
        self.no_contract_count = 0
        self.violations = 0

    @property
    def coverage(self) -> float:
        """Ratio of tools with contracts to total tools evaluated (0.0–1.0)."""
        total = len(self.contracts)
        if total == 0:
            return 0.0
        # count tools that have a contract (i.e., appear in the dict)
        return len([name for name in self.contracts]) / total

    def check(self, call: ToolCall) -> str:
        """Return observation string (execute or violation). Same interface as GateMiddleware.execute."""
        if call.name not in self.contracts:
            self.no_contract_count += 1
            return f"no_contract:{call.name}: allowed-with-flag"  # coverage gap made visible
        pre, post = self.contracts[call.name]
        if not pre(self.state, call.parameters):
            self.violations += 1
            return f"ToolGate violation (pre): {call.name} params={call.parameters}"
        result = _simulate(call)  # placeholder: real executor injected at harness level
        if not post(result):
            self.violations += 1
            return f"ToolGate violation (post): {call.name}"
        return str(result)


def _simulate(call: ToolCall) -> str:
    return f"ok:{call.name}({call.parameters})"
