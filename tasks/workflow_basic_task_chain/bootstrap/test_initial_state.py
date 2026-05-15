import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/windmill-project"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. "
        "The Windmill CLI (wmill) must be installed and accessible."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory '{PROJECT_DIR}' does not exist. "
        "The Windmill project directory must be pre-created before the task."
    )
