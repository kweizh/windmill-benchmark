import os
import shutil
import pytest

PROJECT_DIR = "/home/user/windmill-project"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "f", "workflows", "report_generator.ts")


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


def test_workflow_file_does_not_exist():
    assert not os.path.exists(WORKFLOW_FILE), (
        f"Workflow file '{WORKFLOW_FILE}' already exists. "
        "It must NOT be present in the initial state — the agent must create it."
    )
