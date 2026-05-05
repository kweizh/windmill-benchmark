import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FILTER_TS = os.path.join(SCRIPTS_DIR, "filter_users.ts")
FILTER_YAML = os.path.join(SCRIPTS_DIR, "filter_users.script.yaml")

SAMPLE_USERS = [
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
    {"id": 3, "name": "Carol", "active": True},
]


def test_filter_users_ts_exists():
    assert os.path.isfile(FILTER_TS), f"Expected '{FILTER_TS}' but not found."


def test_filter_users_yaml_exists():
    assert os.path.isfile(FILTER_YAML), f"Expected '{FILTER_YAML}' but not found."


def _eval_filter(users: list, active_only: bool = True) -> list:
    with open(FILTER_TS) as fh:
        src = fh.read()
    js = re.sub(r"Array<[^>]+>", "", src)
    js = re.sub(r":\s*(number|string|boolean)", "", js)
    js = js.replace("export async function", "async function")
    call = (
        f"main({json.dumps(users)}, {'true' if active_only else 'false'})"
        f".then(r => console.log(JSON.stringify(r)));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_active_only_filter():
    """Priority 1: active_only=true returns only active users."""
    out = _eval_filter(SAMPLE_USERS, active_only=True)
    assert len(out) == 2, f"Expected 2 active users, got {len(out)}"
    ids = {u["id"] for u in out}
    assert ids == {1, 3}, f"Expected ids {{1, 3}}, got {ids}"


def test_display_format():
    """Priority 1: display field uses em-dash format."""
    out = _eval_filter(SAMPLE_USERS, active_only=True)
    for u in out:
        expected = f"#{u['id']} \u2014 {u['name']}"
        assert u.get("display") == expected, (
            f"Expected display='{expected}', got {repr(u.get('display'))}"
        )


def test_all_users_when_active_only_false():
    """Priority 1: active_only=false returns all 3 users."""
    out = _eval_filter(SAMPLE_USERS, active_only=False)
    assert len(out) == 3, f"Expected 3 users, got {len(out)}"


def test_empty_array():
    """Priority 1: empty input returns empty array."""
    out = _eval_filter([], active_only=True)
    assert out == [], f"Expected [], got {out}"


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
    assert _parse_simple_yaml(FILTER_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(FILTER_YAML).get("summary") == "Filter and format a list of users"
