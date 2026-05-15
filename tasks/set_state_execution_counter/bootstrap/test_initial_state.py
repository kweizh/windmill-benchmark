import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/windmill-project"
SCRIPT_PATH = "/home/user/windmill-project/f/monitoring/heartbeat.py"


def test_python3_in_path():
    assert shutil.which("python3") is not None, \
        "python3 binary not found in PATH."


def test_wmill_package_importable():
    result = subprocess.run(
        ["python3", "-c", "import wmill"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, \
        f"wmill Python package is not importable: {result.stderr}"


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), \
        f"Project directory {PROJECT_DIR} does not exist."


def test_script_dir_exists():
    script_dir = os.path.dirname(SCRIPT_PATH)
    assert os.path.isdir(script_dir), \
        f"Script directory {script_dir} does not exist."


def test_heartbeat_script_exists():
    assert os.path.isfile(SCRIPT_PATH), \
        f"Heartbeat script not found at {SCRIPT_PATH}."


def test_heartbeat_contains_broken_reset():
    with open(SCRIPT_PATH) as f:
        content = f.read()
    assert "count = 0" in content, \
        "Expected broken 'count = 0' reset pattern in heartbeat.py — the initial state must have the bug present."


def test_heartbeat_does_not_import_get_state():
    with open(SCRIPT_PATH) as f:
        content = f.read()
    assert "get_state" not in content, \
        "heartbeat.py already imports get_state — the initial state should NOT have the fix applied yet."


def test_heartbeat_does_not_import_set_state():
    with open(SCRIPT_PATH) as f:
        content = f.read()
    assert "set_state" not in content, \
        "heartbeat.py already imports set_state — the initial state should NOT have the fix applied yet."
