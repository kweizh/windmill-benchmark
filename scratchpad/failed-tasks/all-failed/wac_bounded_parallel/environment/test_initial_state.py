import os
import re
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_NAME = "evaluation-ws"
WINDMILL_REMOTE = "https://app.windmill.dev/"


@pytest.fixture(scope="session", autouse=True)
def _register_windmill_workspace():
    """Register the Windmill cloud workspace using the runtime-provided token.

    The Docker image cannot bake in WINDMILL_TOKEN (it is a per-evaluation
    secret), so we configure `wmill` here, before any other initial-state
    assertion runs. This also leaves the workspace registered for the agent
    to use during task execution.
    """
    token = os.environ.get("WINDMILL_TOKEN", "")
    workspace = os.environ.get("WINDMILL_WORKSPACE", "")
    if not token or not workspace:
        # Let the dedicated env-var assertions below produce the helpful
        # failure message instead of crashing here.
        yield
        return

    # Best-effort: drop any prior registration for the same name so we never
    # leave a stale workspace pointer in the container's wmill config.
    subprocess.run(
        ["wmill", "workspace", "remove", WORKSPACE_NAME],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )

    result = subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            WORKSPACE_NAME,
            workspace,
            WINDMILL_REMOTE,
            "--token",
            token,
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"`wmill workspace add` failed (rc={result.returncode}). "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    yield


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill CLI binary not found in PATH."


def test_node_binary_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH (required by wmill CLI)."
    )


def test_python3_binary_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_cloudflared_binary_available():
    assert shutil.which("cloudflared") is not None, (
        "cloudflared binary not found in PATH; required by the verifier to "
        "expose the local concurrency-tracking HTTP server to Windmill cloud workers."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_wmill_yaml_exists():
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert os.path.isfile(wmill_yaml), (
        f"Expected pre-initialised Windmill workspace config at {wmill_yaml}."
    )


def test_eval_folder_exists():
    eval_dir = os.path.join(PROJECT_DIR, "f", "eval")
    assert os.path.isdir(eval_dir), (
        f"Expected pre-created folder {eval_dir} for the agent to drop fanout_workflow.ts into."
    )


def test_windmill_token_env_present():
    assert os.environ.get("WINDMILL_TOKEN"), (
        "WINDMILL_TOKEN environment variable is not set; required to authenticate against "
        "https://app.windmill.dev."
    )


def test_windmill_workspace_env_present():
    assert os.environ.get("WINDMILL_WORKSPACE"), (
        "WINDMILL_WORKSPACE environment variable is not set; required to target the correct "
        "Windmill cloud workspace."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    assert re.fullmatch(r"zr-[a-z0-9]+", run_id), (
        f"ZEALT_RUN_ID '{run_id}' does not match expected pattern 'zr-[a-z0-9]+'."
    )


def test_wmill_workspace_registered():
    """Confirm the cloud workspace is registered after the autouse setup ran."""
    result = subprocess.run(
        ["wmill", "workspace", "list"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"`wmill workspace list` failed (rc={result.returncode}). "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    combined = result.stdout + result.stderr
    assert "app.windmill.dev" in combined, (
        "No Windmill cloud workspace is registered with `wmill workspace add`. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_initial_script_not_present():
    """Sanity: the agent's deliverable must NOT already exist before evaluation."""
    target = os.path.join(PROJECT_DIR, "f", "eval", "fanout_workflow.ts")
    assert not os.path.exists(target), (
        f"Initial state must not contain {target}; the agent is supposed to create it."
    )
