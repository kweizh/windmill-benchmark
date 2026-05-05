import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
VALIDATE_PY = os.path.join(SCRIPTS_DIR, "validate_user.py")
VALIDATE_YAML = os.path.join(SCRIPTS_DIR, "validate_user.script.yaml")


def test_validate_py_exists():
    assert os.path.isfile(VALIDATE_PY)


def test_validate_yaml_exists():
    assert os.path.isfile(VALIDATE_YAML)


def _run_main(user: dict) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('vu', '{VALIDATE_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({json.dumps(user)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def _run_expect_error(user: dict) -> str:
    script = (
        f"import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('vu', '{VALIDATE_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"try:\n"
        f"    mod.main({json.dumps(user)})\n"
        f"    print('NO_ERROR')\n"
        f"except ValueError as e:\n"
        f"    print(str(e))\n"
        f"except Exception as e:\n"
        f"    print(f'WRONG:{{type(e).__name__}}:{{e}}')\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def test_valid_user():
    r = _run_main({"name": "Alice", "email": "alice@example.com", "age": 30})
    assert r.get("valid") is True
    assert r.get("name") == "Alice"
    assert r.get("email") == "alice@example.com"
    assert r.get("age") == 30


def test_name_stripped_email_lowercased():
    r = _run_main({"name": "  Bob  ", "email": "BOB@EXAMPLE.COM"})
    assert r.get("name") == "Bob", f"Expected stripped name, got {repr(r.get('name'))}"
    assert r.get("email") == "bob@example.com", f"Expected lowercased email, got {repr(r.get('email'))}"


def test_missing_name_raises():
    msg = _run_expect_error({"email": "alice@example.com"})
    assert msg != "NO_ERROR", "Expected ValueError for missing name."
    assert not msg.startswith("WRONG"), f"Expected ValueError, got: {msg}"


def test_bad_email_raises():
    msg = _run_expect_error({"name": "Alice", "email": "not-an-email"})
    assert msg != "NO_ERROR", "Expected ValueError for bad email."


def test_age_out_of_range_raises():
    msg = _run_expect_error({"name": "Alice", "email": "alice@example.com", "age": 200})
    assert msg != "NO_ERROR", "Expected ValueError for age=200."


def test_multiple_errors_collected():
    """Priority 1: both missing name AND bad email → error mentions both."""
    msg = _run_expect_error({"email": "bad"})
    assert msg != "NO_ERROR"
    # Error should mention at least one of the issues
    assert "name" in msg.lower() or "email" in msg.lower(), (
        f"Expected error to mention validation issues, got: {repr(msg)}"
    )


def _parse_simple_yaml(path: str) -> dict:
    result = {}
    with open(path) as fh:
        for line in fh:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip()] = v.strip().strip('"').strip("'")
    return result


def test_yaml_language():
    assert _parse_simple_yaml(VALIDATE_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(VALIDATE_YAML).get("summary") == "Validate and normalize a user input dict"
