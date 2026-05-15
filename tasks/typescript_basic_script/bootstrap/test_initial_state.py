import os
import shutil
import pytest

PROJECT_DIR = "/home/user/windmill-project"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "f", "scripts", "greet.ts")
METADATA_PATH = os.path.join(PROJECT_DIR, "f", "scripts", "greet.script.yaml")


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. "
        "Ensure windmill-cli is installed via 'npm install -g windmill-cli'."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory '{PROJECT_DIR}' does not exist. "
        "The Windmill project scaffold should be present before the task starts."
    )


def test_greet_script_not_yet_created():
    assert not os.path.exists(SCRIPT_PATH), (
        f"Script file '{SCRIPT_PATH}' already exists before the task starts. "
        "It should be created by the user as part of this task."
    )


def test_greet_metadata_not_yet_created():
    assert not os.path.exists(METADATA_PATH), (
        f"Metadata file '{METADATA_PATH}' already exists before the task starts. "
        "It should be created by the user as part of this task."
    )
