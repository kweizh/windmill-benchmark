import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/wac_accumulator"
WORKSPACE_NAME = "evaluation-ws"
WORKSPACE_ID = "evaluation-ws"
WINDMILL_REMOTE = "https://app.windmill.dev"


def _ensure_workspace_registered():
    """Register the cloud workspace with the wmill CLI using the runtime
    API token from the environment. Idempotent: if the workspace is already
    configured, this is a no-op.
    """
    token = os.environ.get("WMILL_TOKEN")
    assert token, "WMILL_TOKEN environment variable must be set."
    # Run unconditionally; the CLI will overwrite/create the named workspace.
    result = subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            WORKSPACE_NAME,
            WORKSPACE_ID,
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
        f"Failed to register workspace '{WORKSPACE_NAME}'. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    switch = subprocess.run(
        ["wmill", "workspace", "switch", WORKSPACE_NAME],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert switch.returncode == 0, (
        f"Failed to switch to workspace '{WORKSPACE_NAME}'. "
        f"stdout={switch.stdout!r} stderr={switch.stderr!r}"
    )


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "The 'wmill' (windmill-cli) binary must be available in PATH."
    )


def test_node_available():
    assert shutil.which("node") is not None, (
        "Node.js must be installed for windmill-cli to run."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected the bootstrapped project directory at {PROJECT_DIR}."
    )


def test_wmill_yaml_exists():
    yaml_path = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert os.path.isfile(yaml_path), (
        f"Expected a bootstrapped wmill.yaml at {yaml_path}."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable must be set in the task environment."
    )


def test_wmill_token_env_present():
    token = os.environ.get("WMILL_TOKEN")
    assert token, "WMILL_TOKEN environment variable must be set."


def test_workspace_registered_and_active():
    _ensure_workspace_registered()
    result = subprocess.run(
        ["wmill", "workspace", "list"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"'wmill workspace list' failed with code {result.returncode}: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert WORKSPACE_NAME in result.stdout, (
        f"Expected workspace '{WORKSPACE_NAME}' to be registered. "
        f"Got: {result.stdout!r}"
    )


def test_workspace_whoami_reachable():
    """Sanity-check that the configured token can actually authenticate
    against the cloud workspace before the agent begins the task."""
    _ensure_workspace_registered()
    result = subprocess.run(
        ["wmill", "workspace", "whoami"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"'wmill workspace whoami' failed (rc={result.returncode}). "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
