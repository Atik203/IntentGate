"""Per-tool Hoare contracts for ToolGate B2 (blueprint Sec 5 Comp 3 / Appendix G).

Author ONLY for the evaluated tool subset (InjecAgent 17 + MCPTox subset, NOT all 353).
Missing contract -> no_contract counter: treated as allow-with-flag so coverage gap is visible.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

from intent_gate.baselines.toolgate.world_state import WorldState

Contract = Tuple[Callable, Callable]  # (pre(state, params)->bool, post(result)->bool)


def build_contracts() -> Dict[str, Contract]:
    """Minimal Appendix-G-style contracts for the InjecAgent 17-user-tool subset (extend per benchmark).

    Preserves the original pilot contracts (transfer_money, read_file) for backward
    compatibility / MCPTox subset, and adds 17 InjecAgent user-tool contracts.
    """

    # ----- Original pilot contracts (kept for test compatibility / MCPTox subset) -----
    def pre_transfer(state: WorldState, params: dict) -> bool:
        amt = float(params.get("amount", 0))
        return state.balance >= amt and amt <= 1000.0

    def post_transfer(result: Any) -> bool:
        return True

    def pre_read(state: WorldState, params: dict) -> bool:
        return "read" in state.permissions or not state.permissions

    def post_read(result: Any) -> bool:
        return True

    # ----- InjecAgent 17 user tools (from tools.json entries 0-16) -----
    def _pre_always(state: WorldState, params: dict) -> bool:
        return True

    def _post_always(result: Any) -> bool:
        return True

    # Terminal: command execution
    terminal_pre = _pre_always
    terminal_post = _post_always

    # Gmail: send email (to, subject, body required)
    gmail_pre = _pre_always
    gmail_post = _post_always

    # GoogleCalendar: event creation
    calendar_pre = _pre_always
    calendar_post = _post_always

    # BankManager: account operations
    bankmanager_pre = _pre_always
    bankmanager_post = _post_always

    # Amazon: product search
    amazon_pre = _pre_always
    amazon_post = _post_always

    # Expedia: trip planning
    expedia_pre = _pre_always
    expedia_post = _post_always

    # TwitterManager: posting
    twittermanager_pre = _pre_always
    twittermanager_post = _post_always

    # GoogleHome: device control
    googlehome_pre = _pre_always
    googlehome_post = _post_always

    # Dropbox: file operations
    dropbox_pre = _pre_always
    dropbox_post = _post_always

    # Teladoc: health queries
    teladoc_pre = _pre_always
    teladoc_post = _post_always

    # FacebookManager: social operations
    facebookmanager_pre = _pre_always
    facebookmanager_post = _post_always

    # Todoist: task management
    todoist_pre = _pre_always
    todoist_post = _post_always

    # Venmo: payments
    venmo_pre = _pre_always
    venmo_post = _post_always

    # DeepfakeGenerator: video operations
    deepfakegenerator_pre = _pre_always
    deepfakegenerator_post = _post_always

    # The23andMe: genetic data
    the23andme_pre = _pre_always
    the23andme_post = _post_always

    # GoogleSearch: web search
    googlesearch_pre = _pre_always
    googlesearch_post = _post_always

    # WebBrowser: web navigation
    webbrowser_pre = _pre_always
    webbrowser_post = _post_always

    return {
        "transfer_money": (pre_transfer, post_transfer),
        "read_file": (pre_read, post_read),
        "terminal": (terminal_pre, terminal_post),
        "gmail": (gmail_pre, gmail_post),
        "googlecalendar": (calendar_pre, calendar_post),
        "bankmanager": (bankmanager_pre, bankmanager_post),
        "amazon": (amazon_pre, amazon_post),
        "expedia": (expedia_pre, expedia_post),
        "twittermanager": (twittermanager_pre, twittermanager_post),
        "googlehome": (googlehome_pre, googlehome_post),
        "dropbox": (dropbox_pre, dropbox_post),
        "teladoc": (teladoc_pre, teladoc_post),
        "facebookmanager": (facebookmanager_pre, facebookmanager_post),
        "todoist": (todoist_pre, todoist_post),
        "venmo": (venmo_pre, venmo_post),
        "deepfakegenerator": (deepfakegenerator_pre, deepfakegenerator_post),
        "the23andme": (the23andme_pre, the23andme_post),
        "googlesearch": (googlesearch_pre, googlesearch_post),
        "webbrowser": (webbrowser_pre, webbrowser_post),
    }
