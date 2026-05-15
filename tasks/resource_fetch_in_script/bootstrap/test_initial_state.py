import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/windmill-project"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. "
        "Install with: npm install -g windmill-cli"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Windmill project directory {PROJECT_DIR!r} does not exist."
    )
