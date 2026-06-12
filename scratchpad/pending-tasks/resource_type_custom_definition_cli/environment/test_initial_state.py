import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI binary not found in PATH; the Windmill CLI must be pre-installed."
    )


def test_node_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH; Node.js (>= 20) is required by the wmill CLI."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_wmill_token_env_present():
    token = os.environ.get("WMILL_TOKEN")
    assert token is not None and token != "", (
        "WMILL_TOKEN environment variable must be set with a valid Windmill cloud API token."
    )


def test_wmill_workspace_env_present():
    workspace = os.environ.get("WMILL_WORKSPACE")
    assert workspace is not None and workspace != "", (
        "WMILL_WORKSPACE environment variable must be set with the target cloud workspace id."
    )


def test_wmill_base_url_env_present():
    base_url = os.environ.get("WMILL_BASE_URL")
    assert base_url is not None and base_url != "", (
        "WMILL_BASE_URL environment variable must be set (expected https://app.windmill.dev for the cloud instance)."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id is not None and run_id != "", (
        "ZEALT_RUN_ID environment variable must be set so the task can scope its resources."
    )
