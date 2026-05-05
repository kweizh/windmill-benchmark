import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
NOTIFY_PY = os.path.join(SCRIPTS_DIR, "send_notification.py")
NOTIFY_YAML = os.path.join(SCRIPTS_DIR, "send_notification.script.yaml")


def test_notify_py_exists():
    assert os.path.isfile(NOTIFY_PY), f"Expected '{NOTIFY_PY}' but not found."


def test_notify_yaml_exists():
    assert os.path.isfile(NOTIFY_YAML), f"Expected '{NOTIFY_YAML}' but not found."


def _run_main(*args, **kwargs) -> dict:
    all_args = list(args) + [f"{k}={repr(v)}" for k, v in kwargs.items()]
    arg_str = ", ".join(repr(a) if isinstance(a, str) else str(a) for a in args)
    if kwargs:
        kwarg_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
        call_args = f"{arg_str}, {kwarg_str}" if arg_str else kwarg_str
    else:
        call_args = arg_str
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('sn', '{NOTIFY_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({call_args})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_defaults():
    """Priority 1: all defaults applied when only message provided."""
    r = _run_main("Hello")
    assert r.get("to") == "admin@example.com", f"Got to={r.get('to')}"
    assert r.get("subject") == "Notification", f"Got subject={r.get('subject')}"
    assert r.get("body") == "Hello", f"Got body={r.get('body')}"
    assert r.get("priority") == 1, f"Got priority={r.get('priority')}"
    assert r.get("sent") is False, f"Got sent={r.get('sent')}"


def test_all_params():
    """Priority 1: explicit values override defaults."""
    r = _run_main("Alert", "ops@example.com", "Urgent", 3)
    assert r.get("to") == "ops@example.com"
    assert r.get("subject") == "Urgent"
    assert r.get("body") == "Alert"
    assert r.get("priority") == 3
    assert r.get("sent") is False


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
    assert _parse_simple_yaml(NOTIFY_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(NOTIFY_YAML).get("summary") == "Prepare a notification payload"
