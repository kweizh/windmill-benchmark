import re
from pathlib import Path

REMINDER_FILE = Path("/home/user/windmill-project/f/workflows/reminder.ts")


def test_reminder_file_exists():
    """The reminder workflow file must still exist after the fix."""
    assert REMINDER_FILE.exists(), f"reminder.ts not found at: {REMINDER_FILE}"
    assert REMINDER_FILE.is_file(), f"Expected a file at: {REMINDER_FILE}"


def test_sleep_imported_from_windmill_client():
    """The file must import `sleep` from 'windmill-client'."""
    content = REMINDER_FILE.read_text()
    # Match: import { ..., sleep, ... } from 'windmill-client'
    pattern = r"""import\s*\{[^}]*\bsleep\b[^}]*\}\s*from\s*['"]windmill-client['"]"""
    assert re.search(pattern, content), (
        "Expected 'sleep' to be imported from 'windmill-client', but the import was not found. "
        f"File content:\n{content}"
    )


def test_await_sleep_delay_seconds_present():
    """The file must call `await sleep(delay_seconds)` for the delay logic."""
    content = REMINDER_FILE.read_text()
    # Accept await sleep(delay_seconds) with optional whitespace variations
    pattern = r"await\s+sleep\s*\(\s*delay_seconds\s*\)"
    assert re.search(pattern, content), (
        "Expected 'await sleep(delay_seconds)' in reminder.ts, but it was not found. "
        f"File content:\n{content}"
    )


def test_settimeout_not_present():
    """The broken setTimeout pattern must be fully removed."""
    content = REMINDER_FILE.read_text()
    assert "setTimeout" not in content, (
        "Found 'setTimeout' in reminder.ts — the broken delay pattern must be removed entirely. "
        f"File content:\n{content}"
    )
