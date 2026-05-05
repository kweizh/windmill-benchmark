import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"
WORD_COUNT_TS = os.path.join(SCRIPTS_DIR, "compute_word_count.ts")
CHAR_COUNT_TS = os.path.join(SCRIPTS_DIR, "compute_char_count.ts")
LINE_COUNT_TS = os.path.join(SCRIPTS_DIR, "compute_line_count.ts")
FLOW_YAML = os.path.join(FLOWS_DIR, "text_stats.yaml")

SAMPLE_TEXT = "Hello World\nThis is Windmill"


def _eval_ts(path: str, call_expr: str) -> dict:
    with open(path) as fh:
        src = fh.read()
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    js = js.replace("export async function", "async function")
    result = subprocess.run(["node", "-e", js + "\n" + call_expr], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed for {path}: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_word_count_ts_exists():
    assert os.path.isfile(WORD_COUNT_TS)


def test_char_count_ts_exists():
    assert os.path.isfile(CHAR_COUNT_TS)


def test_line_count_ts_exists():
    assert os.path.isfile(LINE_COUNT_TS)


def test_flow_yaml_exists():
    assert os.path.isfile(FLOW_YAML)


def test_word_count_runtime():
    """Priority 1: 'Hello World\\nThis is Windmill' → 5 words."""
    r = _eval_ts(WORD_COUNT_TS, f"main({repr(SAMPLE_TEXT)}).then(r => console.log(JSON.stringify(r)));")
    assert r.get("word_count") == 5, f"Expected word_count=5, got {r.get('word_count')}"


def test_char_count_runtime():
    """Priority 1: char_count = len(text), char_count_no_spaces excludes whitespace."""
    r = _eval_ts(CHAR_COUNT_TS, f"main({repr(SAMPLE_TEXT)}).then(r => console.log(JSON.stringify(r)));")
    assert r.get("char_count") == len(SAMPLE_TEXT), f"Expected char_count={len(SAMPLE_TEXT)}, got {r.get('char_count')}"
    no_spaces = len(SAMPLE_TEXT.replace(" ", "").replace("\n", ""))
    assert r.get("char_count_no_spaces") == no_spaces, (
        f"Expected char_count_no_spaces={no_spaces}, got {r.get('char_count_no_spaces')}"
    )


def test_line_count_runtime():
    """Priority 1: 'Hello World\\nThis is Windmill' → 2 lines."""
    r = _eval_ts(LINE_COUNT_TS, f"main({repr(SAMPLE_TEXT)}).then(r => console.log(JSON.stringify(r)));")
    assert r.get("line_count") == 2, f"Expected line_count=2, got {r.get('line_count')}"


def test_flow_uses_branchall():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "branchall" in content, "Flow must use 'branchall' for parallel execution."


def test_flow_has_parallel_true():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "parallel: true" in content or "parallel:true" in content, (
        "Flow must set 'parallel: true' on the branchall module."
    )


def test_flow_references_all_three_scripts():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "compute_word_count" in content, "Flow must reference compute_word_count script."
    assert "compute_char_count" in content, "Flow must reference compute_char_count script."
    assert "compute_line_count" in content, "Flow must reference compute_line_count script."
