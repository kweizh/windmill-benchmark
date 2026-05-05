import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
PARSE_EVENT_PY = os.path.join(SCRIPTS_DIR, "parse_event.py")
PARSE_EVENT_YAML = os.path.join(SCRIPTS_DIR, "parse_event.script.yaml")

VALID_EVENT = json.dumps({
    "event": "user.signup",
    "user_id": 42,
    "metadata": {"plan": "pro", "source": "web"}
})


def test_parse_event_py_exists():
    assert os.path.isfile(PARSE_EVENT_PY), f"Expected '{PARSE_EVENT_PY}' but not found."


def test_parse_event_yaml_exists():
    assert os.path.isfile(PARSE_EVENT_YAML), f"Expected '{PARSE_EVENT_YAML}' but not found."


def _run_main(event_json: str) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('pe', '{PARSE_EVENT_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({repr(event_json)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def _run_main_expect_error(event_json: str) -> str:
    script = (
        f"import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('pe', '{PARSE_EVENT_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"try:\n"
        f"    mod.main({repr(event_json)})\n"
        f"    print('NO_ERROR')\n"
        f"except (ValueError, Exception) as e:\n"
        f"    print(str(e))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def test_valid_event_parsing():
    """Priority 1: all fields extracted correctly from valid JSON."""
    r = _run_main(VALID_EVENT)
    assert r.get("event") == "user.signup"
    assert r.get("user_id") == 42
    assert r.get("plan") == "pro"
    assert r.get("source") == "web"
    assert "user.signup" in r.get("summary", ""), f"summary should reference event: {r.get('summary')}"
    assert "42" in r.get("summary", ""), f"summary should reference user_id 42: {r.get('summary')}"


def test_invalid_json_raises_error():
    """Priority 1: invalid JSON raises an error."""
    msg = _run_main_expect_error("not-json")
    assert msg != "NO_ERROR", "Expected an error for invalid JSON, got none."


def test_missing_metadata_fields_use_defaults():
    """Priority 1: missing plan/source default to 'free'/'unknown'."""
    minimal = json.dumps({"event": "user.login", "user_id": 1, "metadata": {}})
    r = _run_main(minimal)
    assert r.get("plan") == "free", f"Expected plan='free', got {repr(r.get('plan'))}"
    assert r.get("source") == "unknown", f"Expected source='unknown', got {repr(r.get('source'))}"


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
    assert _parse_simple_yaml(PARSE_EVENT_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(PARSE_EVENT_YAML).get("summary") == "Parse and summarize a JSON event payload"
