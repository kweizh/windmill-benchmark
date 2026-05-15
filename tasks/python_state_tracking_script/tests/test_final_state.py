import os
import sys
import ast
import importlib
import importlib.util
import types
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
SCRIPT_PATH = os.path.join(SCRIPTS_DIR, "execution_counter.py")
YAML_PATH = os.path.join(SCRIPTS_DIR, "execution_counter.script.yaml")


# ---------------------------------------------------------------------------
# Priority 3: File / State checks (no CLI can verify local file correctness)
# ---------------------------------------------------------------------------

def test_script_file_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"execution_counter.py not found at '{SCRIPT_PATH}'. "
        "The file must be created as part of the task."
    )


def test_script_imports_get_state_and_set_state():
    with open(SCRIPT_PATH) as f:
        source = f.read()
    assert "from wmill import" in source and "get_state" in source and "set_state" in source, (
        "execution_counter.py must contain 'from wmill import get_state, set_state'. "
        f"File content:\n{source}"
    )


def test_script_defines_main_function():
    with open(SCRIPT_PATH) as f:
        source = f.read()
    assert "def main(" in source or "def main():" in source, (
        "execution_counter.py must define a 'main()' function. "
        f"File content:\n{source}"
    )


def test_script_calls_get_state():
    with open(SCRIPT_PATH) as f:
        source = f.read()
    assert "get_state()" in source, (
        "execution_counter.py must call 'get_state()' to retrieve the current count. "
        f"File content:\n{source}"
    )


def test_script_calls_set_state():
    with open(SCRIPT_PATH) as f:
        source = f.read()
    assert "set_state(" in source, (
        "execution_counter.py must call 'set_state(...)' to persist the new count. "
        f"File content:\n{source}"
    )


def test_script_returns_correct_structure_on_first_run():
    """
    Load execution_counter.py with a mocked wmill module so that get_state()
    returns None (simulating first run) and set_state() is a no-op.
    Then call main() and assert the returned dict has the correct keys and values.
    """
    # Build a lightweight mock for the wmill module
    mock_wmill = types.ModuleType("wmill")
    mock_wmill.get_state = lambda: None
    mock_wmill.set_state = lambda v: None

    # Insert mock into sys.modules before importing the script
    sys.modules["wmill"] = mock_wmill

    try:
        spec = importlib.util.spec_from_file_location("execution_counter", SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.main()
    finally:
        # Clean up: remove the mock so it does not affect other tests
        sys.modules.pop("wmill", None)
        sys.modules.pop("execution_counter", None)

    assert isinstance(result, dict), (
        f"main() must return a dict, got {type(result).__name__}: {result}"
    )
    assert "count" in result, (
        f"Returned dict must contain the key 'count'. Got keys: {list(result.keys())}"
    )
    assert "message" in result, (
        f"Returned dict must contain the key 'message'. Got keys: {list(result.keys())}"
    )
    assert result["count"] == 1, (
        f"On first run (state=None), 'count' must be 1. Got: {result['count']}"
    )
    assert "time(s)" in result["message"], (
        f"'message' must contain the phrase 'time(s)'. Got: {result['message']}"
    )
    assert "1" in result["message"], (
        f"'message' must reference the count value '1'. Got: {result['message']}"
    )


def test_companion_yaml_exists():
    assert os.path.isfile(YAML_PATH), (
        f"Companion metadata file not found at '{YAML_PATH}'. "
        "Create 'execution_counter.script.yaml' alongside the Python script."
    )


def test_companion_yaml_contains_python3_language():
    with open(YAML_PATH) as f:
        content = f.read()
    assert "language: python3" in content, (
        "execution_counter.script.yaml must contain 'language: python3'. "
        f"File content:\n{content}"
    )
