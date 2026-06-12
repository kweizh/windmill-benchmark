import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/myproject"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI not found in PATH. The Windmill CLI must be installed in the environment."
    )


def test_node_runtime_available():
    # wmill is distributed as a Node CLI; make sure Node is on PATH so wmill can run.
    assert shutil.which("node") is not None, (
        "node runtime not found in PATH; wmill CLI requires Node.js >= 20."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before evaluation starts."
    )


def test_wmill_token_env_set():
    token = os.environ.get("WMILL_TOKEN", "")
    assert token, (
        "WMILL_TOKEN environment variable must be set to a non-empty Windmill cloud API token."
    )


def test_wmill_workspace_env_set():
    workspace = os.environ.get("WMILL_WORKSPACE", "")
    assert workspace, (
        "WMILL_WORKSPACE environment variable must be set to the cloud workspace ID."
    )


def test_wmill_base_url_env_set():
    base_url = os.environ.get("WMILL_BASE_URL", "")
    assert base_url, (
        "WMILL_BASE_URL environment variable must be set (e.g. https://app.windmill.dev)."
    )


def test_zealt_run_id_env_set():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set so resources can be isolated per trial."
    )


def test_wmill_workspace_configured():
    # The wmill CLI should already have a workspace registered (matching WMILL_WORKSPACE).
    # `wmill workspace list` exits 0 and prints the configured workspaces.
    result = subprocess.run(
        ["wmill", "workspace", "list"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"`wmill workspace list` failed with code {result.returncode}: {result.stderr}"
    )
