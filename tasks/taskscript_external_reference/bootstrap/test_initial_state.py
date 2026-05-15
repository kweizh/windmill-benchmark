import os
import shutil
import pytest

PROJECT_DIR = "/home/user/windmill-project"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "f", "workflows", "data_orchestrator.ts")


def _read_file() -> str:
    with open(WORKFLOW_FILE, "r") as fh:
        return fh.read()


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


def test_workflow_file_exists():
    assert os.path.isfile(WORKFLOW_FILE), (
        f"Workflow file not found at '{WORKFLOW_FILE}'. "
        "The broken data_orchestrator.ts must exist before the agent starts."
    )


def test_file_does_not_contain_taskscript_import():
    content = _read_file()
    assert "taskScript" not in content, (
        "The file already contains 'taskScript' — it should NOT be refactored yet. "
        "The initial state must have inline task functions only."
    )


def test_file_contains_extract_users_function():
    content = _read_file()
    assert "async function extractUsers" in content, (
        "Expected 'async function extractUsers' to be defined in the initial file. "
        "The inline extractUsers function must be present before refactoring."
    )


def test_file_contains_transform_records_function():
    content = _read_file()
    assert "async function transformRecords" in content, (
        "Expected 'async function transformRecords' to be defined in the initial file. "
        "The inline transformRecords function must be present before refactoring."
    )
