"""
Final state tests for multi_stage_etl_with_approval task.

Priority 3 — File content checks (no Windmill CLI can introspect local TypeScript source).

Verifies that the agent correctly created
/home/user/windmill-project/f/workflows/etl_with_approval.ts
with all required WAC primitives and workflow logic.

Truth conditions verified:
  1.  File exists at the specified path.
  2.  `step` is imported from 'windmill-client'.
  3.  `getResumeUrls` is imported from 'windmill-client'.
  4.  `waitForApproval` is imported from 'windmill-client'.
  5.  `parallel` is imported from 'windmill-client'.
  6.  `await step('run_id'` and `crypto.randomUUID()` are both present.
  7.  `parallel(` appears at least twice.
  8.  `await step(` and `getResumeUrls()` are both present.
  9.  `waitForApproval({ timeout: 3600 })` is present.
  10. `status: 'rejected'` (rejection branch) is present.
  11. `task(loadData)` (approval branch load call) is present.
  12. `try` and `catch` are both present (extractEndpoint error handling).
"""

import os
import re

TARGET_FILE = "/home/user/windmill-project/f/workflows/etl_with_approval.ts"


def _read_file() -> str:
    """Read and return the content of the target file."""
    with open(TARGET_FILE, "r", encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# 1. File existence
# ---------------------------------------------------------------------------

def test_file_exists():
    """The workflow file must exist at the specified path."""
    assert os.path.isfile(TARGET_FILE), (
        f"Expected file '{TARGET_FILE}' to exist, but it was not found."
    )


# ---------------------------------------------------------------------------
# 2. `step` imported from windmill-client
# ---------------------------------------------------------------------------

def test_step_imported_from_windmill_client():
    """`step` must be imported from 'windmill-client'."""
    content = _read_file()
    pattern = r"""import\s+[^;]*\bstep\b[^;]*from\s+['"]windmill-client['"]"""
    assert re.search(pattern, content), (
        "Expected 'step' to be imported from 'windmill-client', "
        "but the import statement was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 3. `getResumeUrls` imported from windmill-client
# ---------------------------------------------------------------------------

def test_get_resume_urls_imported_from_windmill_client():
    """`getResumeUrls` must be imported from 'windmill-client'."""
    content = _read_file()
    pattern = r"""import\s+[^;]*\bgetResumeUrls\b[^;]*from\s+['"]windmill-client['"]"""
    assert re.search(pattern, content), (
        "Expected 'getResumeUrls' to be imported from 'windmill-client', "
        "but the import statement was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 4. `waitForApproval` imported from windmill-client
# ---------------------------------------------------------------------------

def test_wait_for_approval_imported_from_windmill_client():
    """`waitForApproval` must be imported from 'windmill-client'."""
    content = _read_file()
    pattern = r"""import\s+[^;]*\bwaitForApproval\b[^;]*from\s+['"]windmill-client['"]"""
    assert re.search(pattern, content), (
        "Expected 'waitForApproval' to be imported from 'windmill-client', "
        "but the import statement was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 5. `parallel` imported from windmill-client
# ---------------------------------------------------------------------------

def test_parallel_imported_from_windmill_client():
    """`parallel` must be imported from 'windmill-client'."""
    content = _read_file()
    pattern = r"""import\s+[^;]*\bparallel\b[^;]*from\s+['"]windmill-client['"]"""
    assert re.search(pattern, content), (
        "Expected 'parallel' to be imported from 'windmill-client', "
        "but the import statement was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 6. step('run_id') wrapping crypto.randomUUID()
# ---------------------------------------------------------------------------

def test_step_run_id_with_crypto_random_uuid():
    """`step('run_id', ...)` and `crypto.randomUUID()` must both be present."""
    content = _read_file()

    step_pattern = r"""await\s+step\s*\(\s*['"]run_id['"]"""
    uuid_pattern = r"""crypto\.randomUUID\s*\(\s*\)"""

    assert re.search(step_pattern, content), (
        "Expected `await step('run_id', ...)` in the file, but it was not found.\n\n"
        f"File content:\n{content}"
    )
    assert re.search(uuid_pattern, content), (
        "Expected `crypto.randomUUID()` in the file, but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 7. `parallel(` appears at least twice
# ---------------------------------------------------------------------------

def test_parallel_called_at_least_twice():
    """`parallel(` must appear at least twice (extraction + transformation)."""
    content = _read_file()
    occurrences = len(re.findall(r"\bparallel\s*\(", content))
    assert occurrences >= 2, (
        f"Expected `parallel(` to appear at least 2 times in the file, "
        f"but found {occurrences} occurrence(s).\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 8. getResumeUrls() called inside a step()
# ---------------------------------------------------------------------------

def test_get_resume_urls_inside_step():
    """`await step(` and `getResumeUrls()` must both be present."""
    content = _read_file()

    step_await_pattern = r"await\s+step\s*\("
    resume_urls_pattern = r"getResumeUrls\s*\(\s*\)"

    assert re.search(step_await_pattern, content), (
        "Expected `await step(` to be present in the file, but it was not found.\n\n"
        f"File content:\n{content}"
    )
    assert re.search(resume_urls_pattern, content), (
        "Expected `getResumeUrls()` to be present in the file, but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 9. waitForApproval({ timeout: 3600 }) present
# ---------------------------------------------------------------------------

def test_wait_for_approval_with_timeout_3600():
    """`waitForApproval({ timeout: 3600 })` must be present and awaited."""
    content = _read_file()
    pattern = r"await\s+waitForApproval\s*\(\s*\{\s*timeout\s*:\s*3600\s*\}\s*\)"
    assert re.search(pattern, content), (
        "Expected `await waitForApproval({ timeout: 3600 })` in the file, "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 10. Rejection branch returns status: 'rejected'
# ---------------------------------------------------------------------------

def test_rejected_status_in_rejection_branch():
    """The rejection branch must return an object containing `status: 'rejected'`."""
    content = _read_file()
    # Accept both single and double quotes
    pattern = r"""status\s*:\s*['"]rejected['"]"""
    assert re.search(pattern, content), (
        "Expected a return object with `status: 'rejected'` in the file, "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 11. task(loadData) called in the approval branch
# ---------------------------------------------------------------------------

def test_task_load_data_called_in_approval_branch():
    """`task(loadData)` must be present for the approval branch load step."""
    content = _read_file()
    pattern = r"task\s*\(\s*loadData\s*\)"
    assert re.search(pattern, content), (
        "Expected `task(loadData)` to be present in the file, "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 12. try/catch present in extractEndpoint (error handling)
# ---------------------------------------------------------------------------

def test_try_catch_present_for_error_handling():
    """`try` and `catch` must both be present for extractEndpoint error handling."""
    content = _read_file()

    assert re.search(r"\btry\b", content), (
        "Expected a `try` block in the file (for extractEndpoint error handling), "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )
    assert re.search(r"\bcatch\b", content), (
        "Expected a `catch` block in the file (for extractEndpoint error handling), "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )
