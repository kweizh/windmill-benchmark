import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
EXPECTED_OUTPUT = {"computed": 10, "target": "x"}


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for verification."
    return run_id


def _script_remote_path() -> str:
    return f"f/zealt/go_arith_{_run_id()}"


def _script_local_path() -> str:
    return os.path.join(PROJECT_DIR, "f", "zealt", f"go_arith_{_run_id()}.go")


def _yaml_local_path() -> str:
    return os.path.join(PROJECT_DIR, "f", "zealt", f"go_arith_{_run_id()}.script.yaml")


def _read_log() -> str:
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()


def test_go_source_file_exists():
    path = _script_local_path()
    assert os.path.isfile(path), f"Expected Go source file at {path}."
    assert os.path.getsize(path) > 0, f"Go source file {path} must not be empty."


def test_script_yaml_metadata_exists():
    path = _yaml_local_path()
    assert os.path.isfile(path), f"Expected Windmill script metadata file at {path}."
    assert os.path.getsize(path) > 0, f"Metadata file {path} must not be empty."


def test_log_contains_script_path_line():
    content = _read_log()
    expected = f"Script path: {_script_remote_path()}"
    assert expected in content, (
        f"Expected log line {expected!r} in {LOG_FILE}. Got:\n{content}"
    )


def test_log_contains_output_line_with_expected_json():
    content = _read_log()
    match = re.search(r"^Output:\s*(\{.*\})\s*$", content, flags=re.MULTILINE)
    assert match, (
        f"Expected a line matching 'Output: <json>' in {LOG_FILE}. Got:\n{content}"
    )
    payload_text = match.group(1)
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Output line JSON did not parse: {exc}. Raw: {payload_text!r}"
        )
    assert payload == EXPECTED_OUTPUT, (
        f"Expected log Output JSON to equal {EXPECTED_OUTPUT}, got {payload}."
    )


def test_script_deployed_on_cloud_workspace():
    result = subprocess.run(
        ["wmill", "script", "list", "--json"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
    )
    assert result.returncode == 0, (
        f"`wmill script list --json` failed with exit {result.returncode}. stderr: {result.stderr}"
    )
    try:
        scripts = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"`wmill script list --json` produced invalid JSON: {exc}. stdout: {result.stdout!r}"
        )

    paths = []
    if isinstance(scripts, list):
        for item in scripts:
            if isinstance(item, dict):
                value = item.get("path")
                if isinstance(value, str):
                    paths.append(value)

    expected_path = _script_remote_path()
    assert expected_path in paths, (
        f"Expected script {expected_path!r} to be deployed in the cloud workspace. Found: {paths}"
    )


def test_remote_execution_returns_expected_output():
    expected_path = _script_remote_path()
    payload = json.dumps({"threshold": 5, "name": "x"})
    result = subprocess.run(
        [
            "wmill",
            "script",
            "run",
            expected_path,
            "--data",
            payload,
            "--silent",
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=180,
    )
    assert result.returncode == 0, (
        f"`wmill script run {expected_path}` failed with exit {result.returncode}. "
        f"stderr: {result.stderr}\nstdout: {result.stdout}"
    )

    stdout = result.stdout.strip()
    # The silent mode prints only the final output. Try to locate a JSON object in the output.
    json_match = re.search(r"\{.*\}", stdout, flags=re.DOTALL)
    assert json_match, (
        f"Expected a JSON object in `wmill script run` stdout, got: {stdout!r}"
    )
    try:
        payload_out = json.loads(json_match.group(0))
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"`wmill script run` stdout JSON did not parse: {exc}. Raw: {json_match.group(0)!r}"
        )

    assert payload_out == EXPECTED_OUTPUT, (
        f"Expected remote script output to equal {EXPECTED_OUTPUT}, got {payload_out}."
    )
