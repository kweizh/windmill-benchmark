import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
PARSE_AGE_PY = os.path.join(SCRIPTS_DIR, "parse_age.py")
PARSE_AGE_YAML = os.path.join(SCRIPTS_DIR, "parse_age.script.yaml")


def test_parse_age_py_exists():
    assert os.path.isfile(PARSE_AGE_PY), f"Expected '{PARSE_AGE_PY}' but not found."


def test_parse_age_yaml_exists():
    assert os.path.isfile(PARSE_AGE_YAML), f"Expected '{PARSE_AGE_YAML}' but not found."


def _run_main(age_str: str) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('pa', '{PARSE_AGE_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({repr(age_str)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def _run_main_expect_error(age_str: str) -> str:
    script = (
        f"import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('pa', '{PARSE_AGE_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"try:\n"
        f"    mod.main({repr(age_str)})\n"
        f"    print('NO_ERROR')\n"
        f"except ValueError as e:\n"
        f"    print(str(e))\n"
        f"except Exception as e:\n"
        f"    print(f'WRONG_EXCEPTION:{{type(e).__name__}}:{{e}}')\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def test_adult_category():
    r = _run_main("25")
    assert r.get("age") == 25
    assert r.get("category") == "adult"


def test_minor_category():
    r = _run_main("10")
    assert r.get("age") == 10
    assert r.get("category") == "minor"


def test_senior_category():
    r = _run_main("70")
    assert r.get("age") == 70
    assert r.get("category") == "senior"


def test_invalid_string_raises_value_error():
    msg = _run_main_expect_error("abc")
    assert msg != "NO_ERROR", "Expected ValueError for non-integer input, got no error."
    assert not msg.startswith("WRONG_EXCEPTION"), f"Expected ValueError, got: {msg}"
    assert "not an integer" in msg.lower() or "invalid" in msg.lower(), (
        f"Expected error about 'not an integer', got: {repr(msg)}"
    )


def test_out_of_range_raises_value_error():
    msg = _run_main_expect_error("200")
    assert msg != "NO_ERROR", "Expected ValueError for age=200, got no error."
    assert not msg.startswith("WRONG_EXCEPTION"), f"Expected ValueError, got: {msg}"
    assert "range" in msg.lower() or "valid" in msg.lower(), (
        f"Expected error about valid range, got: {repr(msg)}"
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
    assert _parse_simple_yaml(PARSE_AGE_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(PARSE_AGE_YAML).get("summary") == "Parse and categorize an age string"
