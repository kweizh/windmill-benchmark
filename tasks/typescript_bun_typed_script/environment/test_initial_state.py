import os
import shutil

PROJECT_DIR = "/home/user/wmill_project"


def test_wmill_cli_available() -> None:
    assert shutil.which("wmill") is not None, (
        "wmill CLI binary not found in PATH; the Windmill CLI must be installed."
    )


def test_node_available() -> None:
    assert shutil.which("node") is not None, (
        "node binary not found in PATH; Node.js 20+ is required for the wmill CLI."
    )


def test_project_dir_exists() -> None:
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_run_id_env_var_set() -> None:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set so the script path can be isolated per trial."
    )


def test_windmill_credentials_env_vars_set() -> None:
    token = os.environ.get("WMILL_TOKEN")
    workspace = os.environ.get("WMILL_WORKSPACE_ID")
    base_url = os.environ.get("WMILL_BASE_URL")
    assert token, "WMILL_TOKEN environment variable must be set for cloud authentication."
    assert workspace, "WMILL_WORKSPACE_ID environment variable must be set for cloud authentication."
    assert base_url, "WMILL_BASE_URL environment variable must be set for the cloud instance URL."
