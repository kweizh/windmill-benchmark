import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
DIVIDE_TS = os.path.join(SCRIPTS_DIR, "divide.ts")
DIVIDE_YAML = os.path.join(SCRIPTS_DIR, "divide.script.yaml")


def test_divide_ts_exists():
    assert os.path.isfile(DIVIDE_TS), f"Expected '{DIVIDE_TS}' but not found."


def test_divide_yaml_exists():
    assert os.path.isfile(DIVIDE_YAML), f"Expected '{DIVIDE_YAML}' but not found."


def _build_js() -> str:
    with open(DIVIDE_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    return js.replace("export async function", "async function")


def _eval_divide(n: float, d: float) -> dict:
    js = _build_js()
    call = f"main({n}, {d}).then(r => console.log(JSON.stringify(r)));"
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def _eval_divide_expect_error(n: float, d: float) -> str:
    js = _build_js()
    call = (
        f"main({n}, {d})"
        f".then(() => {{ process.stdout.write('NO_ERROR'); process.exit(0); }})"
        f".catch(e => {{ process.stdout.write(e.message); process.exit(0); }});"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def test_normal_division():
    """Priority 1: main(10, 2) → {result:5, numerator:10, denominator:2}"""
    r = _eval_divide(10, 2)
    assert r.get("result") == 5.0, f"Expected result=5, got {r.get('result')}"
    assert r.get("numerator") == 10, f"Expected numerator=10, got {r.get('numerator')}"
    assert r.get("denominator") == 2, f"Expected denominator=2, got {r.get('denominator')}"


def test_decimal_division():
    """Priority 1: main(7, 2) → result=3.5"""
    r = _eval_divide(7, 2)
    assert r.get("result") == 3.5, f"Expected result=3.5, got {r.get('result')}"


def test_division_by_zero_throws():
    """Priority 1: main(0, 0) must throw with the correct error message."""
    msg = _eval_divide_expect_error(0, 0)
    assert msg != "NO_ERROR", "Expected an error to be thrown for division by zero, but none was."
    assert "Division by zero is not allowed" in msg, (
        f"Expected error message 'Division by zero is not allowed', got: {repr(msg)}"
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
    assert _parse_simple_yaml(DIVIDE_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(DIVIDE_YAML).get("summary") == "Divide two numbers with zero-check"
