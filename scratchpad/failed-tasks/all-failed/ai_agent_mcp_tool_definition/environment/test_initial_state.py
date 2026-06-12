import os
import shutil


PROJECT_DIR = "/home/user/wm-agent"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "Windmill CLI (`wmill`) is not available on PATH. "
        "The task environment must ship the Windmill CLI."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_wmill_token_env_present():
    assert os.environ.get("WMILL_TOKEN"), (
        "WMILL_TOKEN environment variable is not set; "
        "the executor needs it to authenticate against the cloud Windmill instance."
    )


def test_wmill_workspace_env_present():
    assert os.environ.get("WMILL_WORKSPACE"), (
        "WMILL_WORKSPACE environment variable is not set; "
        "the executor needs it to target the cloud Windmill workspace."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, (
        "ZEALT_RUN_ID environment variable is not set; "
        "it is required for parallel-run-safe resource naming."
    )


def test_deploy_log_not_yet_created():
    log_path = os.path.join(PROJECT_DIR, "deploy.log")
    assert not os.path.exists(log_path), (
        f"{log_path} already exists; it should be created by the executor "
        "as part of the task."
    )
