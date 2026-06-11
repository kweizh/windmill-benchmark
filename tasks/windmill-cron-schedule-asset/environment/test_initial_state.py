import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, "wmill CLI not found in PATH."


def test_wmill_cli_runs():
    result = subprocess.run(
        ["wmill", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"`wmill --version` failed with exit code {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_windmill_token_env_set():
    token = os.environ.get("WINDMILL_TOKEN", "")
    assert token, "WINDMILL_TOKEN environment variable is not set."


def test_windmill_workspace_env_set():
    workspace = os.environ.get("WINDMILL_WORKSPACE", "")
    assert workspace, "WINDMILL_WORKSPACE environment variable is not set."


def test_zealt_run_id_env_set():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
