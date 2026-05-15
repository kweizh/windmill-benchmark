import os
import pytest

SCRIPT_PATH = "/home/user/windmill-project/f/monitoring/heartbeat.py"


def _read_script() -> str:
    with open(SCRIPT_PATH) as f:
        return f.read()


def test_script_imports_get_state_and_set_state():
    """The fixed script must import both get_state and set_state from wmill."""
    content = _read_script()
    assert "get_state" in content, \
        "heartbeat.py does not import or use get_state — the wmill state import is missing."
    assert "set_state" in content, \
        "heartbeat.py does not import or use set_state — the wmill state import is missing."
    # Verify the import comes from the wmill package
    assert "from wmill import" in content or "import wmill" in content, \
        "heartbeat.py does not contain a 'from wmill import ...' or 'import wmill' statement."


def test_script_calls_get_state():
    """The fixed script must call get_state() to load the persistent count."""
    content = _read_script()
    assert "get_state()" in content, \
        "heartbeat.py does not call get_state() — the persistent count load is missing."


def test_script_calls_set_state():
    """The fixed script must call set_state(...) to persist the updated count."""
    content = _read_script()
    assert "set_state(" in content, \
        "heartbeat.py does not call set_state(...) — the persistent count save is missing."


def test_broken_reset_pattern_removed():
    """The bare 'count = 0' reset line must no longer be the sole initialisation of the counter."""
    content = _read_script()
    lines = [line.strip() for line in content.splitlines()]
    # The exact broken pattern is a standalone assignment: count = 0
    # After the fix, the counter must be loaded via get_state(), not hardcoded to 0.
    bare_reset_lines = [l for l in lines if l == "count = 0"]
    assert len(bare_reset_lines) == 0, \
        "heartbeat.py still contains 'count = 0' as a bare reset line — the bug has not been fixed."


def test_return_dict_keys_preserved():
    """The return statement must still include count, timestamp, and message keys."""
    content = _read_script()
    assert '"count"' in content or "'count'" in content, \
        "heartbeat.py return value is missing the 'count' key."
    assert '"timestamp"' in content or "'timestamp'" in content, \
        "heartbeat.py return value is missing the 'timestamp' key."
    assert '"message"' in content or "'message'" in content, \
        "heartbeat.py return value is missing the 'message' key."


def test_import_time_preserved():
    """The 'import time' statement must still be present (used for timestamp)."""
    content = _read_script()
    assert "import time" in content, \
        "heartbeat.py is missing 'import time' — this statement must not be removed."
