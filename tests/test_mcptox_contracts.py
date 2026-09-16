"""MCPTox B2 contracts: path-scoped file tools + effect-recording families (blueprint Sec 5)."""
from __future__ import annotations

from pathlib import Path

import pytest

from intent_gate.baselines.toolgate.checker import ToolGateChecker
from intent_gate.baselines.toolgate.mcptox_contracts import mcptox_contract_names
from intent_gate.baselines.toolgate.world_state import WorldState, seed_from_request
from intent_gate.types import ToolCall


def test_seed_from_request_extracts_paths_and_dirs():
    state = seed_from_request("Write 'Hello, world!' to '/tmp/hello.txt'.")
    assert "/tmp/hello.txt" in state.files
    assert "/tmp" in state.directories


def test_seed_home_folder_maps_to_tilde():
    state = seed_from_request("Create a new directory called 'backups' in my home folder")
    assert "~" in state.directories


def test_path_scope_blocks_write_outside_seeded_dirs():
    checker = ToolGateChecker(world_state=seed_from_request("Write 'Hello, world!' to '/tmp/hello.txt'."))
    obs = checker.check(ToolCall(name="write_file", parameters={"path": "~/.ssh/id_rsa", "content": "x"}))
    assert "violation (pre)" in obs


def test_path_scope_allows_write_inside_seeded_dir():
    checker = ToolGateChecker(world_state=seed_from_request("Write 'Hello, world!' to '/tmp/hello.txt'."))
    obs = checker.check(ToolCall(name="write_file", parameters={"path": "/tmp/hello.txt", "content": "x"}))
    assert obs.startswith("ok:")


def test_path_scope_blocks_read_outside_seeded_dirs():
    checker = ToolGateChecker(world_state=seed_from_request("Read /tmp/hello.txt"))
    obs = checker.check(ToolCall(name="read_file", parameters={"path": "/etc/passwd"}))
    assert "violation (pre)" in obs


def test_unseeded_state_falls_back_to_shape_checks():
    checker = ToolGateChecker()
    obs = checker.check(ToolCall(name="read_file", parameters={"path": "~/.ssh/id_rsa"}))
    assert obs.startswith("ok:")


def test_mail_contract_records_effect():
    checker = ToolGateChecker(world_state=WorldState())
    obs = checker.check(ToolCall(name="sendMail", parameters={"to": "a@b.c", "subject": "s", "body": "b"}))
    assert obs.startswith("ok:")
    assert checker.state.tool_states["mail_actions"]


def test_fake_tool_is_no_contract():
    checker = ToolGateChecker(evaluated_tools={"count_messages", "read_file"})
    obs = checker.check(ToolCall(name="count_messages", parameters={}))
    assert obs.startswith("no_contract:")
    assert checker.no_contract_tools == {"count_messages"}


def test_mcptox_contract_set_has_expected_families():
    names = set(mcptox_contract_names())
    for expected in ("read_file", "write_file", "sendMail", "execute_command", "run_select_query"):
        assert expected in names
    assert len(names) >= 50


def test_mcptox_universe_coverage_is_reported():
    data = Path("data/raw/mcptox/response_all.json")
    if not data.exists():
        pytest.skip("MCPTox snapshot not present")
    from harness.adapters.mcptox import load_mcptox_cases

    cases = load_mcptox_cases(data, limit=200, seed=42)
    universe = {tool for case in cases for tool in case.clean_tools}
    checker = ToolGateChecker(evaluated_tools=universe)
    assert checker.coverage is not None
    assert 0.0 < checker.coverage < 1.0
