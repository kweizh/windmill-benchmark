import os
import shutil

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI not found in PATH. The Windmill CLI is required to author and "
        "deploy flows."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. The agent is expected to "
        "work in this directory."
    )


def test_wm_token_env_var_set():
    token = os.environ.get("WM_TOKEN")
    assert token, (
        "WM_TOKEN environment variable is not set. A Windmill cloud API token is "
        "required to deploy and run flows."
    )


def test_wm_workspace_env_var_set():
    workspace = os.environ.get("WM_WORKSPACE")
    assert workspace, (
        "WM_WORKSPACE environment variable is not set. The target Windmill workspace "
        "must be specified."
    )


def test_wm_base_url_env_var_set():
    base_url = os.environ.get("WM_BASE_URL")
    assert base_url, (
        "WM_BASE_URL environment variable is not set. The cloud Windmill base URL "
        "must be specified."
    )


def test_zealt_run_id_env_var_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable is not set. A run-id is required to "
        "isolate resource names across parallel runs."
    )


def test_requests_library_importable():
    pytest.importorskip("requests", reason="requests is required for verification.")


def test_yaml_library_importable():
    pytest.importorskip("yaml", reason="PyYAML is required to parse the flow YAML.")
