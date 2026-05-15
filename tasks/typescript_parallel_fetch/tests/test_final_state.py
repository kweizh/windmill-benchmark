import os
import pytest

SCRIPT_PATH = "/home/user/windmill-project/f/workflows/parallel_status_check.ts"
YAML_PATH = "/home/user/windmill-project/f/workflows/parallel_status_check.script.yaml"


def _read_script():
    with open(SCRIPT_PATH) as f:
        return f.read()


def test_typescript_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"TypeScript workflow script not found at {SCRIPT_PATH}. "
        "The file must be created as part of this task."
    )


def test_imports_workflow_from_windmill_client():
    content = _read_script()
    assert "workflow" in content and "windmill-client" in content, (
        "Expected 'workflow' to be imported from 'windmill-client' in "
        f"{SCRIPT_PATH}, but it was not found."
    )


def test_imports_parallel_from_windmill_client():
    content = _read_script()
    assert "parallel" in content and "windmill-client" in content, (
        "Expected 'parallel' to be imported from 'windmill-client' in "
        f"{SCRIPT_PATH}, but it was not found."
    )


def test_imports_task_from_windmill_client():
    content = _read_script()
    assert "task" in content and "windmill-client" in content, (
        "Expected 'task' to be imported from 'windmill-client' in "
        f"{SCRIPT_PATH}, but it was not found."
    )


def test_defines_check_url_function():
    content = _read_script()
    assert "checkUrl" in content, (
        f"Expected an async function named 'checkUrl' to be defined in {SCRIPT_PATH}, "
        "but it was not found."
    )


def test_check_url_accepts_url_parameter():
    content = _read_script()
    assert "url" in content and "string" in content, (
        f"Expected 'checkUrl' to accept a 'url: string' parameter in {SCRIPT_PATH}."
    )


def test_check_url_returns_ok_field():
    content = _read_script()
    assert "ok" in content, (
        f"Expected 'checkUrl' to return an object with an 'ok' field in {SCRIPT_PATH}."
    )


def test_check_url_returns_status_field():
    content = _read_script()
    assert "status" in content, (
        f"Expected 'checkUrl' to return an object with a 'status' field in {SCRIPT_PATH}."
    )


def test_exports_main_as_workflow():
    content = _read_script()
    assert "export" in content and "main" in content and "workflow(" in content, (
        f"Expected 'export const main = workflow(...)' in {SCRIPT_PATH}, "
        "but it was not found."
    )


def test_uses_parallel_call():
    content = _read_script()
    assert "parallel(" in content, (
        f"Expected 'parallel(...)' to be called inside the workflow body in {SCRIPT_PATH}."
    )


def test_parallel_concurrency_is_3():
    content = _read_script()
    assert "concurrency" in content and "3" in content, (
        f"Expected parallel() to be called with a concurrency value of 3 in {SCRIPT_PATH}."
    )


def test_return_includes_summary_field():
    content = _read_script()
    assert "summary" in content, (
        f"Expected the workflow to return an object with a 'summary' field in {SCRIPT_PATH}."
    )


def test_companion_yaml_exists():
    assert os.path.isfile(YAML_PATH), (
        f"Companion YAML metadata file not found at {YAML_PATH}. "
        "The .script.yaml file must be created alongside the TypeScript script."
    )
