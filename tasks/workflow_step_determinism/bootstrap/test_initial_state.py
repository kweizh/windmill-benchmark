import os
import shutil
import pathlib
import re
import pytest


WORKFLOW_FILE = pathlib.Path("/home/user/windmill-project/f/workflows/order_processor.ts")
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
    """The order_processor.ts workflow file must exist."""
    assert WORKFLOW_FILE.is_file(), (
        f"Workflow file {WORKFLOW_FILE} does not exist."
    )


def test_file_contains_bare_date_now():
    """Initial broken state: Date.now() must appear directly in the workflow body (not inside step())."""
    content = WORKFLOW_FILE.read_text()
    # Match bare `Date.now()` that is NOT preceded by `step(` context.
    # The broken pattern is: `const timestamp = Date.now();`
    assert re.search(r"const\s+timestamp\s*=\s*Date\.now\(\)", content), (
        "Expected broken initial state: bare `const timestamp = Date.now()` not found in workflow file. "
        "The file may already be partially or fully fixed."
    )


def test_file_contains_bare_math_random():
    """Initial broken state: Math.random() must appear directly in the workflow body (not inside step())."""
    content = WORKFLOW_FILE.read_text()
    # The broken pattern is: `const orderId = Math.random().toString(36).slice(2);`
    assert re.search(r"const\s+orderId\s*=\s*Math\.random\(\)", content), (
        "Expected broken initial state: bare `const orderId = Math.random()` not found in workflow file. "
        "The file may already be partially or fully fixed."
    )


def test_step_not_imported():
    """Initial broken state: `step` should NOT be imported from windmill-client yet."""
    content = WORKFLOW_FILE.read_text()
    # The broken file only imports `task` and `workflow`, not `step`
    assert not re.search(r"\bstep\b", content), (
        "Expected broken initial state: `step` should not be present in the file before the fix."
    )


def test_task_calls_present():
    """The task() calls for processOrder and notifyShipping must be present in the broken file."""
    content = WORKFLOW_FILE.read_text()
    assert "task(processOrder)" in content, (
        "task(processOrder) call not found in workflow file."
    )
    assert "task(notifyShipping)" in content, (
        "task(notifyShipping) call not found in workflow file."
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
