import os
import shutil
from pathlib import Path

PROJECT_DIR = Path("/home/user/windmill-project")
WORKFLOWS_DIR = PROJECT_DIR / "f" / "workflows"
API_CALLER_FILE = WORKFLOWS_DIR / "api_caller.ts"


def test_wmill_binary_in_path():
    """wmill CLI must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. Install via: npm install -g windmill-cli"
    )


def test_project_directory_exists():
    """The Windmill project directory must exist."""
    assert PROJECT_DIR.exists(), f"Project directory not found: {PROJECT_DIR}"
    assert PROJECT_DIR.is_dir(), f"Expected a directory at: {PROJECT_DIR}"


def test_api_caller_file_does_not_exist():
    """The api_caller.ts file must NOT exist before the task is performed."""
    assert not API_CALLER_FILE.exists(), (
        f"api_caller.ts already exists at {API_CALLER_FILE} — "
        "the initial state requires this file to be absent so the agent creates it."
    )
