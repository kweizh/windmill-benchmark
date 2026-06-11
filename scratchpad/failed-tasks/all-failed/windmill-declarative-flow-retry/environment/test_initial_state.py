import os
import shutil


PROJECT_DIR = "/home/user/windmill-project"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "Windmill CLI (`wmill`) was not found on PATH. The initial environment must "
        "ship with the Windmill CLI pre-installed."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist; it must be created during "
        "environment setup so the executor can author Windmill assets there."
    )


def test_windmill_token_env_present():
    token = os.environ.get("WINDMILL_TOKEN")
    assert token is not None and token.strip() != "", (
        "Environment variable WINDMILL_TOKEN must be set so the executor can "
        "authenticate against https://app.windmill.dev."
    )


def test_windmill_workspace_env_present():
    workspace = os.environ.get("WINDMILL_WORKSPACE")
    assert workspace is not None and workspace.strip() != "", (
        "Environment variable WINDMILL_WORKSPACE must be set so the executor can "
        "target the correct Windmill cloud workspace."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id is not None and run_id.strip() != "", (
        "Environment variable ZEALT_RUN_ID must be set so the task can derive a "
        "collision-safe Windmill folder suffix for concurrent runs."
    )
