"""
Initial state verification for the event_driven_etl_orchestrator task.

Asserts:
- wmill CLI is available in PATH
- /home/user/windmill-project directory exists
- /home/user/windmill-project/processed_events.json exists and contains an empty JSON array
- /home/user/windmill-project/f/workflows/etl_orchestrator.ts does NOT exist (agent must create it)
"""

import json
import os
import shutil
import subprocess
import sys


def test_wmill_in_path():
    """wmill CLI must be available in PATH."""
    wmill_path = shutil.which("wmill")
    assert wmill_path is not None, (
        "wmill CLI not found in PATH. "
        "Expected it to be installed via npm (windmill-cli package)."
    )


def test_windmill_project_exists():
    """The windmill project directory must exist."""
    project_dir = "/home/user/windmill-project"
    assert os.path.isdir(project_dir), (
        f"Expected project directory '{project_dir}' to exist, but it does not."
    )


def test_processed_events_json_exists_and_empty():
    """processed_events.json must exist and contain an empty JSON array."""
    state_file = "/home/user/windmill-project/processed_events.json"
    assert os.path.isfile(state_file), (
        f"Expected state file '{state_file}' to exist, but it does not."
    )
    with open(state_file, "r") as f:
        content = f.read().strip()
    assert content, f"State file '{state_file}' is empty (no content at all)."
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"State file '{state_file}' does not contain valid JSON: {e}"
        )
    assert isinstance(data, list), (
        f"Expected '{state_file}' to contain a JSON array, got: {type(data).__name__}"
    )
    assert len(data) == 0, (
        f"Expected '{state_file}' to contain an empty array [], "
        f"but it contains {len(data)} item(s): {data}"
    )


def test_etl_orchestrator_does_not_exist():
    """etl_orchestrator.ts must NOT exist before the agent runs."""
    workflow_file = "/home/user/windmill-project/f/workflows/etl_orchestrator.ts"
    assert not os.path.exists(workflow_file), (
        f"Expected '{workflow_file}' to NOT exist in the initial state, "
        "but it was found. The agent should create this file."
    )


if __name__ == "__main__":
    tests = [
        test_wmill_in_path,
        test_windmill_project_exists,
        test_processed_events_json_exists_and_empty,
        test_etl_orchestrator_does_not_exist,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {test.__name__}: {e}")
            failed += 1

    if failed:
        print(f"\n{failed}/{len(tests)} initial-state check(s) failed.")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} initial-state checks passed.")
        sys.exit(0)
