import os
import pytest

PROJECT_DIR = "/home/user/windmill-project"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "f", "workflows", "data_pipeline.ts")
YAML_FILE = os.path.join(PROJECT_DIR, "f", "workflows", "data_pipeline.script.yaml")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _read_workflow() -> str:
    with open(WORKFLOW_FILE, "r") as fh:
        return fh.read()


def _read_yaml() -> str:
    with open(YAML_FILE, "r") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_workflow_file_exists():
    assert os.path.isfile(WORKFLOW_FILE), (
        f"Workflow file not found at '{WORKFLOW_FILE}'. "
        "Create 'f/workflows/data_pipeline.ts' inside the project directory."
    )


def test_companion_yaml_exists():
    assert os.path.isfile(YAML_FILE), (
        f"Companion YAML not found at '{YAML_FILE}'. "
        "Create 'f/workflows/data_pipeline.script.yaml' alongside the TypeScript file."
    )


# ---------------------------------------------------------------------------
# Import checks
# ---------------------------------------------------------------------------

def test_imports_workflow_from_windmill_client():
    content = _read_workflow()
    assert "workflow" in content, (
        "Expected 'workflow' to be imported from 'windmill-client' in data_pipeline.ts."
    )
    assert "windmill-client" in content, (
        "Expected import from 'windmill-client' in data_pipeline.ts."
    )


def test_imports_task_from_windmill_client():
    content = _read_workflow()
    assert "task" in content, (
        "Expected 'task' to be imported from 'windmill-client' in data_pipeline.ts."
    )


# ---------------------------------------------------------------------------
# Export: main = workflow(...)
# ---------------------------------------------------------------------------

def test_exports_main_as_workflow():
    content = _read_workflow()
    assert "export const main" in content or "export const main=" in content.replace(" ", ""), (
        "Expected 'export const main' to be present in data_pipeline.ts."
    )
    assert "workflow(" in content, (
        "Expected 'main' to be assigned to a 'workflow(...)' call in data_pipeline.ts."
    )


# ---------------------------------------------------------------------------
# Task function definitions
# ---------------------------------------------------------------------------

def test_defines_validate_input_function():
    content = _read_workflow()
    assert "validateInput" in content, (
        "Expected async function 'validateInput' to be defined in data_pipeline.ts."
    )


def test_defines_transform_data_function():
    content = _read_workflow()
    assert "transformData" in content, (
        "Expected async function 'transformData' to be defined in data_pipeline.ts."
    )


def test_defines_format_output_function():
    content = _read_workflow()
    assert "formatOutput" in content, (
        "Expected async function 'formatOutput' to be defined in data_pipeline.ts."
    )


# ---------------------------------------------------------------------------
# Task chaining within workflow body
# ---------------------------------------------------------------------------

def test_workflow_calls_task_validate_input():
    content = _read_workflow()
    assert "task(validateInput)" in content, (
        "Expected 'task(validateInput)' to be called inside the workflow body in data_pipeline.ts."
    )


def test_workflow_calls_task_transform_data():
    content = _read_workflow()
    assert "task(transformData)" in content, (
        "Expected 'task(transformData)' to be called inside the workflow body in data_pipeline.ts."
    )


def test_workflow_calls_task_format_output():
    content = _read_workflow()
    assert "task(formatOutput)" in content, (
        "Expected 'task(formatOutput)' to be called inside the workflow body in data_pipeline.ts."
    )


def test_workflow_chain_order():
    """Verify the three task() calls appear in the correct sequential order."""
    content = _read_workflow()
    idx_validate = content.find("task(validateInput)")
    idx_transform = content.find("task(transformData)")
    idx_format = content.find("task(formatOutput)")
    assert idx_validate != -1, "task(validateInput) not found in data_pipeline.ts."
    assert idx_transform != -1, "task(transformData) not found in data_pipeline.ts."
    assert idx_format != -1, "task(formatOutput) not found in data_pipeline.ts."
    assert idx_validate < idx_transform, (
        "task(validateInput) must appear before task(transformData) in the workflow body."
    )
    assert idx_transform < idx_format, (
        "task(transformData) must appear before task(formatOutput) in the workflow body."
    )


# ---------------------------------------------------------------------------
# validateInput semantics
# ---------------------------------------------------------------------------

def test_validate_input_uses_trim():
    content = _read_workflow()
    assert "trim()" in content, (
        "Expected 'trim()' to be called inside 'validateInput' to strip whitespace."
    )


def test_validate_input_throws_on_empty():
    content = _read_workflow()
    assert "throw" in content, (
        "Expected 'validateInput' to throw an error when input is empty."
    )


# ---------------------------------------------------------------------------
# transformData semantics
# ---------------------------------------------------------------------------

def test_transform_data_includes_original_key():
    content = _read_workflow()
    assert "original" in content, (
        "Expected 'transformData' to include an 'original' key in the returned object."
    )


def test_transform_data_includes_upper_key():
    content = _read_workflow()
    assert "upper" in content, (
        "Expected 'transformData' to include an 'upper' key (toUpperCase result)."
    )
    assert "toUpperCase" in content, (
        "Expected 'toUpperCase()' to be called inside 'transformData'."
    )


def test_transform_data_includes_word_count_key():
    content = _read_workflow()
    assert "word_count" in content, (
        "Expected 'transformData' to include a 'word_count' key in the returned object."
    )


# ---------------------------------------------------------------------------
# formatOutput semantics
# ---------------------------------------------------------------------------

def test_format_output_spreads_data():
    content = _read_workflow()
    # The spread operator applied to the incoming data object
    assert "...data" in content or "...transformed" in content or "...result" in content or "..." in content, (
        "Expected 'formatOutput' to spread the incoming data object using the spread operator '...'."
    )


def test_format_output_includes_processed_at():
    content = _read_workflow()
    assert "processed_at" in content, (
        "Expected 'formatOutput' to add a 'processed_at' key to the output object."
    )
    assert "toISOString" in content, (
        "Expected 'new Date().toISOString()' to be used for the 'processed_at' value."
    )


def test_format_output_includes_status_complete():
    content = _read_workflow()
    assert "status" in content, (
        "Expected 'formatOutput' to add a 'status' key to the output object."
    )
    assert "complete" in content, (
        "Expected the 'status' field to have the value 'complete' in 'formatOutput'."
    )


# ---------------------------------------------------------------------------
# Companion YAML checks
# ---------------------------------------------------------------------------

def test_yaml_mentions_raw_input():
    content = _read_yaml()
    assert "raw_input" in content, (
        "Expected 'data_pipeline.script.yaml' to declare 'raw_input' as a parameter in its schema."
    )
