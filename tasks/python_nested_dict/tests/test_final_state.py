import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLATTEN_PY = os.path.join(SCRIPTS_DIR, "flatten_config.py")
FLATTEN_YAML = os.path.join(SCRIPTS_DIR, "flatten_config.script.yaml")


def test_flatten_py_exists():
    assert os.path.isfile(FLATTEN_PY)


def test_flatten_yaml_exists():
    assert os.path.isfile(FLATTEN_YAML)


def _run_main(config: dict, prefix: str = "") -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('fc', '{FLATTEN_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({json.dumps(config)}, {repr(prefix)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_nested_two_levels():
    """Priority 1: {a:{b:1,c:{d:2}}} → {a.b:1, a.c.d:2}"""
    r = _run_main({"a": {"b": 1, "c": {"d": 2}}})
    assert r.get("a.b") == 1, f"Expected a.b=1, got {r}"
    assert r.get("a.c.d") == 2, f"Expected a.c.d=2, got {r}"
    assert "a" not in r or isinstance(r.get("a"), int), "Parent key 'a' should not exist as a key."


def test_with_prefix():
    """Priority 1: {x:1} with prefix='ns' → {'ns.x':1}"""
    r = _run_main({"x": 1}, prefix="ns")
    assert r.get("ns.x") == 1, f"Expected ns.x=1, got {r}"


def test_db_config():
    """Priority 1: {db:{host:'localhost',port:5432}} → flat dict."""
    r = _run_main({"db": {"host": "localhost", "port": 5432}})
    assert r.get("db.host") == "localhost", f"Expected db.host='localhost', got {r}"
    assert r.get("db.port") == 5432, f"Expected db.port=5432, got {r}"


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
    assert _parse_simple_yaml(FLATTEN_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(FLATTEN_YAML).get("summary") == "Flatten a nested dictionary into dot-notation keys"
