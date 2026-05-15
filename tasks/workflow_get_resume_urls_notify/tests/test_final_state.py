"""
Tests for the final state of the workflow_get_resume_urls_notify task.

Verifies that the agent has correctly fixed the approval_notifier.ts workflow by:
1. Ensuring the file exists
2. Verifying getResumeUrls is imported from windmill-client
3. Verifying step is imported from windmill-client
4. Confirming the step('approval_urls', () => getResumeUrls()) pattern is present
5. Confirming urls.approvalPage is referenced for notification
6. Confirming waitForApproval({ timeout: 7200 }) is still present and unchanged
7. Confirming task(deploy) is still present (rest of workflow intact)
8. Confirming getResumeUrls call appears BEFORE waitForApproval in source order
"""

import os
import re

TARGET_FILE = "/home/user/windmill-project/f/workflows/approval_notifier.ts"


def _read_file() -> str:
    with open(TARGET_FILE, "r") as f:
        return f.read()


def test_file_exists():
    """The approval_notifier.ts file must exist."""
    assert os.path.isfile(TARGET_FILE), (
        f"Target file {TARGET_FILE} does not exist."
    )


def test_get_resume_urls_imported():
    """getResumeUrls must be imported from windmill-client."""
    content = _read_file()
    # Check that getResumeUrls appears in an import statement from windmill-client
    import_pattern = re.compile(
        r"import\s*\{[^}]*getResumeUrls[^}]*\}\s*from\s*['\"]windmill-client['\"]",
        re.MULTILINE,
    )
    assert import_pattern.search(content) is not None, (
        "'getResumeUrls' is not imported from 'windmill-client'. "
        "Add getResumeUrls to the import statement."
    )


def test_step_imported():
    """step must be imported from windmill-client."""
    content = _read_file()
    import_pattern = re.compile(
        r"import\s*\{[^}]*\bstep\b[^}]*\}\s*from\s*['\"]windmill-client['\"]",
        re.MULTILINE,
    )
    assert import_pattern.search(content) is not None, (
        "'step' is not imported from 'windmill-client'. "
        "Add step to the import statement."
    )


def test_step_approval_urls_pattern_present():
    """The step('approval_urls', () => getResumeUrls()) pattern must be present."""
    content = _read_file()
    # Allow for whitespace variations but require the key 'approval_urls' and getResumeUrls()
    pattern = re.compile(
        r"step\s*\(\s*['\"]approval_urls['\"]\s*,\s*\(\s*\)\s*=>\s*getResumeUrls\s*\(\s*\)\s*\)",
        re.MULTILINE,
    )
    assert pattern.search(content) is not None, (
        "Pattern `step('approval_urls', () => getResumeUrls())` not found. "
        "Ensure getResumeUrls() is wrapped in a step() with key 'approval_urls'."
    )


def test_urls_approval_page_referenced():
    """urls.approvalPage must be referenced in the file (notification step)."""
    content = _read_file()
    assert "urls.approvalPage" in content, (
        "'urls.approvalPage' is not referenced in the file. "
        "The log_approval_url step must log the approval page URL."
    )


def test_log_approval_url_step_present():
    """A step with key 'log_approval_url' must be present."""
    content = _read_file()
    assert "'log_approval_url'" in content or '"log_approval_url"' in content, (
        "Step key 'log_approval_url' not found. "
        "Add a step('log_approval_url', ...) that logs the approval URL."
    )


def test_wait_for_approval_unchanged():
    """waitForApproval({ timeout: 7200 }) must still be present and unchanged."""
    content = _read_file()
    assert "waitForApproval({ timeout: 7200 })" in content, (
        "'waitForApproval({ timeout: 7200 })' not found or was modified. "
        "The waitForApproval call must remain unchanged."
    )


def test_task_deploy_intact():
    """task(deploy) must still be present (rest of workflow must be intact)."""
    content = _read_file()
    assert "task(deploy)" in content, (
        "'task(deploy)' not found in the file. "
        "The rest of the workflow must remain intact."
    )


def test_get_resume_urls_before_wait_for_approval():
    """getResumeUrls call must appear BEFORE waitForApproval in source order."""
    content = _read_file()

    # Find position of the step('approval_urls', ...) call containing getResumeUrls
    get_resume_match = re.search(
        r"step\s*\(\s*['\"]approval_urls['\"]",
        content,
    )
    wait_for_approval_match = re.search(
        r"waitForApproval\s*\(",
        content,
    )

    assert get_resume_match is not None, (
        "step('approval_urls', ...) not found in the file."
    )
    assert wait_for_approval_match is not None, (
        "waitForApproval() not found in the file."
    )

    get_resume_pos = get_resume_match.start()
    wait_for_approval_pos = wait_for_approval_match.start()

    assert get_resume_pos < wait_for_approval_pos, (
        f"getResumeUrls (via step 'approval_urls') appears at position {get_resume_pos} "
        f"but waitForApproval appears at position {wait_for_approval_pos}. "
        "getResumeUrls must be called BEFORE waitForApproval."
    )
