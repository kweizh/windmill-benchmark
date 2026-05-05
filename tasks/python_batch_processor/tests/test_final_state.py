import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
BATCH_PY = os.path.join(SCRIPTS_DIR, "batch_process.py")
BATCH_YAML = os.path.join(SCRIPTS_DIR, "batch_process.script.yaml")


def test_batch_py_exists():
    assert os.path.isfile(BATCH_PY)


def test_batch_yaml_exists():
    assert os.path.isfile(BATCH_YAML)


def _run_main(items: list, batch_size: int = 10, transform: str = "upper") -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('bp', '{BATCH_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({json.dumps(items)}, {batch_size}, {repr(transform)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def _run_expect_error(items: list, transform: str) -> str:
    script = (
        f"import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('bp', '{BATCH_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"try:\n"
        f"    mod.main({json.dumps(items)}, 10, {repr(transform)})\n"
        f"    print('NO_ERROR')\n"
        f"except ValueError as e:\n"
        f"    print(str(e))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def test_upper_transform_with_batching():
    """Priority 1: 3 items in batches of 2 → batch_count=2, results uppercased."""
    r = _run_main(["hello", "world", "foo"], batch_size=2, transform="upper")
    assert r.get("results") == ["HELLO", "WORLD", "FOO"]
    assert r.get("batch_count") == 2, f"Expected batch_count=2, got {r.get('batch_count')}"
    assert r.get("total") == 3
    assert len(r.get("batches", [])) == 2


def test_reverse_transform():
    """Priority 1: reverse transform."""
    r = _run_main(["abc"], batch_size=10, transform="reverse")
    assert r.get("results") == ["cba"], f"Expected ['cba'], got {r.get('results')}"


def test_empty_list():
    """Priority 1: empty input."""
    r = _run_main([], transform="lower")
    assert r.get("total") == 0
    assert r.get("batch_count") == 0
    assert r.get("results") == []


def test_invalid_transform_raises():
    """Priority 1: invalid transform raises ValueError."""
    msg = _run_expect_error(["x"], "invalid")
    assert msg != "NO_ERROR", "Expected ValueError for invalid transform."
    assert "invalid" in msg.lower() or "unknown" in msg.lower() or "choose" in msg.lower(), (
        f"Expected informative error, got: {repr(msg)}"
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
    assert _parse_simple_yaml(BATCH_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(BATCH_YAML).get("summary") == "Process a list of strings in configurable batches"
