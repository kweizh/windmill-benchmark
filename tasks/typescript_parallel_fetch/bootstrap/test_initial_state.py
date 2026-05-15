import os
import shutil
import pytest

PROJECT_DIR = "/home/user/windmill-project"
WORKFLOWS_DIR = os.path.join(PROJECT_DIR, "f", "workflows")


def test_wmill_binary_in_path():
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. "
        "The Windmill CLI (wmill) must be installed and available on PATH."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. "
        "The windmill-project directory must be created before the task begins."
    )


def test_workflows_directory_exists():
    assert os.path.isdir(WORKFLOWS_DIR), (
        f"Workflows directory {WORKFLOWS_DIR} does not exist. "
        "The f/workflows subdirectory must be present in the project."
    )
