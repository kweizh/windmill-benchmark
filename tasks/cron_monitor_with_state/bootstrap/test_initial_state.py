"""
Bootstrap test: verify the initial (broken) state of the environment
before the agent attempts the task.
"""

import os
import shutil
import subprocess
import sys


SCRIPT_PATH = "/home/user/windmill-project/f/scripts/health_monitor.py"


def test_wmill_in_path():
    """wmill package must be importable."""
    result = subprocess.run(
        [sys.executable, "-c", "import wmill"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"wmill is not importable. stderr: {result.stderr}"
    )


def test_project_directory_exists():
    """/home/user/windmill-project directory must exist."""
    assert os.path.isdir("/home/user/windmill-project"), (
        "/home/user/windmill-project directory does not exist"
    )


def test_script_file_exists():
    """health_monitor.py must exist at the expected path."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Script file not found at {SCRIPT_PATH}"
    )


def test_script_does_not_import_get_state():
    """Initial script must NOT import get_state (that is the bug to fix)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()
    assert "get_state" not in content, (
        "Script already imports get_state — initial state is incorrect. "
        "The broken version should only have set_state."
    )


def test_script_imports_set_state():
    """Initial script must import set_state from wmill."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()
    assert "set_state" in content, (
        "Script does not contain set_state import — unexpected initial state."
    )


def test_script_has_unconditional_alert():
    """
    Initial script must call send_alert unconditionally — i.e., there must be
    no 'if current_status != last_status' guard present yet.
    """
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    assert "send_alert(" in content, (
        "Script does not contain a send_alert() call — unexpected initial state."
    )
    assert "if current_status != last_status" not in content, (
        "Script already contains the fix (if current_status != last_status). "
        "The initial broken version should NOT have this guard."
    )


def test_wmill_cli_available():
    """windmill CLI (wmill) must be available as a system command."""
    result = shutil.which("wmill")
    assert result is not None, (
        "wmill CLI not found in PATH. Expected it to be installed via npm."
    )
