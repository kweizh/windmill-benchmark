import os
import shutil
from pathlib import Path

PROJECT_DIR = Path("/home/user/windmill-project")
REMINDER_FILE = PROJECT_DIR / "f" / "workflows" / "reminder.ts"


def test_wmill_binary_in_path():
    """wmill CLI must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. Install via: npm install -g windmill-cli"
    )


def test_project_directory_exists():
    """The Windmill project directory must exist."""
    assert PROJECT_DIR.exists(), f"Project directory not found: {PROJECT_DIR}"
    assert PROJECT_DIR.is_dir(), f"Expected a directory at: {PROJECT_DIR}"


def test_reminder_file_exists():
    """The reminder workflow file must exist at the expected path."""
    assert REMINDER_FILE.exists(), f"reminder.ts not found at: {REMINDER_FILE}"
    assert REMINDER_FILE.is_file(), f"Expected a file at: {REMINDER_FILE}"


def test_reminder_file_contains_settimeout():
    """The file must contain the broken setTimeout pattern (initial broken state)."""
    content = REMINDER_FILE.read_text()
    assert "setTimeout" in content, (
        "Expected to find 'setTimeout' in reminder.ts to confirm the broken initial state, "
        "but it was not present."
    )
