import json
import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_NAME = "evaluation-ws"
WORKSPACE_URL = "https://app.windmill.dev"


@pytest.fixture(scope="session", autouse=True)
def configure_windmill_workspace():
    """Register the cloud workspace with the wmill CLI before any test runs.

    The Dockerfile cannot bake in the runtime token, so the workspace
    registration is performed here using `WMILL_TOKEN`. This makes the
    `evaluation-ws` workspace available to the executor and to verification.
    """
    token = os.environ.get("WMILL_TOKEN")
    if not token:
        # The dedicated assertion below will fail with a clear message.
        return
    if shutil.which("wmill") is None:
        return

    # Try to add (idempotent: if already present, the CLI will return non-zero
    # which we tolerate, then verify presence below).
    subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            WORKSPACE_NAME,
            WORKSPACE_NAME,
            WORKSPACE_URL,
            "--token",
            token,
        ],
        capture_output=True,
        text=True,
    )

    # Ensure the workspace is the active one.
    subprocess.run(
        ["wmill", "workspace", "switch", WORKSPACE_NAME],
        capture_output=True,
        text=True,
    )


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "Windmill CLI (`wmill`) not found in PATH. The environment must come with windmill-cli preinstalled."
    )


def test_go_toolchain_available():
    assert shutil.which("go") is not None, (
        "Go toolchain (`go`) not found in PATH. The environment must come with Go preinstalled for Windmill Go scripts."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. It should be pre-created for the executor."
    )


def test_zealt_run_id_env_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "Environment variable ZEALT_RUN_ID must be set so the task can isolate cloud assets per trial."
    )


def test_wmill_token_env_set():
    token = os.environ.get("WMILL_TOKEN")
    assert token, (
        "Environment variable WMILL_TOKEN must be set so the wmill CLI can authenticate against the cloud workspace."
    )


def test_wmill_workspace_configured():
    result = subprocess.run(
        ["wmill", "workspace", "list", "--json"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"`wmill workspace list --json` failed (exit {result.returncode}). stderr: {result.stderr}"
    )
    try:
        workspaces = json.loads(result.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic path
        raise AssertionError(
            f"`wmill workspace list --json` did not return valid JSON: {exc}. stdout: {result.stdout!r}"
        )
    names = []
    if isinstance(workspaces, list):
        for item in workspaces:
            if isinstance(item, dict):
                for key in ("workspaceId", "id", "name"):
                    value = item.get(key)
                    if isinstance(value, str):
                        names.append(value)
    assert any(WORKSPACE_NAME == n or n.endswith(WORKSPACE_NAME) for n in names), (
        f"Expected a workspace named {WORKSPACE_NAME!r} to be configured. Found: {names}"
    )
