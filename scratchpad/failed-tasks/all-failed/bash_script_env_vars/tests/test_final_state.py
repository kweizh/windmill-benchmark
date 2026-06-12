import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _script_dir() -> str:
    return os.path.join(PROJECT_DIR, "f", f"zealt_{_run_id()}")


def _extract_last_json_object(text: str) -> dict:
    """Find the last `{...}` JSON object in the text and return it as a dict."""
    matches = re.findall(r"\{[^{}]*\}", text or "", flags=re.DOTALL)
    assert matches, (
        f"No JSON object literal found in text: {text!r}"
    )
    last = matches[-1]
    try:
        return json.loads(last)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Last JSON-looking fragment is not valid JSON: {last!r} ({exc})"
        )


def test_bash_script_file_exists():
    script_path = os.path.join(_script_dir(), "echo_user.sh")
    assert os.path.isfile(script_path), (
        f"Expected Bash script source file at {script_path} but it was not found."
    )


def test_script_yaml_metadata_file_exists():
    yaml_path = os.path.join(_script_dir(), "echo_user.script.yaml")
    assert os.path.isfile(yaml_path), (
        f"Expected Windmill script metadata file at {yaml_path} but it was not found."
    )


def test_output_log_contains_expected_json():
    assert os.path.isfile(LOG_FILE), (
        f"Expected log file at {LOG_FILE} produced by the task but it was not found."
    )
    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    payload = _extract_last_json_object(content)
    assert payload.get("input") == "hello", (
        f"Expected JSON 'input' field to equal 'hello' in {LOG_FILE}, "
        f"got: {payload!r}"
    )
    user = payload.get("user")
    assert isinstance(user, str) and user.strip(), (
        f"Expected JSON 'user' field to be a non-empty string in {LOG_FILE}, "
        f"got: {payload!r}"
    )


def test_deployed_script_runs_on_cloud_workspace():
    script_path_on_instance = f"f/zealt_{_run_id()}/echo_user"
    # Windmill Bash scripts expose typed positional parameters. The parameter
    # name does not affect the positional ordering, so the verifier supplies
    # the input as the first declared field regardless of its key name.
    payload = json.dumps({"msg": "hello"})
    result = subprocess.run(
        ["wmill", "script", "run", script_path_on_instance, "-d", payload],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=180,
    )
    assert result.returncode == 0, (
        "`wmill script run` failed for the deployed Bash script. "
        f"stdout: {result.stdout!r} stderr: {result.stderr!r}"
    )
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    parsed = _extract_last_json_object(combined)
    assert parsed.get("input") == "hello", (
        "Expected the deployed Bash script to echo 'input':'hello' but "
        f"got: {parsed!r}. Full output: {combined!r}"
    )
    user = parsed.get("user")
    assert isinstance(user, str) and user.strip(), (
        "Expected the deployed Bash script to echo a non-empty 'user' field "
        f"(the value of WM_USERNAME) but got: {parsed!r}. Full output: {combined!r}"
    )
