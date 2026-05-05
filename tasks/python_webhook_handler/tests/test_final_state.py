import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
WEBHOOK_PY = os.path.join(SCRIPTS_DIR, "handle_webhook.py")
WEBHOOK_YAML = os.path.join(SCRIPTS_DIR, "handle_webhook.script.yaml")


def test_webhook_py_exists():
    assert os.path.isfile(WEBHOOK_PY)


def test_webhook_yaml_exists():
    assert os.path.isfile(WEBHOOK_YAML)


def _run_main(event_type: str, payload: dict) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('wh', '{WEBHOOK_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({repr(event_type)}, {json.dumps(payload)})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_push_event():
    r = _run_main("push", {"repository": {"name": "my-repo"}, "commits": ["c1", "c2"]})
    assert r.get("action") == "push"
    assert r.get("repo") == "my-repo"
    assert r.get("commit_count") == 2
    assert r.get("handled") is True


def test_pull_request_event():
    r = _run_main("pull_request", {"action": "opened", "pull_request": {"title": "Fix bug"}})
    assert r.get("action") == "pull_request"
    assert r.get("pr_action") == "opened"
    assert r.get("title") == "Fix bug"
    assert r.get("handled") is True


def test_ping_event():
    r = _run_main("ping", {})
    assert r.get("action") == "ping"
    assert r.get("message") == "pong"
    assert r.get("handled") is True


def test_unknown_event():
    r = _run_main("deployment", {})
    assert r.get("handled") is False
    assert r.get("action") == "deployment"


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
    assert _parse_simple_yaml(WEBHOOK_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(WEBHOOK_YAML).get("summary") == "Dispatch and process incoming GitHub webhook events"
