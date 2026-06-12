import json
import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/windmill-webhook"
HEADERS_FILE = os.path.join(PROJECT_DIR, "response.headers")
BODY_FILE = os.path.join(PROJECT_DIR, "response.body.json")
WINDMILL_INSTANCE_URL = "https://app.windmill.dev"


def _env(name: str) -> str:
    value = os.environ.get(name)
    assert value, f"Required environment variable {name} is not set."
    return value


@pytest.fixture(scope="module")
def windmill_env() -> dict:
    run_id = _env("ZEALT_RUN_ID")
    token = _env("WINDMILL_TOKEN")
    workspace = _env("WINDMILL_WORKSPACE")
    username = _env("WINDMILL_USERNAME")
    run_id_safe = run_id.replace("-", "_")
    script_path = f"u/{username}/echo_message_{run_id_safe}"
    expected_body_value = f"harbor-{run_id}"
    return {
        "run_id": run_id,
        "token": token,
        "workspace": workspace,
        "username": username,
        "run_id_safe": run_id_safe,
        "script_path": script_path,
        "expected_body_value": expected_body_value,
    }


def test_script_is_deployed_in_workspace(windmill_env: dict) -> None:
    """Use the Windmill API to confirm the script exists at the expected path."""
    url = (
        f"{WINDMILL_INSTANCE_URL}/api/w/{windmill_env['workspace']}"
        f"/scripts/get/p/{windmill_env['script_path']}"
    )
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {windmill_env['token']}"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Expected HTTP 200 from {url} when fetching the deployed script, "
        f"got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert data.get("path") == windmill_env["script_path"], (
        f"Expected deployed script path to be {windmill_env['script_path']!r}, "
        f"got {data.get('path')!r}."
    )


def test_response_headers_file_exists_and_has_200_status() -> None:
    """The captured HTTP response headers file must exist, be non-empty, and start with HTTP/.* 200."""
    assert os.path.isfile(HEADERS_FILE), (
        f"Captured headers file {HEADERS_FILE} does not exist."
    )
    with open(HEADERS_FILE, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    assert content.strip(), f"Captured headers file {HEADERS_FILE} is empty."

    lines = [line for line in content.splitlines() if line.strip()]
    assert lines, f"Captured headers file {HEADERS_FILE} has no non-empty lines."
    status_line = lines[0]
    assert status_line.startswith("HTTP/"), (
        f"First non-empty line of {HEADERS_FILE} must start with 'HTTP/', "
        f"got: {status_line!r}"
    )
    assert re.search(r"\b200\b", status_line), (
        f"Expected HTTP status 200 in the status line, got: {status_line!r}"
    )


def test_response_headers_file_contains_json_content_type() -> None:
    """The Content-Type header in the captured response must contain 'application/json'."""
    with open(HEADERS_FILE, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    content_type_value = None
    for line in content.splitlines():
        if ":" not in line:
            continue
        name, _, value = line.partition(":")
        if name.strip().lower() == "content-type":
            content_type_value = value.strip().lower()
            break
    assert content_type_value is not None, (
        f"No 'Content-Type' header found in {HEADERS_FILE}."
    )
    assert "application/json" in content_type_value, (
        f"Expected Content-Type to contain 'application/json', got: {content_type_value!r}"
    )


def test_response_body_matches_expected_json(windmill_env: dict) -> None:
    """The captured response body must equal exactly {'echoed': 'harbor-<ZEALT_RUN_ID>'}."""
    assert os.path.isfile(BODY_FILE), (
        f"Captured body file {BODY_FILE} does not exist."
    )
    with open(BODY_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"Captured body file {BODY_FILE} is not valid JSON: {exc}; content was: {raw!r}"
        )
    expected = {"echoed": windmill_env["expected_body_value"]}
    assert parsed == expected, (
        f"Expected response body to equal {expected!r}, got {parsed!r}."
    )
