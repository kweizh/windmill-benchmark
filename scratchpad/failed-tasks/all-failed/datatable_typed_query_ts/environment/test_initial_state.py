import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, "wmill CLI binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_zealt_run_id_env_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."


def test_wmill_token_env_set():
    token = os.environ.get("WMILL_TOKEN")
    assert token, "WMILL_TOKEN environment variable is not set."


def test_wmill_workspace_configured():
    result = subprocess.run(
        ["wmill", "workspace", "list"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"`wmill workspace list` failed with exit code {result.returncode}. "
        f"stdout: {result.stdout!r}, stderr: {result.stderr!r}"
    )
    assert "evaluation-ws" in result.stdout, (
        "Expected workspace 'evaluation-ws' to be configured in the wmill CLI. "
        f"Got: {result.stdout!r}"
    )


def test_node_available():
    # The wmill CLI requires Node >= 20 to be present in the environment.
    assert shutil.which("node") is not None, "node binary not found in PATH."
