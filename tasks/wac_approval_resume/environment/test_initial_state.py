"""Initial state checks (and one-time provisioning) for the windmill WAC
approval/resume task.

In addition to the usual environment assertions, this module registers the
target cloud Windmill workspace with the local ``wmill`` CLI so that the agent
can deploy scripts without having to run the interactive setup flow itself.
It runs once, before the agent starts working.
"""

import os
import shutil
import subprocess

import requests


PROJECT_DIR = "/home/user/wac-pipeline"
WINDMILL_BASE_URL = "https://app.windmill.dev"
LOCAL_WORKSPACE_NAME = "evaluation-ws"


def _run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "").strip()
    assert rid, "ZEALT_RUN_ID environment variable is not set."
    return rid


def _token() -> str:
    t = os.environ.get("WINDMILL_TOKEN", "").strip()
    assert t, "WINDMILL_TOKEN environment variable is not set."
    return t


def _workspace() -> str:
    w = os.environ.get("WINDMILL_WORKSPACE", "").strip()
    assert w, "WINDMILL_WORKSPACE environment variable is not set."
    return w


def test_wmill_cli_available() -> None:
    assert shutil.which("wmill") is not None, (
        "The `wmill` (windmill-cli) binary is not on PATH. "
        "The task expects the Windmill CLI to be preinstalled."
    )


def test_required_env_vars_present() -> None:
    assert os.environ.get("ZEALT_RUN_ID"), "ZEALT_RUN_ID env var is missing."
    assert os.environ.get("WINDMILL_TOKEN"), "WINDMILL_TOKEN env var is missing."
    assert os.environ.get("WINDMILL_WORKSPACE"), "WINDMILL_WORKSPACE env var is missing."


def test_project_dir_exists() -> None:
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_register_wmill_workspace_for_agent() -> None:
    """Pre-register the cloud workspace with the local wmill CLI.

    This is required so that the agent can run ``wmill sync push`` / ``wmill
    script push`` without going through the interactive token / URL prompts.
    Re-running ``wmill workspace add`` for an already registered workspace is
    safe; we treat a successful run OR an "already exists" error as success.
    """
    token = _token()
    workspace = _workspace()
    result = subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            LOCAL_WORKSPACE_NAME,
            workspace,
            WINDMILL_BASE_URL,
            "--token",
            token,
        ],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=120,
    )
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    if result.returncode != 0 and "already" not in combined.lower():
        raise AssertionError(
            "Failed to register the cloud workspace with the wmill CLI: "
            f"returncode={result.returncode} output={combined!r}"
        )

    whoami = subprocess.run(
        ["wmill", "workspace", "whoami"],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=60,
    )
    assert whoami.returncode == 0, (
        f"`wmill workspace whoami` failed after add: "
        f"stdout={whoami.stdout!r} stderr={whoami.stderr!r}"
    )


def test_windmill_token_and_workspace_reachable() -> None:
    """The cloud workspace must respond to an authenticated whoami-style call."""
    token = _token()
    workspace = _workspace()
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/users/whoami"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    assert resp.status_code == 200, (
        f"Could not authenticate against {url}: status={resp.status_code}, body={resp.text!r}"
    )


def test_workflow_script_not_yet_deployed() -> None:
    """For this run-id, the WAC script must not already exist in the workspace."""
    token = _token()
    workspace = _workspace()
    run_id = _run_id()
    path = f"f/eval/deploy_pipeline_{run_id}"
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/scripts/get/p/{path}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    assert resp.status_code in (404, 400), (
        f"Expected script {path} to not yet exist (HTTP 404), "
        f"but got status={resp.status_code} body={resp.text[:200]!r}"
    )


def test_workflow_script_file_not_yet_on_disk() -> None:
    run_id = _run_id()
    candidate = os.path.join(
        PROJECT_DIR, "f", "eval", f"deploy_pipeline_{run_id}.ts"
    )
    assert not os.path.exists(candidate), (
        f"Expected agent's script file {candidate} to not yet exist before evaluation."
    )
