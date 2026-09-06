"""Per-call JSONL trace logging (blueprint Sec 6 - load-bearing for threshold sweep)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from intent_gate.types import GateResult, ToolCall


class TraceLogger:
    def __init__(self, path: str | Path = "results/gate_trace.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8")

    def log(self, call: ToolCall, result: GateResult, extra: dict | None = None):
        record = {
            "ts": time.time(),
            "tool_call": {"name": call.name, "parameters": call.parameters, "source": call.source},
            "gate": {
                "S": result.score,
                "S_sem": result.score_sem,
                "S_rule": result.score_rule,
                "decision": result.decision,
                "would_escalate": result.would_escalate,
                "rule_triggered": result.rule_triggered,
                "reason": result.reason,
                "latency_ms": result.latency_ms,
            },
        }
        if extra:
            record.update(extra)
        self._fh.write(json.dumps(record, default=str) + "\n")
        self._fh.flush()

    def close(self):
        if not self._fh.closed:
            self._fh.close()
