import os
import pytest

PROJECT_DIR = "/home/user/windmill-project"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "f", "workflows", "data_orchestrator.ts")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _read_file() -> str:
    with open(WORKFLOW_FILE, "r") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_workflow_file_exists():
    assert os.path.isfile(WORKFLOW_FILE), (
        f"Workflow file not found at '{WORKFLOW_FILE}'. "
        "The file must exist after refactoring."
    )


# ---------------------------------------------------------------------------
# Import checks
# ---------------------------------------------------------------------------

def test_imports_taskscript_from_windmill_client():
    content = _read_file()
    assert "taskScript" in content, (
        "Expected 'taskScript' to be imported from 'windmill-client'. "
        "Add 'taskScript' to the import statement, e.g.: "
        "import { task, taskScript, workflow } from 'windmill-client';"
    )
    assert "windmill-client" in content, (
        "Expected an import from 'windmill-client' in data_orchestrator.ts."
    )


# ---------------------------------------------------------------------------
# taskScript() call checks
# ---------------------------------------------------------------------------

def test_calls_taskscript_extract_users():
    content = _read_file()
    assert "taskScript('f/data/extract_users')" in content or \
           'taskScript("f/data/extract_users")' in content, (
        "Expected 'taskScript('f/data/extract_users')' to be present in data_orchestrator.ts. "
        "Replace the inline task(extractUsers) call with taskScript('f/data/extract_users')."
    )


def test_calls_taskscript_transform_records():
    content = _read_file()
    assert "taskScript('f/data/transform_records')" in content or \
           'taskScript("f/data/transform_records")' in content, (
        "Expected 'taskScript('f/data/transform_records')' to be present in data_orchestrator.ts. "
        "Replace the inline task(transformRecords) call with taskScript('f/data/transform_records')."
    )


# ---------------------------------------------------------------------------
# saveResults inline task must be preserved
# ---------------------------------------------------------------------------

def test_save_results_still_inline():
    content = _read_file()
    assert "task(saveResults)" in content, (
        "Expected 'task(saveResults)' to still be present in data_orchestrator.ts. "
        "The saveResults function must remain as an inline task — do NOT convert it to taskScript()."
    )


# ---------------------------------------------------------------------------
# Removed inline function definitions
# ---------------------------------------------------------------------------

def test_extract_users_function_removed():
    content = _read_file()
    count = content.count("async function extractUsers")
    assert count == 0, (
        f"Found {count} occurrence(s) of 'async function extractUsers' in data_orchestrator.ts. "
        "The inline extractUsers function definition must be completely removed after refactoring."
    )


def test_transform_records_function_removed():
    content = _read_file()
    count = content.count("async function transformRecords")
    assert count == 0, (
        f"Found {count} occurrence(s) of 'async function transformRecords' in data_orchestrator.ts. "
        "The inline transformRecords function definition must be completely removed after refactoring."
    )


# ---------------------------------------------------------------------------
# workflow() wrapper still present
# ---------------------------------------------------------------------------

def test_workflow_wrapper_present():
    content = _read_file()
    assert "workflow(" in content, (
        "Expected 'workflow(' to still be present in data_orchestrator.ts. "
        "The exported main must still be wrapped in a workflow() call."
    )
