"""
Initial state tests for deployment_pipeline_with_rollback task.

Verifies that the environment is correctly set up BEFORE the agent runs:
- wmill binary is available in PATH and executable
- /home/user/windmill-project directory exists
- /home/user/windmill-project/f/workflows directory exists
- /home/user/windmill-project/f/workflows/deploy_with_rollback.ts does NOT exist
"""

import os
import shutil
import subprocess


def test_wmill_binary_in_path():
    """wmill CLI binary must be available in PATH."""
    binary = shutil.which("wmill")
    assert binary is not None, (
        "wmill binary not found in PATH. "
        "Ensure the windmill npm package is installed globally."
    )


def test_wmill_binary_executable():
    """wmill binary must be executable and return a version string."""
    result = subprocess.run(
        ["wmill", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"wmill --version failed with return code {result.returncode}. "
        f"stderr: {result.stderr.strip()}"
    )


def test_windmill_project_directory_exists():
    """The /home/user/windmill-project directory must exist."""
    project_dir = "/home/user/windmill-project"
    assert os.path.isdir(project_dir), (
        f"Expected project directory '{project_dir}' to exist, but it does not."
    )


def test_workflows_directory_exists():
    """The /home/user/windmill-project/f/workflows directory must exist."""
    workflows_dir = "/home/user/windmill-project/f/workflows"
    assert os.path.isdir(workflows_dir), (
        f"Expected workflows directory '{workflows_dir}' to exist, but it does not."
    )


def test_deploy_with_rollback_file_does_not_exist():
    """deploy_with_rollback.ts must NOT exist before the task runs."""
    target_file = "/home/user/windmill-project/f/workflows/deploy_with_rollback.ts"
    assert not os.path.exists(target_file), (
        f"Expected '{target_file}' to NOT exist in the initial state, "
        "but it was found. The environment setup may be incorrect."
    )
