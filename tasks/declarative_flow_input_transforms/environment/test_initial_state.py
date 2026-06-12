import os
import shutil

import pytest

PROJECT_DIR = "/home/user/wmill-project"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI binary not found in PATH. The windmill-cli npm package must be installed."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_wmill_token_env_present():
    assert os.environ.get("WMILL_TOKEN"), (
        "WMILL_TOKEN environment variable is not set; required to authenticate against the cloud Windmill instance."
    )


def test_wmill_workspace_env_present():
    assert os.environ.get("WMILL_WORKSPACE"), (
        "WMILL_WORKSPACE environment variable is not set; required to identify the target Windmill workspace."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable is not set; required for parallel-run safety."
    assert run_id.startswith("zr-"), (
        f"ZEALT_RUN_ID must match pattern 'zr-[a-z0-9]+'; got '{run_id}'."
    )
