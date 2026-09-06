"""Per-tool Hoare contracts for ToolGate B2 (blueprint Sec 5 Comp 3 / Appendix G).

Author ONLY for the evaluated tool subset (InjecAgent 17 + MCPTox subset, not all 353).
Missing contract -> no_contract counter: treated as allow-with-flag so coverage gap is visible.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

from intent_gate.baselines.toolgate.world_state import WorldState

Contract = Tuple[Callable, Callable]  # (pre(state, params)->bool, post(result)->bool)


def build_contracts() -> Dict[str, Contract]:
    """Minimal Appendix-G-style contracts for the pilot tool subset (extend per benchmark)."""
    def pre_transfer(state: WorldState, params: dict) -> bool:
        amt = float(params.get("amount", 0))
        return state.balance >= amt and amt <= 1000.0

    def post_transfer(result: Any) -> bool:
        return True

    def pre_read(state: WorldState, params: dict) -> bool:
        return "read" in state.permissions or not state.permissions

    def post_read(result: Any) -> bool:
        return True

    return {
        "transfer_money": (pre_transfer, post_transfer),
        "read_file": (pre_read, post_read),
    }
