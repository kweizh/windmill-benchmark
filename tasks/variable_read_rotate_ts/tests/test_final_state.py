import json
import os
import re
import subprocess
import urllib.request

import pytest

PROJECT_DIR = "/home/user/project"
SCRIPT_FILE = "/home/user/project/f/eval/var_rotate.ts"
SCRIPT_PATH_REMOTE = "f/eval/var_rotate"
VARIABLE_PATH = "f/eval/session_token"
INITIAL_VALUE = "INITIAL_SECRET"
ROTATED_VALUE = "INITIAL_SECRET_rotated"
WINDMILL_BASE_URL = "https://app.windmill.dev"


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    assert value, f"Environment variable {name} must be set during verification."
    return value


def _extract_last_json_object(text: str) -> dict:
    """Find the last balanced top-level JSON object embedded in CLI output."""
    last: dict | None = None
    for start in range(len(text)):
        if text[start] != "{":
            continue
        depth = 0
        in_string = False
        escape = False
        for end in range(start, len(text)):
            ch = text[end]
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : end + 1]
                    try:
                        parsed = json.loads(candidate)
                    except json.JSONDecodeError:
                        break
                    if isinstance(parsed, dict):
                        last = parsed
                    break
    if last is None:
        raise ValueError(f"No JSON object found in CLI output:\n{text!r}")
    return last


def test_script_file_exists_and_uses_expected_apis():
    """The agent must have created the TypeScript script with the required SDK calls."""
    assert os.path.isfile(SCRIPT_FILE), (
        f"Expected the TypeScript script file at {SCRIPT_FILE} to exist after the task completes."
    )
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        contents = f.read()

    assert re.search(r"from\s+['\"]windmill-client['\"]", contents), (
        f"Expected {SCRIPT_FILE} to import from the `windmill-client` package."
    )
    assert re.search(r"getVariable\s*\(", contents), (
        f"Expected {SCRIPT_FILE} to invoke `getVariable(` from the windmill-client SDK."
    )
    assert re.search(r"setVariable\s*\(", contents), (
        f"Expected {SCRIPT_FILE} to invoke `setVariable(` from the windmill-client SDK."
    )


def test_wmill_script_run_returns_expected_rotation_payload():
    """`wmill script run f/eval/var_rotate` must succeed and report the previous/next pair."""
    env = os.environ.copy()
    result = subprocess.run(
        ["wmill", "script", "run", SCRIPT_PATH_REMOTE],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert result.returncode == 0, (
        f"`wmill script run {SCRIPT_PATH_REMOTE}` failed with exit code {result.returncode}.\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )

    combined = result.stdout + "\n" + result.stderr
    try:
        payload = _extract_last_json_object(combined)
    except ValueError as exc:
        pytest.fail(
            f"Could not find a JSON object in the wmill output: {exc}\n"
            f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
        )

    assert payload.get("previous") == INITIAL_VALUE, (
        f"Expected JSON field `previous` to equal {INITIAL_VALUE!r}, got payload {payload!r}."
    )
    assert payload.get("next") == ROTATED_VALUE, (
        f"Expected JSON field `next` to equal {ROTATED_VALUE!r}, got payload {payload!r}."
    )


def test_remote_variable_value_has_been_rotated():
    """Re-read the workspace variable via the Windmill API and verify it was updated."""
    token = _required_env("WINDMILL_TOKEN")
    workspace = _required_env("WINDMILL_WORKSPACE")
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/variables/get_value/{VARIABLE_PATH}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosec - trusted external API
            body = resp.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            f"Failed to query the post-rotation value of {VARIABLE_PATH} from Windmill Cloud: {exc!r}"
        )

    try:
        decoded = json.loads(body)
    except json.JSONDecodeError:
        decoded = body

    assert decoded == ROTATED_VALUE, (
        f"Expected workspace variable {VARIABLE_PATH} to be {ROTATED_VALUE!r} after rotation, "
        f"got {decoded!r}."
    )
