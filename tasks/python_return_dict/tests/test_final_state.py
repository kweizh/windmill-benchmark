import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
STATS_PY = os.path.join(SCRIPTS_DIR, "stats.py")
STATS_YAML = os.path.join(SCRIPTS_DIR, "stats.script.yaml")


def test_stats_py_exists():
    assert os.path.isfile(STATS_PY), f"Expected '{STATS_PY}' but file not found."


def test_stats_yaml_exists():
    assert os.path.isfile(STATS_YAML), f"Expected '{STATS_YAML}' but file not found."


def _run_main(numbers: list) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('stats', '{STATS_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({json.dumps(numbers)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, (
        f"python3 failed (exit {result.returncode}): {result.stderr}"
    )
    return json.loads(result.stdout.strip())


def test_stats_normal_list():
    """Priority 1: main([1.0, 2.0, 3.0, 4.0]) returns correct stats."""
    r = _run_main([1.0, 2.0, 3.0, 4.0])
    assert r.get("count") == 4, f"Expected count=4, got {r.get('count')}"
    assert r.get("total") == 10.0, f"Expected total=10.0, got {r.get('total')}"
    assert r.get("average") == 2.5, f"Expected average=2.5, got {r.get('average')}"


def test_stats_empty_list():
    """Priority 1: main([]) returns count=0, total=0.0, average=0.0."""
    r = _run_main([])
    assert r.get("count") == 0, f"Expected count=0, got {r.get('count')}"
    assert r.get("total") == 0.0, f"Expected total=0.0, got {r.get('total')}"
    assert r.get("average") == 0.0, f"Expected average=0.0, got {r.get('average')}"


def test_stats_single_element():
    """Priority 1: main([5.0]) returns count=1, total=5.0, average=5.0."""
    r = _run_main([5.0])
    assert r.get("count") == 1
    assert r.get("total") == 5.0
    assert r.get("average") == 5.0


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
    data = _parse_simple_yaml(STATS_YAML)
    assert data.get("language") == "python3", f"Expected language='python3', got {repr(data.get('language'))}"


def test_yaml_summary():
    data = _parse_simple_yaml(STATS_YAML)
    assert data.get("summary") == "Compute basic statistics for a list of numbers", (
        f"Unexpected summary: {repr(data.get('summary'))}"
    )
