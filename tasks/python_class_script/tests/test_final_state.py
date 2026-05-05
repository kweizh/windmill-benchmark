import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
REPORT_PY = os.path.join(SCRIPTS_DIR, "generate_report.py")
REPORT_YAML = os.path.join(SCRIPTS_DIR, "generate_report.script.yaml")


def test_report_py_exists():
    assert os.path.isfile(REPORT_PY)


def test_report_yaml_exists():
    assert os.path.isfile(REPORT_YAML)


def _run_main(title: str, sections: list) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('gr', '{REPORT_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({repr(title)}, {json.dumps(sections)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_two_section_report():
    sections = [{"heading": "Revenue", "content": "$1M"}, {"heading": "Costs", "content": "$0.5M"}]
    r = _run_main("Q1 Report", sections)
    assert r.get("section_count") == 2, f"Expected section_count=2, got {r.get('section_count')}"
    assert r.get("title") == "Q1 Report"
    text = r.get("text", "")
    assert text.startswith("# Q1 Report"), f"text must start with '# Q1 Report', got: {repr(text[:50])}"
    assert "## Revenue" in text, "text must contain '## Revenue'"
    assert "$1M" in text, "text must contain section content '$1M'"


def test_empty_sections():
    r = _run_main("Empty", [])
    assert r.get("section_count") == 0
    assert r.get("text") == "# Empty", f"Expected '# Empty', got {repr(r.get('text'))}"


def test_fluent_add_section_returns_self():
    """Priority 1: verify add_section fluent interface at runtime."""
    script = (
        f"import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('gr', '{REPORT_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"builder = mod.ReportBuilder('Test')\n"
        f"result = builder.add_section('H', 'C')\n"
        f"print('same' if result is builder else 'different')\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    assert result.stdout.strip() == "same", "add_section must return self (fluent interface)."


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
    assert _parse_simple_yaml(REPORT_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(REPORT_YAML).get("summary") == "Generate a structured report from sections"
