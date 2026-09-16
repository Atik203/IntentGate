"""Hoare contracts for the evaluated MCPTox tool subset (blueprint Sec 5 Comp 3 / Appendix G).

Covered families (exact snapshot tool names): filesystem read/write, mail, GitHub,
process/shell, DB/Prisma, plus a few frequently called misc tools. The long tail
(801 distinct clean tools across 45 servers) is intentionally not contracted and is
counted as ``no_contract`` - exposing ToolGate's per-tool setup cost.

File tools enforce path scope against the seeded world state: only paths named in the
trusted request (and their directories) are allowed; when nothing was seeded, contracts
fall back to shape/effect checks.
"""
from __future__ import annotations

from collections.abc import Callable

from intent_gate.baselines.toolgate.contracts import (
    Contract,
    _always_post,
    _no_effect,
    _record_effect,
    _recorded_post,
    _shape,
)
from intent_gate.baselines.toolgate.world_state import WorldState

Pre = Callable[[WorldState, dict], bool]

_PATH_KEY_HINTS = ("path", "file", "dir", "folder", "destination")

_READ_FILE_TOOLS = (
    "read_file",
    "read_multiple_files",
    "list_directory",
    "search_files",
    "get_file_info",
    "search_code",
    "directory_tree",
    "list_allowed_directories",
    "get_file_contents",
)
_WRITE_FILE_TOOLS = (
    "write_file",
    "create_directory",
    "move_file",
    "edit_file",
    "edit_block",
    "create_or_update_file",
    "push_files",
)
_MAIL_TOOLS = (
    "sendMail",
    "sendSimpleMail",
    "sendHtmlMail",
    "sendBulkMail",
    "waitForReply",
    "searchEmails",
    "listEmails",
    "getContacts",
    "getEmailDetail",
    "deleteEmail",
    "moveEmail",
    "getAttachment",
    "listFolders",
    "markAsRead",
    "markAsUnread",
    "markMultipleAsRead",
    "markMultipleAsUnread",
)
_GITHUB_TOOLS = (
    "search_repositories",
    "create_repository",
    "create_issue",
    "fork_repository",
    "create_branch",
)
_PROCESS_TOOLS = (
    "execute_command",
    "read_output",
    "list_sessions",
    "list_processes",
    "kill_process",
    "force_terminate",
)
_DB_TOOLS = (
    "list_tables",
    "run_select_query",
    "list_databases",
    "migrate-status",
    "migrate-dev",
    "migrate-reset",
    "Prisma-Studio",
    "Prisma-Login",
    "Prisma-Postgres-account-status",
    "Create-Prisma-Postgres-Database",
    "get_config",
    "set_config_value",
)
_MISC_READ_TOOLS = (
    "tavily-search",
    "search-maps",
    "get_current_stock_price",
    "news_sentiment",
    "search_papers",
    "get_paper_data",
    "search_nodes",
)
_MISC_ACTION_TOOLS = ("generate_image", "puppeteer_evaluate")


def _path_allowed(state: WorldState, path: str) -> bool:
    if not state.files and not state.directories:
        return True
    if path in state.files:
        return True
    for allowed in state.directories:
        base = allowed.rstrip("/")
        if path == base or path.startswith(base + "/"):
            return True
    return False


def _path_scope_pre() -> Pre:
    def pre(state: WorldState, params: dict) -> bool:
        for key, value in params.items():
            if not any(hint in str(key).lower() for hint in _PATH_KEY_HINTS):
                continue
            items = value if isinstance(value, (list, tuple, set)) else [value]
            for item in items:
                if isinstance(item, str) and item and not _path_allowed(state, item):
                    return False
        return True
    return pre


def _recorded(kind: str) -> Contract:
    return Contract(pre=_shape(), post=_recorded_post(kind), effect=_record_effect(kind))


def build_mcptox_contracts() -> dict[str, Contract]:
    contracts: dict[str, Contract] = {}
    for name in _READ_FILE_TOOLS:
        contracts[name] = Contract(pre=_path_scope_pre(), post=_always_post, effect=_no_effect)
    for name in _WRITE_FILE_TOOLS:
        contracts[name] = Contract(
            pre=_path_scope_pre(),
            post=_recorded_post("file_writes"),
            effect=_record_effect("file_writes"),
        )
    for name in _MAIL_TOOLS:
        contracts[name] = _recorded("mail_actions")
    for name in _GITHUB_TOOLS:
        contracts[name] = _recorded("github_actions")
    for name in _PROCESS_TOOLS:
        contracts[name] = _recorded("process_actions")
    for name in _DB_TOOLS:
        contracts[name] = _recorded("db_actions")
    for name in _MISC_READ_TOOLS:
        contracts[name] = Contract(pre=_shape(), post=_always_post, effect=_no_effect)
    for name in _MISC_ACTION_TOOLS:
        contracts[name] = _recorded("misc_actions")
    return contracts


def mcptox_contract_names() -> list[str]:
    return sorted(build_mcptox_contracts())
