import os
import shutil

import pytest

PROJECT_DIR = "/home/user/windmill-webhook"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "Windmill CLI binary 'wmill' was not found in PATH."
    )


def test_curl_available():
    assert shutil.which("curl") is not None, (
        "'curl' binary was not found in PATH; it is required to call the sync webhook."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_zealt_run_id_env_var_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."


def test_windmill_token_env_var_present():
    token = os.environ.get("WINDMILL_TOKEN")
    assert token, "WINDMILL_TOKEN environment variable is not set."


def test_windmill_workspace_env_var_present():
    workspace = os.environ.get("WINDMILL_WORKSPACE")
    assert workspace, "WINDMILL_WORKSPACE environment variable is not set."


def test_windmill_username_env_var_present():
    username = os.environ.get("WINDMILL_USERNAME")
    assert username, "WINDMILL_USERNAME environment variable is not set."


def test_response_artifacts_not_yet_created():
    # The executor is expected to create these files; ensure we start clean.
    for name in ("response.headers", "response.body.json"):
        path = os.path.join(PROJECT_DIR, name)
        assert not os.path.exists(path), (
            f"Initial state error: {path} already exists before the task starts."
        )
