import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"


def _run(cmd, cwd=None, env=None, timeout=120):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI binary not found in PATH; the Windmill CLI must be installed for this task."
    )


def test_node_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH; Node.js is required to build full-code apps."
    )


def test_npm_available():
    assert shutil.which("npm") is not None, (
        "npm binary not found in PATH; npm is required to install full-code app dependencies."
    )


def test_required_env_vars_set():
    for var in ("WM_TOKEN", "WM_WORKSPACE", "ZEALT_RUN_ID"):
        value = os.environ.get(var)
        assert value, f"Environment variable {var} must be set before running the task."


def test_project_dir_setup():
    """Ensure the project directory exists. The Dockerfile creates it."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist; the Dockerfile must create it."
    )


def test_wmill_workspace_configured():
    """
    Register the cloud Windmill workspace with the local CLI using credentials provided
    via environment variables. This step is idempotent: re-running it on an already
    configured workspace is treated as a no-op.
    """
    workspace = os.environ["WM_WORKSPACE"]
    token = os.environ["WM_TOKEN"]
    base_url = os.environ.get("WM_BASE_URL", "https://app.windmill.dev").rstrip("/")

    # `wmill workspace add <name> <workspace_id> <remote_url> --token <token>`
    add = _run(
        [
            "wmill",
            "workspace",
            "add",
            workspace,
            workspace,
            base_url,
            "--token",
            token,
        ],
        cwd=PROJECT_DIR,
    )
    # If the workspace was already added in a previous run, the CLI returns a non-zero
    # exit code but the configuration is still valid. We tolerate that case and rely on
    # `wmill workspace list` below as the definitive check.
    if add.returncode != 0:
        assert "already" in (add.stdout + add.stderr).lower() or workspace in (
            add.stdout + add.stderr
        ), f"`wmill workspace add` failed: stdout={add.stdout} stderr={add.stderr}"

    # Ensure the workspace is the active one.
    _run(["wmill", "workspace", "switch", workspace], cwd=PROJECT_DIR)

    listing = _run(["wmill", "workspace", "list"], cwd=PROJECT_DIR)
    assert listing.returncode == 0, (
        f"`wmill workspace list` failed: stdout={listing.stdout} stderr={listing.stderr}"
    )
    assert workspace in listing.stdout, (
        f"Workspace {workspace!r} not found in `wmill workspace list` output:\n{listing.stdout}"
    )


def test_wmill_yaml_initialised():
    """Ensure a wmill.yaml file exists in the project directory."""
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    if not os.path.isfile(wmill_yaml):
        # `wmill init` creates the wmill.yaml file. Run it from the project directory.
        result = _run(["wmill", "init"], cwd=PROJECT_DIR)
        assert result.returncode == 0 or os.path.isfile(wmill_yaml), (
            f"`wmill init` failed and wmill.yaml is missing: "
            f"stdout={result.stdout} stderr={result.stderr}"
        )
    assert os.path.isfile(wmill_yaml), (
        f"Expected {wmill_yaml} to exist after `wmill init`."
    )


def test_app_scaffold_not_yet_present():
    """Ensure no leftover scaffold from a previous run interferes with verification."""
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    safe_run_id = run_id.replace("-", "_")
    base = os.path.join(PROJECT_DIR, "f", "harbor")
    if not os.path.isdir(base):
        return
    for name in os.listdir(base):
        assert not (
            name == f"fullcode_{safe_run_id}.raw_app"
            or name == f"fullcode_{safe_run_id}__raw_app"
        ), f"Unexpected pre-existing scaffold directory: {os.path.join(base, name)}"
