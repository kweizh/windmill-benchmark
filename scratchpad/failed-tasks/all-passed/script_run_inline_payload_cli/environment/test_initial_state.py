import json
import os
import shutil
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user"
SCRIPT_PATH = "f/zealt_eval/add_numbers"
SCRIPT_FILE = "/opt/wmill_bootstrap/f/zealt_eval/add_numbers.py"
LOCAL_WORKSPACE_NAME = "evaluation"


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    assert value, (
        f"Environment variable `{name}` must be set so the initial-state setup "
        "can authenticate against Windmill Cloud and pre-deploy the addition script."
    )
    return value


@pytest.fixture(scope="session", autouse=True)
def bootstrap_windmill_workspace():
    """Configure the wmill CLI workspace and ensure the addition script is
    deployed on Windmill Cloud before the agent runs."""
    base_url = _required_env("WMILL_BASE_URL").rstrip("/")
    workspace_id = _required_env("WMILL_WORKSPACE_ID")
    token = _required_env("WMILL_TOKEN")

    # 1) Register a local CLI workspace pointing at the cloud workspace. The
    #    `wmill workspace add` command is idempotent: it overwrites the entry
    #    when the local workspace name is reused.
    add_result = subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            LOCAL_WORKSPACE_NAME,
            workspace_id,
            f"{base_url}/",
            "--token",
            token,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert add_result.returncode == 0, (
        "Failed to register Windmill Cloud workspace with `wmill workspace add`. "
        f"stdout={add_result.stdout!r} stderr={add_result.stderr!r}"
    )

    # 2) Ensure the addition script is deployed at SCRIPT_PATH using the
    #    Windmill REST API. We tolerate the case where the script already
    #    exists (concurrent runs share the same cloud workspace).
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    exists_url = f"{base_url}/api/w/{workspace_id}/scripts/exists/p/{SCRIPT_PATH}"
    exists_resp = requests.get(exists_url, headers=headers, timeout=60)
    assert exists_resp.status_code == 200, (
        "Failed to query Windmill scripts existence endpoint: "
        f"status={exists_resp.status_code} body={exists_resp.text!r}"
    )

    if exists_resp.json() is not True:
        with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        body = {
            "path": SCRIPT_PATH,
            "summary": "Add two numbers",
            "description": "Returns the sum of inputs `a` and `b`.",
            "content": content,
            "language": "python3",
            "is_template": False,
            "kind": "script",
            "schema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "order": ["a", "b"],
                "properties": {
                    "a": {"type": "integer", "description": "First addend"},
                    "b": {"type": "integer", "description": "Second addend"},
                },
                "required": ["a", "b"],
            },
        }
        create_url = f"{base_url}/api/w/{workspace_id}/scripts/create"
        create_resp = requests.post(
            create_url, headers=headers, json=body, timeout=60
        )
        # Accept 200/201 success or 400 conflict (script created by a parallel run
        # in the same workspace between our existence check and create call).
        assert create_resp.status_code in (200, 201, 400, 409), (
            "Failed to deploy the `add_numbers` Windmill script via API. "
            f"status={create_resp.status_code} body={create_resp.text!r}"
        )

    yield


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, (
        "The `wmill` CLI binary was not found in PATH; the Windmill CLI must be "
        "installed for this task."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected the project directory {PROJECT_DIR} to exist before the task starts."
    )


def test_bootstrap_script_file_present():
    # Sanity-check that the bootstrap copy of the addition script is in place;
    # the initial-state fixture uses it to seed the cloud workspace.
    assert os.path.isfile(SCRIPT_FILE), (
        f"Bootstrap addition script source file {SCRIPT_FILE} is missing from "
        "the environment image."
    )


def test_wmill_workspace_authenticated():
    # `wmill workspace whoami` succeeds (exit code 0) only when a workspace is
    # configured and the stored token can authenticate against the remote.
    result = subprocess.run(
        ["wmill", "workspace", "whoami"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        "Expected `wmill workspace whoami` to succeed after the bootstrap fixture "
        "configured a Windmill Cloud workspace. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_pre_deployed_script_exists_on_workspace():
    # Use the CLI to confirm that the pre-deployed script at `f/zealt_eval/add_numbers`
    # is reachable from the active workspace.
    result = subprocess.run(
        ["wmill", "script", "show", SCRIPT_PATH],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Expected the pre-deployed Windmill script at `{SCRIPT_PATH}` to be "
        "accessible from the current workspace, but `wmill script show` failed. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_json_module_available():
    # Sanity check that the verifier can parse JSON results.
    parsed = json.loads("42")
    assert parsed == 42, "Python's `json` module must be available for verification."
