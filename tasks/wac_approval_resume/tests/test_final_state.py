"""Final-state verification for the windmill WAC approval/resume task.

The agent has authored a Workflows-as-Code TypeScript script at
``f/eval/deploy_pipeline_<RUN_ID>.ts`` inside ``/home/user/wac-pipeline`` and
deployed it to the shared cloud Windmill workspace. This module:

1. Asserts the on-disk script file and log file exist and have the required
   structural content.
2. Calls the Windmill HTTP API to confirm the script has been deployed.
3. Resets the counter variable, triggers the workflow asynchronously, polls
   for the suspended checkpoint, resumes it via
   ``/jobs_u/flow/resume_suspended/{id}`` with ``{"approved": true}``, polls
   for completion, and asserts the final result deep-equals
   ``["tests-ran", "staging-deployed", "production-deployed"]``.
4. Asserts the counter variable equals ``"1"`` after completion, proving the
   checkpoint/replay semantics did not re-execute ``runTests``.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any

import pytest
import requests


PROJECT_DIR = "/home/user/wac-pipeline"
WINDMILL_BASE_URL = "https://app.windmill.dev"

POLL_INTERVAL_S = 2.0
SUSPEND_POLL_TIMEOUT_S = 180.0
COMPLETE_POLL_TIMEOUT_S = 180.0
HTTP_TIMEOUT_S = 60.0


# -----------------------------
# Environment / config helpers
# -----------------------------


def _run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "").strip()
    assert rid, "ZEALT_RUN_ID environment variable must be set."
    return rid


def _token() -> str:
    t = os.environ.get("WINDMILL_TOKEN", "").strip()
    assert t, "WINDMILL_TOKEN environment variable must be set."
    return t


def _workspace() -> str:
    w = os.environ.get("WINDMILL_WORKSPACE", "").strip()
    assert w, "WINDMILL_WORKSPACE environment variable must be set."
    return w


def _auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }


def _script_path(run_id: str) -> str:
    return f"f/eval/deploy_pipeline_{run_id}"


def _counter_path(run_id: str) -> str:
    return f"f/eval/runtests_counter_{run_id}"


# -----------------------------
# Local artifact tests
# -----------------------------


def test_local_script_file_contains_required_constructs() -> None:
    run_id = _run_id()
    script_file = os.path.join(
        PROJECT_DIR, "f", "eval", f"deploy_pipeline_{run_id}.ts"
    )
    assert os.path.isfile(script_file), (
        f"Expected the agent to have authored {script_file}, but it does not exist."
    )
    with open(script_file, "r", encoding="utf-8") as fh:
        content = fh.read()

    required_substrings = [
        "workflow(",
        'step("runTests"',
        'step("deployStaging"',
        "waitForApproval(",
        'step("deployProduction"',
    ]
    for needle in required_substrings:
        assert needle in content, (
            f"Required substring {needle!r} not found in {script_file}. "
            "The WAC script must contain all five checkpoints / wrappers."
        )


def test_output_log_contains_expected_lines() -> None:
    run_id = _run_id()
    log_path = os.path.join(PROJECT_DIR, "output.log")
    assert os.path.isfile(log_path), f"Expected log file {log_path} to exist."

    with open(log_path, "r", encoding="utf-8") as fh:
        log = fh.read()

    expected_script_line = f"Script path: f/eval/deploy_pipeline_{run_id}"
    expected_var_line = f"Counter variable: f/eval/runtests_counter_{run_id}"
    assert expected_script_line in log, (
        f"Expected line {expected_script_line!r} in {log_path}, got:\n{log}"
    )
    assert expected_var_line in log, (
        f"Expected line {expected_var_line!r} in {log_path}, got:\n{log}"
    )


# -----------------------------
# Windmill HTTP helpers
# -----------------------------


def _get_script_metadata(workspace: str, path: str) -> requests.Response:
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/scripts/get/p/{path}"
    return requests.get(url, headers=_auth_headers(), timeout=HTTP_TIMEOUT_S)


def _variable_exists(workspace: str, path: str) -> bool:
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/variables/get/{path}"
    resp = requests.get(url, headers=_auth_headers(), timeout=HTTP_TIMEOUT_S)
    return resp.status_code == 200


def _set_counter_variable_to_zero(workspace: str, path: str) -> None:
    """Ensure the counter variable exists and equals the string "0"."""
    if _variable_exists(workspace, path):
        update_url = (
            f"{WINDMILL_BASE_URL}/api/w/{workspace}/variables/update/{path}"
        )
        resp = requests.post(
            update_url,
            headers=_auth_headers(),
            data=json.dumps({"value": "0"}),
            timeout=HTTP_TIMEOUT_S,
        )
        assert resp.status_code in (200, 201), (
            f"Failed to update {path} to '0': "
            f"status={resp.status_code} body={resp.text[:300]!r}"
        )
    else:
        create_url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/variables/create"
        body = {
            "path": path,
            "value": "0",
            "is_secret": False,
            "description": "windmill WAC approval/resume eval counter",
        }
        resp = requests.post(
            create_url,
            headers=_auth_headers(),
            data=json.dumps(body),
            timeout=HTTP_TIMEOUT_S,
        )
        assert resp.status_code in (200, 201), (
            f"Failed to create {path}: "
            f"status={resp.status_code} body={resp.text[:300]!r}"
        )


def _get_variable_value(workspace: str, path: str) -> str:
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/variables/get/{path}"
    resp = requests.get(url, headers=_auth_headers(), timeout=HTTP_TIMEOUT_S)
    assert resp.status_code == 200, (
        f"Failed to GET variable {path}: status={resp.status_code} body={resp.text[:300]!r}"
    )
    data = resp.json()
    # The Windmill API returns the variable object; the actual value lives in
    # the "value" field for non-secret variables.
    assert "value" in data, (
        f"Variable {path} response missing 'value' field: {data!r}"
    )
    return str(data["value"])


def _trigger_workflow_async(workspace: str, path: str) -> str:
    url = (
        f"{WINDMILL_BASE_URL}/api/w/{workspace}/jobs/run/p/{path}"
    )
    resp = requests.post(
        url,
        headers=_auth_headers(),
        data=json.dumps({}),
        timeout=HTTP_TIMEOUT_S,
    )
    assert resp.status_code in (200, 201), (
        f"Async trigger failed for {path}: "
        f"status={resp.status_code} body={resp.text[:300]!r}"
    )
    job_id = resp.text.strip().strip('"')
    assert re.fullmatch(r"[0-9a-fA-F-]{36}", job_id), (
        f"Expected a UUID job id from async trigger, got {job_id!r}"
    )
    return job_id


def _get_job_state(workspace: str, job_id: str) -> dict[str, Any]:
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/jobs_u/get/{job_id}"
    resp = requests.get(url, headers=_auth_headers(), timeout=HTTP_TIMEOUT_S)
    assert resp.status_code == 200, (
        f"Failed to GET job {job_id}: status={resp.status_code} body={resp.text[:300]!r}"
    )
    return resp.json()


def _is_suspended(job: dict[str, Any]) -> bool:
    """Detect whether the WAC job is currently suspended waiting for approval.

    The Windmill job representation evolves across versions, so we tolerate a
    few possible signals:

    - A boolean ``suspend`` field that is truthy.
    - A ``flow_status`` whose ``step`` matches the approval checkpoint and
      whose ``modules`` show the current module in a ``WaitingForEvents`` /
      ``Suspended`` state.
    - Any top-level ``type`` containing the word "suspend".
    """
    if not isinstance(job, dict):
        return False
    if job.get("suspend") and job.get("type") != "CompletedJob":
        return True

    job_type = str(job.get("type", "")).lower()
    if "suspend" in job_type:
        return True

    flow_status = job.get("flow_status")
    if isinstance(flow_status, dict):
        modules = flow_status.get("modules", [])
        if isinstance(modules, list):
            for mod in modules:
                if not isinstance(mod, dict):
                    continue
                mod_type = str(mod.get("type", "")).lower()
                if mod_type in (
                    "waitingforevents",
                    "waitingforexecutor",
                    "suspended",
                ):
                    if "suspend" in mod_type or "waitingforevents" in mod_type:
                        return True
                if mod.get("suspend"):
                    return True
    return False


def _is_completed(job: dict[str, Any]) -> bool:
    if not isinstance(job, dict):
        return False
    if str(job.get("type", "")) == "CompletedJob":
        return True
    # Some Windmill responses use a boolean "completed" or "running" field
    if job.get("completed") is True:
        return True
    return False


def _poll_until(
    workspace: str,
    job_id: str,
    predicate,
    timeout_s: float,
    interval_s: float = POLL_INTERVAL_S,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    last_state: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last_state = _get_job_state(workspace, job_id)
        if predicate(last_state):
            return last_state
        time.sleep(interval_s)
    raise AssertionError(
        f"Timed out after {timeout_s}s waiting for job {job_id}. "
        f"Last observed state keys={list(last_state.keys())[:20]} "
        f"type={last_state.get('type')!r} suspend={last_state.get('suspend')!r}"
    )


def _resume_suspended(workspace: str, job_id: str) -> None:
    url = (
        f"{WINDMILL_BASE_URL}/api/w/{workspace}/jobs_u/flow/resume_suspended/{job_id}"
    )
    resp = requests.post(
        url,
        headers=_auth_headers(),
        data=json.dumps({"approved": True}),
        timeout=HTTP_TIMEOUT_S,
    )
    assert resp.status_code in (200, 201, 204), (
        f"resume_suspended call failed: "
        f"status={resp.status_code} body={resp.text[:300]!r}"
    )


def _get_completed_result(workspace: str, job_id: str) -> Any:
    url = (
        f"{WINDMILL_BASE_URL}/api/w/{workspace}/jobs_u/completed/get_result/{job_id}"
    )
    resp = requests.get(url, headers=_auth_headers(), timeout=HTTP_TIMEOUT_S)
    assert resp.status_code == 200, (
        f"Failed to GET completed result for {job_id}: "
        f"status={resp.status_code} body={resp.text[:300]!r}"
    )
    # The endpoint returns the raw JSON result (which can be any JSON value).
    return resp.json()


# -----------------------------
# Tests
# -----------------------------


def test_script_is_deployed_to_workspace() -> None:
    workspace = _workspace()
    run_id = _run_id()
    path = _script_path(run_id)
    resp = _get_script_metadata(workspace, path)
    assert resp.status_code == 200, (
        f"Expected the deployed script at {path} to be retrievable, "
        f"but got status={resp.status_code} body={resp.text[:300]!r}"
    )
    body = resp.json()
    language = str(body.get("language", "")).lower()
    assert language == "bun", (
        f"Expected deployed script language to be 'bun', got {language!r}."
    )


@pytest.fixture(scope="session")
def workflow_run_artifacts() -> dict[str, Any]:
    """Run the end-to-end async-trigger / suspend / resume / complete flow once."""
    workspace = _workspace()
    run_id = _run_id()
    script_path = _script_path(run_id)
    counter_path = _counter_path(run_id)

    # The script must be deployed before we can run it.
    metadata = _get_script_metadata(workspace, script_path)
    if metadata.status_code != 200:
        pytest.fail(
            f"Cannot run end-to-end tests: script {script_path} is not deployed "
            f"(status={metadata.status_code} body={metadata.text[:300]!r})."
        )

    # Pre-seed the counter variable to "0" for deterministic behaviour.
    _set_counter_variable_to_zero(workspace, counter_path)

    job_id = _trigger_workflow_async(workspace, script_path)

    suspended_state = _poll_until(
        workspace, job_id, _is_suspended, SUSPEND_POLL_TIMEOUT_S
    )

    _resume_suspended(workspace, job_id)

    completed_state = _poll_until(
        workspace, job_id, _is_completed, COMPLETE_POLL_TIMEOUT_S
    )

    result = _get_completed_result(workspace, job_id)
    counter_value = _get_variable_value(workspace, counter_path)

    return {
        "job_id": job_id,
        "suspended_state": suspended_state,
        "completed_state": completed_state,
        "result": result,
        "counter_value": counter_value,
    }


def test_workflow_reached_suspended_state(workflow_run_artifacts: dict[str, Any]) -> None:
    suspended_state = workflow_run_artifacts["suspended_state"]
    assert _is_suspended(suspended_state), (
        "Expected the workflow job to have reached a suspended state before resume; "
        f"got state with type={suspended_state.get('type')!r} suspend={suspended_state.get('suspend')!r}"
    )


def test_workflow_completed_successfully(workflow_run_artifacts: dict[str, Any]) -> None:
    completed_state = workflow_run_artifacts["completed_state"]
    assert str(completed_state.get("type")) == "CompletedJob", (
        f"Expected job to be CompletedJob, got type={completed_state.get('type')!r}"
    )
    success_field = completed_state.get("success")
    assert success_field is True, (
        f"Expected the completed job to have success=true, got success={success_field!r}"
    )


def test_workflow_result_audit_array(workflow_run_artifacts: dict[str, Any]) -> None:
    result = workflow_run_artifacts["result"]
    expected = ["tests-ran", "staging-deployed", "production-deployed"]
    assert result == expected, (
        "Final workflow result must deep-equal "
        f"{expected!r}; got {result!r}. This is the proof that the three "
        "checkpoints ran in order and that the early steps were not "
        "re-executed during the resume."
    )


def test_runtests_counter_is_one(workflow_run_artifacts: dict[str, Any]) -> None:
    counter_value = workflow_run_artifacts["counter_value"]
    assert counter_value == "1", (
        f"Expected runTests counter variable to equal '1' after the run, but got "
        f"{counter_value!r}. A value > 1 would indicate that the runTests step "
        "side-effect was re-executed on replay (replay semantics violation)."
    )
