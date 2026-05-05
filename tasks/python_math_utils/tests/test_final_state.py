import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
DESCRIBE_PY = os.path.join(SCRIPTS_DIR, "describe.py")
DESCRIBE_YAML = os.path.join(SCRIPTS_DIR, "describe.script.yaml")


def test_describe_py_exists():
    assert os.path.isfile(DESCRIBE_PY), f"Expected '{DESCRIBE_PY}' but not found."


def test_describe_yaml_exists():
    assert os.path.isfile(DESCRIBE_YAML), f"Expected '{DESCRIBE_YAML}' but not found."


def _run_main(values: list) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('desc', '{DESCRIBE_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({json.dumps(values)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def _run_expect_error(values: list) -> str:
    script = (
        f"import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('desc', '{DESCRIBE_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"try:\n"
        f"    mod.main({json.dumps(values)})\n"
        f"    print('NO_ERROR')\n"
        f"except ValueError as e:\n"
        f"    print(str(e))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def test_odd_length_list():
    """Priority 1: median of [1,2,3,4,5] is 3."""
    r = _run_main([1, 2, 3, 4, 5])
    assert r["count"] == 5
    assert r["min"] == 1.0
    assert r["max"] == 5.0
    assert r["mean"] == 3.0
    assert r["median"] == 3.0
    assert r["range"] == 4.0


def test_even_length_list():
    """Priority 1: median of [1,3] is 2.0 (average of two middles)."""
    r = _run_main([1, 3])
    assert r["median"] == 2.0, f"Expected median=2.0, got {r['median']}"


def test_empty_list_raises():
    """Priority 1: empty list raises ValueError."""
    msg = _run_expect_error([])
    assert msg != "NO_ERROR", "Expected ValueError for empty list, got none."


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
    assert _parse_simple_yaml(DESCRIBE_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(DESCRIBE_YAML).get("summary") == "Compute descriptive statistics for a list of numbers"
