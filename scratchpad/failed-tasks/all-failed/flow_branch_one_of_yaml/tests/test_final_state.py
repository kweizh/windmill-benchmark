import os
import re

import pytest
import requests
import yaml

PROJECT_DIR = "/home/user/myproject"
FLOW_YAML_PATH = os.path.join(PROJECT_DIR, "flow.yaml")
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")


def _env(name: str) -> str:
    val = os.environ.get(name)
    assert val, f"Required environment variable {name} is not set."
    return val


@pytest.fixture(scope="session")
def run_id() -> str:
    return _env("ZEALT_RUN_ID")


@pytest.fixture(scope="session")
def remote_flow_path(run_id: str) -> str:
    return f"f/zealt/branch_one_{run_id}"


@pytest.fixture(scope="session")
def wm_base_url() -> str:
    return _env("WM_BASE_URL").rstrip("/")


@pytest.fixture(scope="session")
def wm_workspace() -> str:
    return _env("WM_WORKSPACE")


@pytest.fixture(scope="session")
def wm_headers() -> dict:
    token = _env("WM_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def test_flow_yaml_exists():
    assert os.path.isfile(FLOW_YAML_PATH), (
        f"Expected flow YAML file at {FLOW_YAML_PATH} but it was not created."
    )


def test_flow_yaml_uses_branchone_with_two_branches():
    with open(FLOW_YAML_PATH) as f:
        doc = yaml.safe_load(f)

    assert isinstance(doc, dict), (
        f"{FLOW_YAML_PATH} must be a YAML mapping at the top level."
    )

    value = doc.get("value")
    assert isinstance(value, dict), (
        "Top-level OpenFlow document must contain a `value` mapping describing the "
        "flow logic."
    )

    modules = value.get("modules")
    assert isinstance(modules, list) and len(modules) >= 1, (
        "`value.modules` must be a non-empty list."
    )

    branchone_modules = []
    for module in modules:
        if not isinstance(module, dict):
            continue
        mvalue = module.get("value")
        if isinstance(mvalue, dict) and mvalue.get("type") == "branchone":
            branchone_modules.append(mvalue)

    assert len(branchone_modules) == 1, (
        "Expected exactly one module of type `branchone` in `value.modules`, "
        f"found {len(branchone_modules)}."
    )

    branches = branchone_modules[0].get("branches")
    assert isinstance(branches, list) and len(branches) == 2, (
        "The branchone module must define exactly 2 branches in its `branches` list."
    )

    for idx, branch in enumerate(branches):
        assert isinstance(branch, dict), f"Branch at index {idx} must be a mapping."
        expr = branch.get("expr")
        assert isinstance(expr, str) and expr.strip(), (
            f"Branch at index {idx} must define a non-empty `expr` predicate string."
        )


def test_log_file_records_flow_path(run_id: str, remote_flow_path: str):
    assert os.path.isfile(LOG_PATH), (
        f"Expected log file at {LOG_PATH} containing the deployed flow path."
    )
    with open(LOG_PATH) as f:
        log = f.read()
    pattern = rf"^Flow path: {re.escape(remote_flow_path)}$"
    assert re.search(pattern, log, flags=re.MULTILINE), (
        f"Expected log file {LOG_PATH} to contain a line matching "
        f"'Flow path: {remote_flow_path}'. Got:\n{log}"
    )


def test_flow_deployed_to_workspace(
    wm_base_url: str, wm_workspace: str, wm_headers: dict, remote_flow_path: str
):
    url = f"{wm_base_url}/api/w/{wm_workspace}/flows/get/{remote_flow_path}"
    response = requests.get(url, headers=wm_headers, timeout=30)
    assert response.status_code == 200, (
        f"Expected GET {url} to return 200 confirming the flow is deployed, "
        f"got {response.status_code}: {response.text}"
    )

    data = response.json()
    value = data.get("value")
    assert isinstance(value, dict), (
        "Deployed flow response is missing the `value` field describing the flow."
    )
    modules = value.get("modules")
    assert isinstance(modules, list) and modules, (
        "Deployed flow `value.modules` must be a non-empty list."
    )

    branchone_modules = [
        m.get("value")
        for m in modules
        if isinstance(m, dict)
        and isinstance(m.get("value"), dict)
        and m["value"].get("type") == "branchone"
    ]
    assert len(branchone_modules) == 1, (
        "Deployed flow must contain exactly one branchone module, "
        f"found {len(branchone_modules)}."
    )

    branches = branchone_modules[0].get("branches")
    assert isinstance(branches, list) and len(branches) == 2, (
        "Deployed branchone module must define exactly 2 branches."
    )


def _run_flow_wait_result(
    wm_base_url: str, wm_workspace: str, wm_headers: dict, remote_flow_path: str, payload: dict
):
    url = (
        f"{wm_base_url}/api/w/{wm_workspace}/jobs/run_wait_result/{remote_flow_path}"
    )
    response = requests.post(url, headers=wm_headers, json=payload, timeout=120)
    assert response.status_code == 200, (
        f"Expected POST {url} with payload {payload} to return 200, "
        f"got {response.status_code}: {response.text}"
    )
    try:
        return response.json()
    except ValueError:
        pytest.fail(
            f"Flow run result for payload {payload} is not valid JSON: {response.text}"
        )


def test_flow_route_a_returns_branch_a_constant(
    wm_base_url: str, wm_workspace: str, wm_headers: dict, remote_flow_path: str
):
    result = _run_flow_wait_result(
        wm_base_url, wm_workspace, wm_headers, remote_flow_path, {"route": "a"}
    )
    assert result == "branch_a_route", (
        "Running the deployed flow with route='a' must return the exact string "
        f"'branch_a_route', got: {result!r}"
    )


def test_flow_route_b_returns_branch_b_constant(
    wm_base_url: str, wm_workspace: str, wm_headers: dict, remote_flow_path: str
):
    result = _run_flow_wait_result(
        wm_base_url, wm_workspace, wm_headers, remote_flow_path, {"route": "b"}
    )
    assert result == "branch_b_route", (
        "Running the deployed flow with route='b' must return the exact string "
        f"'branch_b_route', got: {result!r}"
    )
