"""
Final state tests: verify the agent has correctly fixed health_monitor.py
to use Windmill persistent state and only alert on status changes.
"""

import os


SCRIPT_PATH = "/home/user/windmill-project/f/scripts/health_monitor.py"


def _read_script() -> str:
    assert os.path.isfile(SCRIPT_PATH), (
        f"Script file not found at {SCRIPT_PATH}"
    )
    with open(SCRIPT_PATH, "r") as f:
        return f.read()


def _read_lines() -> list[str]:
    assert os.path.isfile(SCRIPT_PATH), (
        f"Script file not found at {SCRIPT_PATH}"
    )
    with open(SCRIPT_PATH, "r") as f:
        return f.readlines()


# ── Test 1: file exists ───────────────────────────────────────────────────────

def test_script_file_exists():
    """The health_monitor.py file must still exist after the agent's edit."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Script file missing at {SCRIPT_PATH}"
    )


# ── Test 2: get_state imported from wmill ────────────────────────────────────

def test_get_state_imported():
    """get_state must be imported from the wmill package."""
    content = _read_script()
    assert "get_state" in content, (
        "get_state is not present in the file. "
        "Expected: 'from wmill import get_state, set_state' (or similar)."
    )
    # Confirm it's actually part of a wmill import, not just a string literal
    assert "from wmill import" in content or "import wmill" in content, (
        "wmill is not imported at all."
    )
    # Ensure get_state appears alongside the wmill import
    lines = _read_lines()
    import_lines = [l for l in lines if "wmill" in l and "import" in l]
    assert any("get_state" in l for l in import_lines), (
        "get_state is not imported from wmill. "
        f"wmill import lines found: {import_lines}"
    )


# ── Test 3: get_state() called in body ───────────────────────────────────────

def test_get_state_called():
    """get_state() must be called inside the main function."""
    content = _read_script()
    assert "get_state()" in content, (
        "get_state() is never called in the script. "
        "The agent must call get_state() to retrieve the previous status."
    )


# ── Test 4: set_state() still called ─────────────────────────────────────────

def test_set_state_called():
    """set_state() must still be called to persist the current status."""
    content = _read_script()
    assert "set_state(" in content, (
        "set_state() call is missing from the script. "
        "The agent must call set_state(current_status) to persist state."
    )


# ── Test 5: conditional guard present ────────────────────────────────────────

def test_status_change_condition_present():
    """The fix must include a condition checking for status change."""
    content = _read_script()
    assert "current_status != last_status" in content, (
        "Condition 'current_status != last_status' not found in the script. "
        "The agent must add an if-guard so alerts only fire on status changes."
    )


# ── Test 6: return dict contains 'changed' key ───────────────────────────────

def test_return_dict_has_changed_key():
    """The return value must include the 'changed' key."""
    content = _read_script()
    assert "'changed'" in content or '"changed"' in content, (
        "Return dict does not reference a 'changed' key. "
        "Expected: return {'status': ..., 'changed': ..., 'alerted': ...}"
    )


# ── Test 7: return dict contains 'alerted' key ───────────────────────────────

def test_return_dict_has_alerted_key():
    """The return value must include the 'alerted' key."""
    content = _read_script()
    assert "'alerted'" in content or '"alerted"' in content, (
        "Return dict does not reference an 'alerted' key. "
        "Expected: return {'status': ..., 'changed': ..., 'alerted': ...}"
    )


# ── Test 8: send_alert is inside a conditional block ────────────────────────

def test_send_alert_is_conditional():
    """
    send_alert() must only be called inside a conditional block.
    Verify by finding the line with send_alert( and ensuring that an 'if'
    statement precedes it at a lower or equal indentation level within
    the main function body.
    """
    lines = _read_lines()

    send_alert_line_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("send_alert("):
            send_alert_line_idx = i
            break

    assert send_alert_line_idx is not None, (
        "send_alert( call not found in the script."
    )

    # Walk backwards from send_alert line to find a preceding 'if' statement
    # that is at a shallower or equal indentation (i.e., it guards the call).
    send_alert_indent = len(lines[send_alert_line_idx]) - len(
        lines[send_alert_line_idx].lstrip()
    )

    found_if_guard = False
    for i in range(send_alert_line_idx - 1, -1, -1):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent < send_alert_indent and stripped.startswith("if "):
            found_if_guard = True
            break
        # Stop if we've left the function body (dedented past function def)
        if indent == 0 and not stripped.startswith("if "):
            break

    assert found_if_guard, (
        f"send_alert() on line {send_alert_line_idx + 1} does not appear to be "
        "inside a conditional (if) block. The alert must only fire when the "
        "status has changed: 'if current_status != last_status: send_alert(...)'"
    )
