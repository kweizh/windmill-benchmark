"""
Final state tests for deployment_pipeline_with_rollback task.

Priority 3 — File content checks.

Verifies that the agent correctly created
/home/user/windmill-project/f/workflows/deploy_with_rollback.ts
with all required elements of the Windmill deployment pipeline with rollback workflow.
"""

import os
import re

TARGET_FILE = "/home/user/windmill-project/f/workflows/deploy_with_rollback.ts"


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
# 2. step and waitForApproval imported from windmill-client
# ---------------------------------------------------------------------------

def test_step_and_wait_for_approval_imported():
    """Both `step` and `waitForApproval` must be imported from 'windmill-client'."""
    content = _read_file()
    import_pattern = r"import\s*\{[^}]*\}\s*from\s*['\"]windmill-client['\"]"
    match = re.search(import_pattern, content)
    assert match is not None, (
        "Expected an import statement from 'windmill-client', but none was found.\n\n"
        f"File content:\n{content}"
    )
    import_block = match.group(0)
    assert "step" in import_block, (
        "Expected `step` to be imported from 'windmill-client', "
        f"but it was not found in the import statement: {import_block}\n\n"
        f"File content:\n{content}"
    )
    assert "waitForApproval" in import_block, (
        "Expected `waitForApproval` to be imported from 'windmill-client', "
        f"but it was not found in the import statement: {import_block}\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 3. await step('deploy_id', ...) present
# ---------------------------------------------------------------------------

def test_step_deploy_id_present():
    """The workflow must use await step('deploy_id', ...) to capture the deploy ID."""
    content = _read_file()
    pattern = r"await\s+step\s*\(\s*['\"]deploy_id['\"]\s*,"
    assert re.search(pattern, content), (
        "Expected `await step('deploy_id', ...)` to be present in the file, "
        "but it was not found. The deploy ID must be captured deterministically "
        "using step().\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 4. crypto.randomUUID() present
# ---------------------------------------------------------------------------

def test_crypto_random_uuid_present():
    """crypto.randomUUID() must be used to generate the deploy ID."""
    content = _read_file()
    pattern = r"crypto\.randomUUID\s*\(\s*\)"
    assert re.search(pattern, content), (
        "Expected `crypto.randomUUID()` to be present in the file, "
        "but it was not found. The deploy ID must be generated with "
        "crypto.randomUUID() inside the step() callback.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 5. task(runTests) present
# ---------------------------------------------------------------------------

def test_task_run_tests_present():
    """task(runTests) must be called to run tests before deployment."""
    content = _read_file()
    pattern = r"task\s*\(\s*runTests\s*\)"
    assert re.search(pattern, content), (
        "Expected `task(runTests)` to be present in the file, "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 6. task(deployToStaging) present
# ---------------------------------------------------------------------------

def test_task_deploy_to_staging_present():
    """task(deployToStaging) must be called to deploy to the staging environment."""
    content = _read_file()
    pattern = r"task\s*\(\s*deployToStaging\s*\)"
    assert re.search(pattern, content), (
        "Expected `task(deployToStaging)` to be present in the file, "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 7. task(rollbackStaging) present (must be in a catch block or after rejection)
# ---------------------------------------------------------------------------

def test_task_rollback_staging_present():
    """task(rollbackStaging) must be called in rollback scenarios."""
    content = _read_file()
    pattern = r"task\s*\(\s*rollbackStaging\s*\)"
    assert re.search(pattern, content), (
        "Expected `task(rollbackStaging)` to be present in the file, "
        "but it was not found. rollbackStaging must be called in the staging "
        "catch block and/or on approval rejection.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 8. waitForApproval({ timeout: 7200 }) present
# ---------------------------------------------------------------------------

def test_wait_for_approval_with_timeout_7200():
    """waitForApproval must be called with { timeout: 7200 }."""
    content = _read_file()
    pattern = r"await\s+waitForApproval\s*\(\s*\{\s*timeout\s*:\s*7200\s*\}\s*\)"
    assert re.search(pattern, content), (
        "Expected `await waitForApproval({ timeout: 7200 })` in the file, "
        "but it was not found. The approval gate timeout must be set to 7200.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 9. task(deployToProduction) present
# ---------------------------------------------------------------------------

def test_task_deploy_to_production_present():
    """task(deployToProduction) must be called to deploy to the production environment."""
    content = _read_file()
    pattern = r"task\s*\(\s*deployToProduction\s*\)"
    assert re.search(pattern, content), (
        "Expected `task(deployToProduction)` to be present in the file, "
        "but it was not found.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 10. task(rollbackProduction) present (must be in a catch block)
# ---------------------------------------------------------------------------

def test_task_rollback_production_present():
    """task(rollbackProduction) must be called in the production error catch block."""
    content = _read_file()
    pattern = r"task\s*\(\s*rollbackProduction\s*\)"
    assert re.search(pattern, content), (
        "Expected `task(rollbackProduction)` to be present in the file, "
        "but it was not found. rollbackProduction must be called in the production "
        "deployment catch block.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 11. At least 2 try { blocks present (for staging and production)
# ---------------------------------------------------------------------------

def test_at_least_two_try_blocks_present():
    """At least 2 try { blocks must be present — one for staging, one for production."""
    content = _read_file()
    # Match both `try {` and `try{` (with or without a space)
    matches = re.findall(r"\btry\s*\{", content)
    assert len(matches) >= 2, (
        f"Expected at least 2 `try {{` blocks in the file (one for staging, one for "
        f"production), but found {len(matches)}.\n\n"
        f"File content:\n{content}"
    )


# ---------------------------------------------------------------------------
# 12. workflow( present
# ---------------------------------------------------------------------------

def test_workflow_call_present():
    """The main export must be wrapped with workflow()."""
    content = _read_file()
    pattern = r"workflow\s*\("
    assert re.search(pattern, content), (
        "Expected `workflow(` to be present in the file. "
        "The main export must be defined using the workflow() wrapper from "
        "windmill-client.\n\n"
        f"File content:\n{content}"
    )
