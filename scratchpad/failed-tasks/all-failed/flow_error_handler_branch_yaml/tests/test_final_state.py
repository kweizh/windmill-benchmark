import os
import re

import pytest
import requests
import yaml


PROJECT_DIR = "/home/user/myproject"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID must be set in the verifier environment."
    return run_id


def _base_url() -> str:
    base = os.environ.get("WMILL_BASE_URL", "").rstrip("/")
    assert base, "WMILL_BASE_URL must be set."
    return base


def _workspace() -> str:
    ws = os.environ.get("WMILL_WORKSPACE", "")
    assert ws, "WMILL_WORKSPACE must be set."
    return ws


def _token() -> str:
    tok = os.environ.get("WMILL_TOKEN", "")
    assert tok, "WMILL_TOKEN must be set."
    return tok


def _remote_flow_path() -> str:
    return f"f/zealt/err_handler_{_run_id()}"


def _local_flow_yaml_path() -> str:
    return os.path.join(
        PROJECT_DIR, "f", "zealt", f"err_handler_{_run_id()}.flow", "flow.yaml"
    )


@pytest.fixture(scope="session")
def auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }


def test_local_flow_yaml_exists():
    path = _local_flow_yaml_path()
    assert os.path.isfile(path), (
        f"Expected the flow YAML at {path}; the agent must persist the flow as a "
        f"local .flow.yaml file before deploying it."
    )


def test_local_flow_yaml_uses_failure_module_keyword():
    path = _local_flow_yaml_path()
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    # The documented OpenFlow error-handler keyword is `failure_module`.
    assert re.search(r"\bfailure_module\b", text), (
        f"The local flow YAML at {path} must use the documented OpenFlow error-handler "
        f"keyword `failure_module`. Found content did not include that keyword."
    )


def test_flow_is_deployed_with_failure_module(auth_headers):
    url = f"{_base_url()}/api/w/{_workspace()}/flows/get/{_remote_flow_path()}"
    resp = requests.get(url, headers=auth_headers, timeout=30)
    assert resp.status_code == 200, (
        f"Expected GET {url} to return 200 once the flow is deployed, "
        f"got {resp.status_code}: {resp.text[:500]}"
    )
    body = resp.json()
    value = body.get("value") or {}
    assert "failure_module" in value, (
        "Expected the deployed flow's `value` object to contain a `failure_module` entry. "
        f"Got keys: {sorted(value.keys())}"
    )
    # Sanity-check it isn't an empty placeholder.
    fm = value["failure_module"]
    assert isinstance(fm, dict) and fm, (
        f"Expected `failure_module` to be a non-empty object, got: {fm!r}"
    )


def test_running_flow_with_failure_returns_handled_payload(auth_headers):
    url = (
        f"{_base_url()}/api/w/{_workspace()}/jobs/run_wait_result/f/"
        f"{_remote_flow_path()}"
    )
    resp = requests.post(
        url,
        headers=auth_headers,
        json={"should_fail": True},
        timeout=120,
    )
    assert resp.status_code == 200, (
        f"Expected POST {url} with body {{'should_fail': true}} to return 200, "
        f"got {resp.status_code}: {resp.text[:500]}"
    )
    try:
        payload = resp.json()
    except ValueError as exc:
        pytest.fail(
            f"Expected the flow result to be valid JSON; got non-JSON body "
            f"({exc}): {resp.text[:500]}"
        )

    assert isinstance(payload, dict), (
        f"Expected flow result to be a JSON object, got: {type(payload).__name__} -> {payload!r}"
    )
    assert payload.get("handled") is True, (
        f"Expected flow result to include `handled: true`, got: {payload!r}"
    )
    reason = payload.get("reason")
    assert isinstance(reason, str) and reason.strip(), (
        f"Expected flow result to include `reason` as a non-empty string, got: {reason!r}"
    )


def test_local_yaml_parses_as_openflow(auth_headers):
    # Defensive parse: confirm the local YAML is well-formed and contains
    # `value.failure_module` (mirrors what the deployed flow exposes).
    path = _local_flow_yaml_path()
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    assert isinstance(doc, dict), f"Local flow YAML at {path} must parse as a mapping."
    value = doc.get("value")
    assert isinstance(value, dict), (
        f"Local flow YAML at {path} must have a top-level `value` mapping per the OpenFlow spec."
    )
    assert "failure_module" in value, (
        f"Local flow YAML at {path} must declare `value.failure_module` as the error handler."
    )
