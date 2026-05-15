"""
Initial state verification for workflow_concurrent_batched_enrichment.

Checks that the environment is correctly set up BEFORE the agent attempts the task:
  - wmill CLI is available in PATH
  - /home/user/windmill-project directory exists
  - /home/user/windmill-project/f/workflows/batch_enricher.ts does NOT exist
"""

import os
import shutil
import subprocess


def test_wmill_in_path():
    """wmill CLI must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill CLI not found in PATH. "
        "Install it with: npm install -g windmill-cli"
    )


def test_windmill_project_exists():
    """The windmill project directory must exist."""
    project_dir = "/home/user/windmill-project"
    assert os.path.isdir(project_dir), (
        f"Expected directory '{project_dir}' to exist, but it does not. "
        "The Dockerfile should create this directory."
    )


def test_workflows_dir_exists():
    """The f/workflows directory inside the project must exist."""
    workflows_dir = "/home/user/windmill-project/f/workflows"
    assert os.path.isdir(workflows_dir), (
        f"Expected directory '{workflows_dir}' to exist, but it does not. "
        "The Dockerfile should create this directory."
    )


def test_batch_enricher_does_not_exist():
    """batch_enricher.ts must NOT exist before the agent runs."""
    target_file = "/home/user/windmill-project/f/workflows/batch_enricher.ts"
    assert not os.path.exists(target_file), (
        f"File '{target_file}' already exists before the task started. "
        "The agent should create this file; it must not be pre-populated."
    )


def test_wmill_version():
    """wmill CLI must be executable and report a version."""
    result = subprocess.run(
        ["wmill", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, (
        f"'wmill --version' exited with code {result.returncode}. "
        f"stderr: {result.stderr.strip()}"
    )
    output = (result.stdout + result.stderr).strip()
    assert output, "wmill --version produced no output."
