import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/myproject"
WINDMILL_REMOTE = "https://app.windmill.dev"


def _ensure_workspace_added():
    """Register the cloud workspace with the locally installed wmill CLI.

    The token and workspace id are provided via the WMILL_TOKEN and
    WMILL_WORKSPACE_ID environment variables.
    """
    token = os.environ.get("WMILL_TOKEN")
    workspace_id = os.environ.get("WMILL_WORKSPACE_ID")
    assert token, "WMILL_TOKEN environment variable must be set."
    assert workspace_id, "WMILL_WORKSPACE_ID environment variable must be set."

    # Idempotent: re-adding the same workspace simply updates the stored token.
    add_result = subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            workspace_id,
            workspace_id,
            WINDMILL_REMOTE,
            "--token",
            token,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert add_result.returncode == 0, (
        "`wmill workspace add` failed while preparing the initial environment. "
        f"stdout: {add_result.stdout!r} stderr: {add_result.stderr!r}"
    )

    switch_result = subprocess.run(
        ["wmill", "workspace", "switch", workspace_id],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert switch_result.returncode == 0, (
        "`wmill workspace switch` failed while preparing the initial environment. "
        f"stdout: {switch_result.stdout!r} stderr: {switch_result.stderr!r}"
    )


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI binary not found in PATH; the Windmill CLI must be pre-installed."
    )


def test_bash_available():
    assert shutil.which("bash") is not None, "bash binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_zealt_run_id_env_var_set():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    assert run_id.startswith("zr-"), (
        f"ZEALT_RUN_ID does not match the expected 'zr-...' format: {run_id!r}"
    )


def test_cloud_workspace_registered_and_reachable():
    _ensure_workspace_added()
    result = subprocess.run(
        ["wmill", "workspace", "list"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        "`wmill workspace list` failed; the CLI must be authenticated against the "
        f"cloud workspace. stderr: {result.stderr!r}"
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert "windmill.dev" in combined, (
        "`wmill workspace list` output does not reference the cloud-hosted "
        f"Windmill instance. Output: {combined!r}"
    )
    workspace_id = os.environ.get("WMILL_WORKSPACE_ID", "")
    assert workspace_id and workspace_id in combined, (
        "Expected the configured workspace id to be present in "
        f"`wmill workspace list` output. workspace_id={workspace_id!r}, "
        f"output={combined!r}"
    )
