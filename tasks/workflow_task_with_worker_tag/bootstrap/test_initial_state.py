import os
import shutil
import pathlib
import re
import pytest


WORKFLOW_FILE = pathlib.Path("/home/user/windmill-project/f/workflows/ml_pipeline.ts")
PROJECT_DIR = pathlib.Path("/home/user/windmill-project")


def test_wmill_binary_in_path():
    """wmill CLI must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. Ensure windmill-cli is installed (npm install -g windmill-cli)."
    )


def test_project_directory_exists():
    """The windmill project directory must exist."""
    assert PROJECT_DIR.is_dir(), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_workflow_file_exists():
    """The ml_pipeline.ts workflow file must exist."""
    assert WORKFLOW_FILE.is_file(), (
        f"Workflow file {WORKFLOW_FILE} does not exist."
    )


def test_file_does_not_contain_gpu_tag():
    """Initial broken state: file must NOT already contain the gpu tag."""
    content = WORKFLOW_FILE.read_text()
    assert not re.search(r"tag\s*:\s*['\"]gpu['\"]", content), (
        "Expected broken initial state: `tag: 'gpu'` should not be present in the file yet. "
        "The file may already be partially or fully fixed."
    )


def test_file_contains_train_model_task_without_tag():
    """Initial broken state: task(trainModel) must be present without an options argument."""
    content = WORKFLOW_FILE.read_text()
    # The broken pattern: task(trainModel) with no second argument
    assert re.search(r"task\s*\(\s*trainModel\s*\)\s*\(", content), (
        "Expected broken initial state: `task(trainModel)(...)` without tag options not found. "
        "The file may already be partially or fully fixed."
    )


def test_file_contains_preprocess_data_task():
    """The task(preprocessData) call must be present in the broken file."""
    content = WORKFLOW_FILE.read_text()
    assert "task(preprocessData)" in content, (
        "task(preprocessData) call not found in workflow file."
    )


def test_workflow_file_is_typescript():
    """The workflow file must have a .ts extension and contain TypeScript-like content."""
    assert WORKFLOW_FILE.suffix == ".ts", (
        f"Expected a .ts file, got {WORKFLOW_FILE.suffix}."
    )
    content = WORKFLOW_FILE.read_text()
    assert "export const main" in content, (
        "Expected `export const main` in the workflow file."
    )


def test_workflow_wrapper_present():
    """The workflow() wrapper must be present in the initial file."""
    content = WORKFLOW_FILE.read_text()
    assert "workflow(" in content, (
        "Expected `workflow(` to be present in ml_pipeline.ts."
    )
