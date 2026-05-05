import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
USER_INFO_TS = os.path.join(SCRIPTS_DIR, "user_info.ts")
USER_INFO_YAML = os.path.join(SCRIPTS_DIR, "user_info.script.yaml")


def test_user_info_ts_exists():
    assert os.path.isfile(USER_INFO_TS), f"Expected '{USER_INFO_TS}' but file not found."


def test_user_info_yaml_exists():
    assert os.path.isfile(USER_INFO_YAML), f"Expected '{USER_INFO_YAML}' but file not found."


def _eval_user_info(id_: int, name: str, active: str = "") -> dict:
    """Strip TS type annotations, call main(), serialize result to JSON."""
    with open(USER_INFO_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*(number|string|boolean|Promise<[^>]+>)", "", src)
    js = js.replace("export async function", "async function")
    if active:
        call = f"main({id_}, {json.dumps(name)}, {active}).then(r => console.log(JSON.stringify(r)));"
    else:
        call = f"main({id_}, {json.dumps(name)}).then(r => console.log(JSON.stringify(r)));"
    result = subprocess.run(
        ["node", "-e", js + "\n" + call],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, (
        f"node failed (exit {result.returncode}): {result.stderr}"
    )
    return json.loads(result.stdout.strip())


def test_active_user_object():
    """Priority 1: main(1, 'Alice') returns correct object with active=true."""
    obj = _eval_user_info(1, "Alice")
    assert obj.get("id") == 1, f"Expected id=1, got {obj.get('id')}"
    assert obj.get("name") == "Alice", f"Expected name='Alice', got {obj.get('name')}"
    assert obj.get("active") is True, f"Expected active=true, got {obj.get('active')}"
    assert obj.get("display") == "[1] Alice (active)", (
        f"Expected display='[1] Alice (active)', got {repr(obj.get('display'))}"
    )


def test_inactive_user_object():
    """Priority 1: main(2, 'Bob', false) returns correct object with active=false."""
    obj = _eval_user_info(2, "Bob", "false")
    assert obj.get("id") == 2, f"Expected id=2, got {obj.get('id')}"
    assert obj.get("name") == "Bob", f"Expected name='Bob', got {obj.get('name')}"
    assert obj.get("active") is False, f"Expected active=false, got {obj.get('active')}"
    assert obj.get("display") == "[2] Bob (inactive)", (
        f"Expected display='[2] Bob (inactive)', got {repr(obj.get('display'))}"
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
    data = _parse_simple_yaml(USER_INFO_YAML)
    assert data.get("language") == "typescript", (
        f"Expected language='typescript', got {repr(data.get('language'))}"
    )


def test_yaml_summary():
    data = _parse_simple_yaml(USER_INFO_YAML)
    assert data.get("summary") == "Build a user info object", (
        f"Expected summary='Build a user info object', got {repr(data.get('summary'))}"
    )
