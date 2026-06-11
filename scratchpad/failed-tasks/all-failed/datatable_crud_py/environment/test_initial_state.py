import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/wmill-project"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI not found in PATH. "
        "It should have been installed via `npm install -g windmill-cli` in the Dockerfile."
    )


def test_wmill_cli_runs():
    result = subprocess.run(
        ["wmill", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"`wmill --version` failed with exit code {result.returncode}. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_node_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH. Node >= 20 is required by windmill-cli."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. "
        "The Dockerfile should have created it as the working directory for the task."
    )


def test_windmill_env_vars_present():
    for key in ("WINDMILL_TOKEN", "WINDMILL_WORKSPACE"):
        assert os.environ.get(key), (
            f"Environment variable {key} is required for the task to authenticate against "
            "https://app.windmill.dev but is missing or empty."
        )


def test_zealt_run_id_present():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id.strip() != "", (
        "ZEALT_RUN_ID environment variable is required so the agent can derive a unique "
        "table name for the shared Windmill cloud workspace."
    )
