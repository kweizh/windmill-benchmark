import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/windmill-project"


def test_python3_available():
    assert shutil.which("python3") is not None, (
        "python3 binary not found in PATH. python3 must be installed."
    )


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI binary not found in PATH. "
        "Install it with: npm install -g windmill-cli"
    )


def test_wmill_python_package_importable():
    result = subprocess.run(
        ["python3", "-c", "import wmill"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Python package 'wmill' could not be imported. "
        f"Install it with: pip3 install --break-system-packages wmill\n"
        f"stderr: {result.stderr}"
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Windmill project directory '{PROJECT_DIR}' does not exist. "
        "It should be pre-created in the task environment."
    )
