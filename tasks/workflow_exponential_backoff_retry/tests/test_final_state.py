import re
from pathlib import Path

API_CALLER_FILE = Path("/home/user/windmill-project/f/workflows/api_caller.ts")


def _read_file() -> str:
    return API_CALLER_FILE.read_text()


def test_file_exists():
    """The api_caller.ts workflow file must exist after the task."""
    assert API_CALLER_FILE.exists(), (
        f"api_caller.ts not found at: {API_CALLER_FILE}"
    )
    assert API_CALLER_FILE.is_file(), (
        f"Expected a file at: {API_CALLER_FILE}"
    )


def test_sleep_imported_from_windmill_client():
    """The file must import `sleep` from 'windmill-client'."""
    content = _read_file()
    pattern = r"""import\s*\{[^}]*\bsleep\b[^}]*\}\s*from\s*['"]windmill-client['"]"""
    assert re.search(pattern, content), (
        "Expected 'sleep' to be imported from 'windmill-client', but the import was not found.\n"
        f"File content:\n{content}"
    )


def test_await_sleep_present():
    """The file must call `await sleep(` for the backoff delay."""
    content = _read_file()
    assert re.search(r"await\s+sleep\s*\(", content), (
        "Expected 'await sleep(' in api_caller.ts for the exponential backoff delay, "
        "but it was not found.\n"
        f"File content:\n{content}"
    )


def test_exponential_calculation_present():
    """The file must use Math.pow(2, ...) or 2 ** ... for exponential delay calculation."""
    content = _read_file()
    has_math_pow = re.search(r"Math\.pow\s*\(\s*2\s*,", content)
    has_exponent_operator = re.search(r"2\s*\*\*\s*", content)
    assert has_math_pow or has_exponent_operator, (
        "Expected an exponential delay calculation using 'Math.pow(2,' or '2 **' "
        "in api_caller.ts, but neither was found.\n"
        f"File content:\n{content}"
    )


def test_try_block_present():
    """The file must contain a try block for per-attempt error handling."""
    content = _read_file()
    assert re.search(r"\btry\s*\{", content), (
        "Expected a 'try {' block in api_caller.ts for retry error handling, "
        "but it was not found.\n"
        f"File content:\n{content}"
    )


def test_catch_block_present():
    """The file must contain a catch block to handle failed attempts."""
    content = _read_file()
    assert re.search(r"\bcatch\s*\(", content), (
        "Expected a 'catch (' block in api_caller.ts for retry error handling, "
        "but it was not found.\n"
        f"File content:\n{content}"
    )


def test_workflow_export_present():
    """The file must export a workflow using workflow(...)."""
    content = _read_file()
    assert re.search(r"\bworkflow\s*\(", content), (
        "Expected 'workflow(' export in api_caller.ts, but it was not found.\n"
        f"File content:\n{content}"
    )


def test_task_call_api_present():
    """The workflow must call task(callApi) inside the retry loop."""
    content = _read_file()
    assert "task(callApi)" in content, (
        "Expected 'task(callApi)' in api_caller.ts, but it was not found.\n"
        f"File content:\n{content}"
    )


def test_max_retries_referenced():
    """The file must reference maxRetries to control the retry loop."""
    content = _read_file()
    assert "maxRetries" in content, (
        "Expected 'maxRetries' parameter to be referenced in api_caller.ts, "
        "but it was not found.\n"
        f"File content:\n{content}"
    )
