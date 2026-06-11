import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "The Windmill CLI (`wmill`) is not available on PATH; it must be installed in the environment."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist; the workspace folder must be provisioned before evaluation."
    )


def test_windmill_token_env_present():
    assert os.environ.get("WINDMILL_TOKEN"), (
        "Environment variable WINDMILL_TOKEN is not set; a Windmill cloud bearer token is required."
    )


def test_windmill_workspace_env_present():
    assert os.environ.get("WINDMILL_WORKSPACE"), (
        "Environment variable WINDMILL_WORKSPACE is not set; the target cloud workspace ID must be provided."
    )


def test_wmill_workspace_setup_and_authenticated():
    """Authenticate the CLI against https://app.windmill.dev using the provided env vars.

    This is run as part of initial state so the executor can immediately use
    `wmill` against the cloud workspace.
    """
    workspace = os.environ.get("WINDMILL_WORKSPACE", "")
    token = os.environ.get("WINDMILL_TOKEN", "")
    assert workspace and token, "WINDMILL_WORKSPACE and WINDMILL_TOKEN must be set for setup."

    # `wmill workspace add` is idempotent enough: re-adding overwrites the local config entry.
    add_result = subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            workspace,
            workspace,
            "https://app.windmill.dev/",
            "--token",
            token,
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=PROJECT_DIR,
    )
    assert add_result.returncode == 0, (
        f"`wmill workspace add` failed with exit code {add_result.returncode}.\n"
        f"stdout: {add_result.stdout}\nstderr: {add_result.stderr}"
    )

    list_result = subprocess.run(
        ["wmill", "workspace", "list"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=PROJECT_DIR,
    )
    assert list_result.returncode == 0, (
        f"`wmill workspace list` failed with exit code {list_result.returncode}.\n"
        f"stdout: {list_result.stdout}\nstderr: {list_result.stderr}"
    )
    assert workspace in list_result.stdout, (
        f"Configured workspace `{workspace}` not found in `wmill workspace list` output:\n{list_result.stdout}"
    )


def test_no_existing_rust_script_files():
    """Make sure the executor is the one who creates the rust_doubler files (no leftover state)."""
    rs_path = os.path.join(PROJECT_DIR, "f", "eval", "rust_doubler.rs")
    yaml_path = os.path.join(PROJECT_DIR, "f", "eval", "rust_doubler.script.yaml")
    assert not os.path.exists(rs_path), (
        f"Unexpected pre-existing Rust source file at {rs_path}; executor must create it."
    )
    assert not os.path.exists(yaml_path), (
        f"Unexpected pre-existing script.yaml at {yaml_path}; executor must create it."
    )
