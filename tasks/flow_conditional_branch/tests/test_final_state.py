import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"
CHECK_SCORE_TS = os.path.join(SCRIPTS_DIR, "check_score.ts")
ON_PASS_TS = os.path.join(SCRIPTS_DIR, "on_pass.ts")
ON_FAIL_TS = os.path.join(SCRIPTS_DIR, "on_fail.ts")
FLOW_YAML = os.path.join(FLOWS_DIR, "score_check.yaml")


def _strip_ts(src: str) -> str:
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    return js.replace("export async function", "async function")


def _eval_ts(path: str, call_expr: str) -> str:
    with open(path) as fh:
        src = fh.read()
    js = _strip_ts(src)
    result = subprocess.run(["node", "-e", js + "\n" + call_expr], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed for {path}: {result.stderr}"
    return result.stdout.strip()


def test_check_score_ts_exists():
    assert os.path.isfile(CHECK_SCORE_TS)


def test_on_pass_ts_exists():
    assert os.path.isfile(ON_PASS_TS)


def test_on_fail_ts_exists():
    assert os.path.isfile(ON_FAIL_TS)


def test_flow_yaml_exists():
    assert os.path.isfile(FLOW_YAML), f"Expected '{FLOW_YAML}' but not found."


def test_check_score_passing():
    """Priority 1: score=75 → passed=true"""
    out = json.loads(_eval_ts(CHECK_SCORE_TS, "main(75).then(r => console.log(JSON.stringify(r)));"))
    assert out.get("score") == 75
    assert out.get("passed") is True


def test_check_score_failing():
    """Priority 1: score=40 → passed=false"""
    out = json.loads(_eval_ts(CHECK_SCORE_TS, "main(40).then(r => console.log(JSON.stringify(r)));"))
    assert out.get("passed") is False


def test_on_pass_message():
    """Priority 1: on_pass returns correct string."""
    out = _eval_ts(ON_PASS_TS, "main(75).then(r => process.stdout.write(r));")
    assert out == "Score 75: PASSED", f"Got: {repr(out)}"


def test_on_fail_message():
    """Priority 1: on_fail returns correct string."""
    out = _eval_ts(ON_FAIL_TS, "main(40).then(r => process.stdout.write(r));")
    assert out == "Score 40: FAILED", f"Got: {repr(out)}"


def test_flow_yaml_uses_branchone():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "branchone" in content, "Flow must use 'branchone' module type."


def test_flow_yaml_references_results_a_passed():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "results.a.passed" in content, "Branch condition must reference 'results.a.passed'."


def test_flow_yaml_references_on_pass_and_on_fail():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "on_pass" in content, "Flow must reference on_pass script."
    assert "on_fail" in content, "Flow must reference on_fail script."
