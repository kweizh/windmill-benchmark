import os
import shutil

import pytest
import requests


PROJECT_DIR = "/home/user/myproject"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, "wmill CLI binary not found in PATH."


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH (required for windmill-client typing)."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_wmill_token_env_present():
    token = os.environ.get("WMILL_TOKEN")
    assert token, "WMILL_TOKEN environment variable is not set."


def test_wmill_workspace_env_present():
    workspace = os.environ.get("WMILL_WORKSPACE")
    assert workspace, "WMILL_WORKSPACE environment variable is not set."


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."


def test_windmill_cloud_reachable():
    base_url = os.environ.get("WMILL_BASE_URL", "https://app.windmill.dev")
    try:
        resp = requests.get(f"{base_url}/api/version", timeout=15)
    except requests.RequestException as e:
        pytest.fail(f"Could not reach Windmill cloud at {base_url}: {e}")
    assert resp.status_code == 200, (
        f"Windmill cloud /api/version returned {resp.status_code}, expected 200."
    )


def test_windmill_token_authorized():
    base_url = os.environ.get("WMILL_BASE_URL", "https://app.windmill.dev")
    token = os.environ.get("WMILL_TOKEN", "")
    workspace = os.environ.get("WMILL_WORKSPACE", "")
    try:
        resp = requests.get(
            f"{base_url}/api/w/{workspace}/workspaces/get_settings",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
    except requests.RequestException as e:
        pytest.fail(f"Could not authenticate against Windmill cloud workspace {workspace}: {e}")
    assert resp.status_code in (200, 403, 404), (
        f"Unexpected Windmill auth probe status {resp.status_code}. "
        "Expected 200 (authorized) or a recognizable workspace-scoped response."
    )
    assert resp.status_code != 401, "WMILL_TOKEN is unauthorized (HTTP 401)."
