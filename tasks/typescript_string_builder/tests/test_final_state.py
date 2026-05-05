import os
import re
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
BUILD_REPORT_TS = os.path.join(SCRIPTS_DIR, "build_report.ts")
BUILD_REPORT_YAML = os.path.join(SCRIPTS_DIR, "build_report.script.yaml")


def test_build_report_ts_exists():
    assert os.path.isfile(BUILD_REPORT_TS), f"Expected '{BUILD_REPORT_TS}' but not found."


def test_build_report_yaml_exists():
    assert os.path.isfile(BUILD_REPORT_YAML), f"Expected '{BUILD_REPORT_YAML}' but not found."


def _eval_report(*args) -> str:
    with open(BUILD_REPORT_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*(string|string\[\])", "", src)
    js = js.replace("export async function", "async function")
    arg_str = ", ".join(
        repr(a) if isinstance(a, str) else f"[{', '.join(repr(x) for x in a)}]"
        for a in args
    )
    call = f"main({arg_str}).then(r => process.stdout.write(r));"
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return result.stdout


def test_report_structure():
    """Priority 1: header, items, and footer are correctly assembled."""
    report = _eval_report("Sales", ["Widget A: $10", "Widget B: $20"])
    lines = report.split("\n")
    assert lines[0] == "=== Sales ===", f"Expected header '=== Sales ===', got {repr(lines[0])}"
    assert lines[1] == "- Widget A: $10", f"Expected '- Widget A: $10', got {repr(lines[1])}"
    assert lines[2] == "- Widget B: $20", f"Expected '- Widget B: $20', got {repr(lines[2])}"
    assert lines[3] == "--- End of report ---", f"Expected footer, got {repr(lines[3])}"


def test_custom_footer():
    """Priority 1: custom footer replaces default."""
    report = _eval_report("Q1", ["Alpha"], "Done")
    assert "--- Done ---" in report, f"Custom footer not found in: {repr(report)}"


def test_empty_items():
    """Priority 1: empty items list gives 2-line report."""
    report = _eval_report("Empty", [])
    lines = report.split("\n")
    assert len(lines) == 2, f"Expected 2 lines for empty items, got {len(lines)}: {lines}"
    assert lines[0] == "=== Empty ==="
    assert lines[1] == "--- End of report ---"


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
    assert _parse_simple_yaml(BUILD_REPORT_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(BUILD_REPORT_YAML).get("summary") == "Build a formatted text report from a list of items"
