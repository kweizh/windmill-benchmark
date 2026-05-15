"""
Tests for the initial state of the workflow_get_resume_urls_notify task.

Verifies that the environment is properly bootstrapped:
- wmill CLI is available in PATH
- The windmill project directory exists
- The approval_notifier.ts file exists in the expected location
- The file is in its broken initial state (missing getResumeUrls and step usage)
- The file still contains waitForApproval with the expected timeout
"""

import os
import shutil
import subprocess

TARGET_FILE = "/home/user/windmill-project/f/workflows/approval_notifier.ts"


def test_wmill_in_path():
    """wmill CLI must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill CLI not found in PATH. Ensure the windmill-cli npm package is installed."
    )


def test_project_directory_exists():
    """The windmill project directory must exist."""
    assert os.path.isdir("/home/user/windmill-project"), (
        "Project directory /home/user/windmill-project does not exist."
    )


def test_target_file_exists():
    """The approval_notifier.ts file must exist at the expected path."""
    assert os.path.isfile(TARGET_FILE), (
        f"Target file {TARGET_FILE} does not exist."
    )


def test_file_does_not_contain_get_resume_urls():
    """The file must NOT import or call getResumeUrls (broken initial state)."""
    with open(TARGET_FILE, "r") as f:
        content = f.read()
    assert "getResumeUrls" not in content, (
        "File already contains 'getResumeUrls'. The initial state should be broken "
        "(missing getResumeUrls import and call)."
    )


def test_file_does_not_contain_step_calls():
    """The file must NOT contain step() calls (broken initial state)."""
    with open(TARGET_FILE, "r") as f:
        content = f.read()
    assert "step(" not in content, (
        "File already contains 'step(' calls. The initial state should be broken "
        "(no step wrappers present)."
    )


def test_file_contains_wait_for_approval():
    """The file must contain waitForApproval({ timeout: 7200 }) (initial state preserved)."""
    with open(TARGET_FILE, "r") as f:
        content = f.read()
    assert "waitForApproval({ timeout: 7200 })" in content, (
        "File does not contain 'waitForApproval({ timeout: 7200 })'. "
        "The initial state is unexpected."
    )


def test_file_contains_wait_for_approval_import():
    """The file must import waitForApproval from windmill-client."""
    with open(TARGET_FILE, "r") as f:
        content = f.read()
    assert "waitForApproval" in content and "windmill-client" in content, (
        "File does not import waitForApproval from windmill-client."
    )
