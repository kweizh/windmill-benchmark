import json
import os
import re

import pytest
import requests
import yaml

PROJECT_DIR = "/home/user/wmill-project"
FLOW_FILE = os.path.join(PROJECT_DIR, "two_step_flow.flow", "flow.yaml")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
BASE_URL = "https://app.windmill.dev"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _remote_flow_path() -> str:
    return f"f/zealt/two_step_flow_{_run_id()}"


def _headers() -> dict:
    token = os.environ.get("WMILL_TOKEN", "")
    assert token, "WMILL_TOKEN environment variable is not set."
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _workspace() -> str:
    ws = os.environ.get("WMILL_WORKSPACE", "")
    assert ws, "WMILL_WORKSPACE environment variable is not set."
    return ws


@pytest.fixture(scope="module")
def flow_yaml() -> dict:
    assert os.path.isfile(FLOW_FILE), (
        f"Expected flow file at {FLOW_FILE} but it does not exist."
    )
    with open(FLOW_FILE) as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), (
        f"Flow YAML at {FLOW_FILE} must parse to a mapping; got {type(data).__name__}."
    )
    return data


def test_flow_yaml_has_summary(flow_yaml: dict):
    assert isinstance(flow_yaml.get("summary"), str) and flow_yaml["summary"].strip(), (
        "Flow YAML must contain a non-empty top-level 'summary' string."
    )


def test_flow_yaml_has_two_rawscript_modules(flow_yaml: dict):
    value = flow_yaml.get("value")
    assert isinstance(value, dict), "Flow YAML must contain a top-level 'value' mapping."
    modules = value.get("modules")
    assert isinstance(modules, list), "'value.modules' must be a list."
    assert len(modules) == 2, (
        f"Expected exactly 2 modules in the flow, got {len(modules)}."
    )
    ids = []
    for idx, mod in enumerate(modules):
        assert isinstance(mod, dict), f"Module #{idx} must be a mapping."
        mod_id = mod.get("id")
        assert isinstance(mod_id, str) and mod_id.strip(), (
            f"Module #{idx} must have a non-empty string 'id'."
        )
        ids.append(mod_id)
        mod_value = mod.get("value")
        assert isinstance(mod_value, dict), (
            f"Module '{mod_id}' must have a 'value' mapping."
        )
        assert mod_value.get("type") == "rawscript", (
            f"Module '{mod_id}' must have value.type == 'rawscript'; got {mod_value.get('type')!r}."
        )
    assert len(set(ids)) == 2, f"Module ids must be distinct; got {ids}."


def test_second_module_input_transforms_reference_first(flow_yaml: dict):
    modules = flow_yaml["value"]["modules"]
    first_id = modules[0]["id"]
    second_module_value = modules[1]["value"]
    input_transforms = second_module_value.get("input_transforms")
    assert isinstance(input_transforms, dict) and input_transforms, (
        "Second module must have a non-empty 'input_transforms' mapping."
    )
    pattern = re.compile(rf"\bresults\.{re.escape(first_id)}\b")
    matching = []
    for param_name, transform in input_transforms.items():
        if not isinstance(transform, dict):
            continue
        if transform.get("type") != "javascript":
            continue
        expr = transform.get("expr", "")
        if isinstance(expr, str) and pattern.search(expr):
            matching.append(param_name)
    assert matching, (
        f"Second module's input_transforms must contain a 'javascript' transform whose expr "
        f"references the first module via the 'results.{first_id}' pattern. "
        f"Got input_transforms={input_transforms!r}."
    )


def test_flow_schema_declares_x_input(flow_yaml: dict):
    schema = flow_yaml.get("schema")
    assert isinstance(schema, dict), "Flow YAML must declare a top-level 'schema' mapping."
    properties = schema.get("properties")
    assert isinstance(properties, dict), "schema.properties must be a mapping."
    assert "x" in properties, (
        f"Flow input schema must declare a property named 'x'; got properties={list(properties.keys())}."
    )


def test_log_file_contents():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE) as f:
        content = f.read()
    expected_flow_line = f"Flow path: {_remote_flow_path()}"
    assert expected_flow_line in content, (
        f"Log file must contain a line exactly matching '{expected_flow_line}'. "
        f"Got:\n{content}"
    )
    assert "Final result: 9" in content, (
        f"Log file must contain a line exactly matching 'Final result: 9'. Got:\n{content}"
    )


def test_flow_deployed_to_remote_path():
    remote_path = _remote_flow_path()
    url = f"{BASE_URL}/api/w/{_workspace()}/flows/get/{remote_path}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    assert resp.status_code == 200, (
        f"Expected the flow at '{remote_path}' to be deployed (HTTP 200), "
        f"got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    modules = body.get("value", {}).get("modules", [])
    assert isinstance(modules, list) and len(modules) == 2, (
        f"Deployed flow must contain exactly 2 modules; got {len(modules)}."
    )


def test_flow_run_returns_expected_result():
    remote_path = _remote_flow_path()
    url = f"{BASE_URL}/api/w/{_workspace()}/jobs/run_wait_result/f/{remote_path}"
    resp = requests.post(
        url,
        headers=_headers(),
        data=json.dumps({"x": 4}),
        timeout=120,
    )
    assert resp.status_code == 200, (
        f"Running the deployed flow with {{'x': 4}} must return HTTP 200; "
        f"got {resp.status_code}: {resp.text}"
    )
    try:
        result = resp.json()
    except ValueError:
        pytest.fail(f"Flow run response was not valid JSON: {resp.text!r}")
    assert result == 9, (
        f"Running the deployed flow with input {{'x': 4}} must return 9 "
        f"(first step doubles x to 8, second step adds 1); got {result!r}."
    )
