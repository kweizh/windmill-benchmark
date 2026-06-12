import json
import os
import re

import requests

PROJECT_DIR = "/home/user/wmill_project"
LOG_FILE = os.path.join(PROJECT_DIR, "run.log")


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for verification."
    return run_id


def _wmill_base_url() -> str:
    base_url = os.environ.get("WMILL_BASE_URL")
    assert base_url, "WMILL_BASE_URL must be set for cloud verification."
    return base_url.rstrip("/")


def _wmill_workspace() -> str:
    workspace = os.environ.get("WMILL_WORKSPACE_ID")
    assert workspace, "WMILL_WORKSPACE_ID must be set for cloud verification."
    return workspace


def _wmill_token() -> str:
    token = os.environ.get("WMILL_TOKEN")
    assert token, "WMILL_TOKEN must be set for cloud verification."
    return token


def _script_path() -> str:
    return f"f/zealt_demo/sum_ts_{_run_id()}"


def test_local_script_ts_file_exists() -> None:
    expected = os.path.join(PROJECT_DIR, "f", "zealt_demo", f"sum_ts_{_run_id()}.ts")
    assert os.path.isfile(expected), (
        f"Expected TypeScript script file pair member at {expected} but it was not found."
    )


def test_local_script_yaml_file_exists() -> None:
    expected = os.path.join(
        PROJECT_DIR, "f", "zealt_demo", f"sum_ts_{_run_id()}.script.yaml"
    )
    assert os.path.isfile(expected), (
        f"Expected Windmill script metadata file at {expected} but it was not found."
    )


def test_main_function_signature_is_typed() -> None:
    ts_path = os.path.join(PROJECT_DIR, "f", "zealt_demo", f"sum_ts_{_run_id()}.ts")
    assert os.path.isfile(ts_path), f"Missing TypeScript script source at {ts_path}."
    with open(ts_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(
        r"export\s+async\s+function\s+main\s*\(\s*a\s*:\s*number\s*,\s*b\s*:\s*number\s*\)",
        re.MULTILINE,
    )
    assert pattern.search(content), (
        "The main function in the .ts file must be declared as "
        "`export async function main(a: number, b: number)` with both parameters typed as number."
    )


def test_script_deployed_to_cloud_workspace() -> None:
    url = (
        f"{_wmill_base_url()}/api/w/{_wmill_workspace()}/scripts/get/p/{_script_path()}"
    )
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {_wmill_token()}"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Expected the script to be deployed and retrievable at {url}, "
        f"but got HTTP {response.status_code}: {response.text}"
    )
    body = response.json()
    assert body.get("path") == _script_path(), (
        f"Deployed script path mismatch: expected {_script_path()}, got {body.get('path')!r}"
    )


def test_log_file_contains_sum_result() -> None:
    assert os.path.isfile(LOG_FILE), (
        f"Expected run log file at {LOG_FILE} containing the wmill script run output."
    )
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content, f"Run log file {LOG_FILE} is empty."

    # Extract the last balanced JSON object from the log content.
    last_obj_match = None
    depth = 0
    start = -1
    for i, ch in enumerate(content):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                last_obj_match = content[start : i + 1]
    assert last_obj_match, (
        f"Could not find a JSON object inside {LOG_FILE}; content was: {content!r}"
    )
    parsed = json.loads(last_obj_match)
    assert "sum" in parsed, (
        f"Run output JSON must contain a 'sum' field, got: {parsed!r}"
    )
    assert parsed["sum"] == 5, (
        f"Expected sum=5 in run output, got sum={parsed['sum']!r}"
    )


def test_deployed_script_returns_correct_sum_via_api() -> None:
    url = (
        f"{_wmill_base_url()}/api/w/{_wmill_workspace()}/jobs/run_wait_result/p/"
        f"{_script_path()}"
    )
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {_wmill_token()}",
            "Content-Type": "application/json",
        },
        json={"a": 2, "b": 3},
        timeout=120,
    )
    assert response.status_code == 200, (
        f"Synchronous run via {url} failed with HTTP {response.status_code}: {response.text}"
    )
    # The endpoint returns the raw script result.
    try:
        result = response.json()
    except ValueError as exc:  # pragma: no cover - defensive
        raise AssertionError(
            f"Expected JSON response from run_wait_result, got: {response.text!r}"
        ) from exc
    assert isinstance(result, dict), (
        f"Expected a JSON object result from the script, got: {result!r}"
    )
    assert result.get("sum") == 5, (
        f"Expected the deployed script to return sum=5 for a=2, b=3, got: {result!r}"
    )
