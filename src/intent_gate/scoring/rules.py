"""Deterministic rule engine (blueprint Sec 5 Comp 2): never relies on embeddings.

Categories map tool names -> risk category. Critical veto: S_rule==0 on a critical
constraint forces S=0 regardless of semantic score.
"""
from __future__ import annotations

import re

from intent_gate.types import IntentContract, ToolCall

FINANCIAL_TOOLS = {"transfer_money", "pay", "purchase", "buy", "send_money", "transferfunds", "pay_bill"}
SEND_TOOLS = {"send_email", "send_message", "email", "post_external"}
FILE_TOOLS = {"write_file", "delete_file", "rm", "shred"}
CODE_TOOLS = {"exec", "exec_code", "run_code", "run_shell", "python_exec"}

FINANCIAL_KEYWORDS = (
    "transfer",
    "withdraw",
    "purchase",
    "buy",
    "pay_bill",
    "paybill",
    "paynow",
    "makepayment",
    "sendpayment",
    "send_money",
    "sendmoney",
    "deposit",
)
SEND_KEYWORDS = ("send", "send_message", "sendmessage", "sendmail", "post_external", "forward", "reply")
SHARE_KEYWORD = "share"
SHARE_SENSITIVE = ("password", "credential", "cred", "secret", "file", "data", "result", "profile", "address", "payment", "contact")

COMMAND_INJECTION_RE = re.compile(r"(&&|\|\||;|`|\$\()")
COMMAND_TOOL_KEYWORDS = ("exec", "shell", "commit", "run_", "script")
COMMAND_PARAM_KEYS = {"command", "cmd", "script", "code", "shell", "patch"}


def _is_send_tool(n: str) -> bool:
    if any(k in n for k in SEND_KEYWORDS):
        return True
    return SHARE_KEYWORD in n and any(s in n for s in SHARE_SENSITIVE)


FILE_KEYWORDS = (
    "write_file",
    "delete_file",
    "file_delete",
    "remove_file",
    "overwrite",
    "shred",
    "deletion",
    "relocat",
    "unlink",
    "truncate",
    "rename",
    "move_item",
    "moveitem",
    "upload",
)
CODE_KEYWORDS = ("exec", "shell", "run_code", "python_exec")


def tool_category(name: str) -> str:
    """Map tool names (snake_case or benchmark CamelCase) to a risk category."""
    n = (name or "").lower()
    if n in FINANCIAL_TOOLS or any(k in n for k in FINANCIAL_KEYWORDS):
        return "financial"
    if n in SEND_TOOLS or _is_send_tool(n):
        return "send"
    if n in FILE_TOOLS or any(k in n for k in FILE_KEYWORDS):
        return "file"
    if n in CODE_TOOLS or any(k in n for k in CODE_KEYWORDS):
        return "code"
    return "other"


def _command_injection(call: ToolCall) -> bool:
    """True when a command-like tool/parameter carries shell operators (injection payload)."""
    name = (call.name or "").lower()
    keys = {str(k).lower() for k in (call.parameters or {})}
    command_like = any(k in name for k in COMMAND_TOOL_KEYWORDS) or bool(keys & COMMAND_PARAM_KEYS)
    if not command_like:
        return False
    for value in (call.parameters or {}).values():
        if isinstance(value, str) and COMMAND_INJECTION_RE.search(value):
            return True
    return False


PATH_SCOPE_HINTS = ("path", "folder", "directory")


def _authorized_paths(limit_val: str) -> list[str]:
    return [
        token.strip("'\"")
        for token in re.split(r"[\s,;]+", limit_val or "")
        if "/" in token or token.startswith("~")
    ]


def _path_matches(candidate: str, allowed: str) -> bool:
    c = candidate.rstrip("/")
    a = allowed.rstrip("/")
    return c == a or c.startswith(a + "/") or a.startswith(c + "/")


def _path_scope_ok(limit_val: str, params: dict) -> bool:
    """When the contract names authorized paths, path-like arguments must fall inside them."""
    allowed = _authorized_paths(limit_val)
    if not allowed:
        return True
    for key, value in params.items():
        if not isinstance(value, str) or not any(hint in key for hint in PATH_SCOPE_HINTS):
            continue
        for candidate in (p.strip() for p in re.split(r"[\s,;]+", value) if p.strip()):
            if not any(_path_matches(candidate, allowed_path) for allowed_path in allowed):
                return False
    return True


CLOSED_PREFIXES = ("disallow", "no ", "deny", "forbidden", "self-only")


def _limit_allows(limit_val: str) -> bool:
    """A limit is closed when it starts with an explicit denial prefix; otherwise open."""
    v = (limit_val or "").strip().lower()
    return not v.startswith(CLOSED_PREFIXES)


def evaluate_rules(contract: IntentContract, call: ToolCall) -> tuple[float, bool, str]:
    """Return (score_rule in {0,1}, triggered, reason). 1 = passes all hard constraints."""
    cat = tool_category(call.name)
    limits = contract.side_effect_limits or {}
    name = call.name.lower()
    params = {str(k).lower(): v for k, v in (call.parameters or {}).items()}

    # Financial veto: any money-moving tool when financial limit is closed
    if cat == "financial" or "transfer" in name or name.startswith("pay"):
        if not _limit_allows(limits.get("financial", "no payment")):
            return 0.0, True, f"financial tool {call.name} not in intent (limit={limits.get('financial')})"

    # Code exec veto: single exec can do arbitrary side effects (Sec 10 scope boundary)
    if cat == "code":
        if not _limit_allows(limits.get("code_exec", "disallow")):
            return 0.0, True, f"code_exec {call.name} disallowed by intent"

    # File write veto
    if cat == "file":
        file_limit = limits.get("file_write", "disallow")
        if not _limit_allows(file_limit):
            return 0.0, True, f"file tool {call.name} disallowed by intent"
        if not _path_scope_ok(file_limit, params):
            return 0.0, True, f"file path outside the authorized scope for {call.name}"

    # External send: block send to non-self recipient when limit is self-only/disallow
    if cat == "send":
        ext_limit = (limits.get("external_send", "disallow") or "").lower()
        to = str(params.get("to", params.get("recipient", params.get("to_email", "")))).lower()
        if "disallow" in ext_limit:
            return 0.0, True, f"external send {call.name} disallowed by intent"
        if "self-only" in ext_limit and to and to not in ("me", "self", "user"):
            # Heuristic: attacker address contains attacker/external domain
            if "attacker" in to or "@" in to:
                return 0.0, True, f"external send to {to!r} outside self-only intent"

    # Shell operators inside command-like parameters: treat as code execution payload
    if _command_injection(call) and not _limit_allows(limits.get("code_exec", "disallow")):
        return 0.0, True, f"shell operators in {call.name} parameters treated as code_exec"

    return 1.0, False, ""
