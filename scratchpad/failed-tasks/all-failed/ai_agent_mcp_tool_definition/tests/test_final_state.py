import json
import os
import re
import time
from typing import Any, Dict, Optional, Tuple

import pytest
import requests
from jsonschema import Draft202012Validator


WMILL_BASE_URL = "https://app.windmill.dev"
PROJECT_DIR = "/home/user/wm-agent"
DEPLOY_LOG_PATH = os.path.join(PROJECT_DIR, "deploy.log")


# ---------- Fixtures ----------


@pytest.fixture(scope="session")
def wmill_token() -> str:
    token = os.environ.get("WMILL_TOKEN", "")
    assert token, "WMILL_TOKEN is not set in the verifier environment."
    return token


@pytest.fixture(scope="session")
def wmill_workspace() -> str:
    ws = os.environ.get("WMILL_WORKSPACE", "")
    assert ws, "WMILL_WORKSPACE is not set in the verifier environment."
    return ws


@pytest.fixture(scope="session")
def run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "")
    assert rid, "ZEALT_RUN_ID is not set in the verifier environment."
    return rid


@pytest.fixture(scope="session")
def deploy_log_paths(run_id: str) -> Tuple[str, str]:
    assert os.path.isfile(DEPLOY_LOG_PATH), (
        f"Expected deploy log file at {DEPLOY_LOG_PATH} but it does not exist."
    )
    with open(DEPLOY_LOG_PATH, "r", encoding="utf-8") as fh:
        text = fh.read()

    tool_match = re.search(r"^Tool script path:\s*(\S+)\s*$", text, re.MULTILINE)
    flow_match = re.search(r"^Flow path:\s*(\S+)\s*$", text, re.MULTILINE)

    assert tool_match, (
        f"deploy.log is missing a 'Tool script path: <path>' line. Content was:\n{text}"
    )
    assert flow_match, (
        f"deploy.log is missing a 'Flow path: <path>' line. Content was:\n{text}"
    )

    tool_path = tool_match.group(1).strip()
    flow_path = flow_match.group(1).strip()

    expected_prefix = f"f/agent_{run_id}/"
    assert tool_path.startswith(expected_prefix), (
        f"Tool script path '{tool_path}' must begin with '{expected_prefix}' "
        f"to be parallel-run safe."
    )
    assert flow_path.startswith(expected_prefix), (
        f"Flow path '{flow_path}' must begin with '{expected_prefix}' "
        f"to be parallel-run safe."
    )

    return tool_path, flow_path


@pytest.fixture(scope="session")
def fetched_flow(
    deploy_log_paths: Tuple[str, str],
    wmill_token: str,
    wmill_workspace: str,
) -> Dict[str, Any]:
    _, flow_path = deploy_log_paths
    url = f"{WMILL_BASE_URL}/api/w/{wmill_workspace}/flows/get/{flow_path}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {wmill_token}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"Failed to fetch deployed flow at {flow_path}: "
        f"HTTP {resp.status_code} - {resp.text[:500]}"
    )
    body = resp.json()
    assert isinstance(body, dict), (
        f"Unexpected flow GET response shape (not a dict): {body!r}"
    )
    return body


# ---------- Helpers ----------


def _get_modules(flow: Dict[str, Any]) -> list:
    value = flow.get("value")
    assert isinstance(value, dict), (
        f"Flow 'value' must be an object, got: {type(value).__name__}"
    )
    modules = value.get("modules")
    assert isinstance(modules, list) and modules, (
        "Flow 'value.modules' must be a non-empty list."
    )
    return modules


def _get_first_module_value(flow: Dict[str, Any]) -> Dict[str, Any]:
    modules = _get_modules(flow)
    first = modules[0]
    assert isinstance(first, dict), "First module entry must be an object."
    mod_value = first.get("value")
    assert isinstance(mod_value, dict), (
        "First module's 'value' must be an object describing the step."
    )
    return mod_value


def _extract_static(transform: Any) -> Optional[Any]:
    """Return the value of a static InputTransform, or None if not static."""
    if not isinstance(transform, dict):
        return None
    if transform.get("type") != "static":
        return None
    return transform.get("value")


# ---------- Tests ----------


def test_first_module_is_aiagent(fetched_flow: Dict[str, Any]) -> None:
    mod_value = _get_first_module_value(fetched_flow)
    assert mod_value.get("type") == "aiagent", (
        "The first flow module must be an AI Agent step "
        f"(value.type == 'aiagent'); got value.type={mod_value.get('type')!r}."
    )


def test_aiagent_tools_reference_deployed_tool(
    fetched_flow: Dict[str, Any],
    deploy_log_paths: Tuple[str, str],
) -> None:
    tool_path, _ = deploy_log_paths
    mod_value = _get_first_module_value(fetched_flow)
    tools = mod_value.get("tools")
    assert isinstance(tools, list) and tools, (
        "AI Agent step must have a non-empty 'tools' array."
    )

    found_reference = False
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        value = tool.get("value")
        if not isinstance(value, dict):
            continue
        tool_type = value.get("tool_type")
        if tool_type == "flowmodule":
            inner_type = value.get("type")
            inner_path = value.get("path")
            if inner_type == "script" and inner_path == tool_path:
                found_reference = True
                break
        elif tool_type == "mcp":
            resource_path = value.get("resource_path")
            if isinstance(resource_path, str) and resource_path:
                # Alternate documented form (MCP entry). Accepted.
                found_reference = True
                break

    assert found_reference, (
        "The AI Agent step's tools array must include either a flowmodule "
        f"script tool referencing '{tool_path}' or an MCP tool entry with a "
        f"non-empty 'resource_path'. Got tools={tools!r}"
    )


def test_output_schema_defined_with_required_fields(
    fetched_flow: Dict[str, Any],
) -> None:
    mod_value = _get_first_module_value(fetched_flow)
    input_transforms = mod_value.get("input_transforms")
    assert isinstance(input_transforms, dict), (
        "AI Agent step must define 'input_transforms' as an object."
    )
    output_schema_transform = input_transforms.get("output_schema")
    assert output_schema_transform is not None, (
        "AI Agent step must declare 'input_transforms.output_schema' to enforce "
        "structured output."
    )
    schema_value = _extract_static(output_schema_transform)
    assert isinstance(schema_value, dict), (
        "'input_transforms.output_schema' must be a static transform whose value "
        "is a JSON Schema object; got: "
        f"{output_schema_transform!r}"
    )

    # Validate the schema is itself a valid JSON Schema.
    try:
        Draft202012Validator.check_schema(schema_value)
    except Exception as exc:
        pytest.fail(
            f"Declared output_schema is not a valid JSON Schema: {exc}\n"
            f"Schema was: {json.dumps(schema_value)[:500]}"
        )

    properties = schema_value.get("properties")
    assert isinstance(properties, dict), (
        "output_schema must declare 'properties'."
    )

    def _type_of(prop_name: str) -> Optional[str]:
        prop = properties.get(prop_name)
        if not isinstance(prop, dict):
            return None
        t = prop.get("type")
        if isinstance(t, list):
            for entry in t:
                if isinstance(entry, str) and entry != "null":
                    return entry
            return None
        return t if isinstance(t, str) else None

    assert _type_of("sku") == "string", (
        f"output_schema.properties.sku must declare type 'string'; got: "
        f"{properties.get('sku')!r}"
    )
    assert _type_of("unit_price") in ("number", "integer"), (
        f"output_schema.properties.unit_price must declare type 'number' "
        f"(or 'integer'); got: {properties.get('unit_price')!r}"
    )
    assert _type_of("currency") == "string", (
        f"output_schema.properties.currency must declare type 'string'; got: "
        f"{properties.get('currency')!r}"
    )


def test_tool_script_is_deployed(
    deploy_log_paths: Tuple[str, str],
    wmill_token: str,
    wmill_workspace: str,
) -> None:
    tool_path, _ = deploy_log_paths
    url = (
        f"{WMILL_BASE_URL}/api/w/{wmill_workspace}/scripts/get/{tool_path}"
    )
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {wmill_token}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"Tool script {tool_path} is not reachable on the cloud workspace: "
        f"HTTP {resp.status_code} - {resp.text[:500]}"
    )


def test_invoking_agent_returns_schema_conformant_payload(
    fetched_flow: Dict[str, Any],
    deploy_log_paths: Tuple[str, str],
    wmill_token: str,
    wmill_workspace: str,
) -> None:
    _, flow_path = deploy_log_paths
    mod_value = _get_first_module_value(fetched_flow)
    output_schema = _extract_static(
        mod_value.get("input_transforms", {}).get("output_schema")
    )
    assert isinstance(output_schema, dict), (
        "Cannot validate agent output without a static output_schema."
    )

    invoke_url = (
        f"{WMILL_BASE_URL}/api/w/{wmill_workspace}"
        f"/jobs/run_wait_result/f/{flow_path}"
    )
    payload = {
        "prompt": (
            "Look up the unit price for SKU WIDGET-42 and reply with the "
            "structured answer."
        )
    }

    # Allow a generous timeout for cold-start + LLM round-trip.
    last_status = None
    last_text = ""
    body: Any = None
    deadline = time.time() + 240
    while time.time() < deadline:
        try:
            resp = requests.post(
                invoke_url,
                headers={
                    "Authorization": f"Bearer {wmill_token}",
                    "Content-Type": "application/json",
                },
                data=json.dumps(payload),
                timeout=200,
            )
            last_status = resp.status_code
            last_text = resp.text
            if resp.status_code == 200:
                try:
                    body = resp.json()
                except ValueError:
                    body = None
                break
        except requests.exceptions.RequestException as exc:
            last_text = f"request error: {exc}"
        time.sleep(2)

    assert last_status == 200, (
        f"Invoking the AI Agent flow at {flow_path} did not return HTTP 200. "
        f"Last status={last_status}, body snippet={last_text[:500]}"
    )
    assert body is not None, (
        f"Invocation succeeded with status 200 but body was not valid JSON. "
        f"Body snippet: {last_text[:500]}"
    )

    # Accept either a wrapped agent step output (`{"output": {...}, ...}`) or
    # the structured payload at the top level.
    if isinstance(body, dict) and isinstance(body.get("output"), (dict, list)):
        candidate = body["output"]
    else:
        candidate = body

    try:
        Draft202012Validator(output_schema).validate(candidate)
    except Exception as exc:
        pytest.fail(
            "Agent response did not validate against the declared output_schema: "
            f"{exc}\nPayload: {json.dumps(candidate)[:500]}"
        )
