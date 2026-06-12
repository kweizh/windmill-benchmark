import os
import re

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")


def _env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", (
        f"{name} environment variable is required for verification."
    )
    return value


@pytest.fixture(scope="module")
def run_id() -> str:
    return _env("ZEALT_RUN_ID")


@pytest.fixture(scope="module")
def sanitized_run_id(run_id: str) -> str:
    return run_id.replace("-", "_")


@pytest.fixture(scope="module")
def base_url() -> str:
    return _env("WMILL_BASE_URL").rstrip("/")


@pytest.fixture(scope="module")
def workspace() -> str:
    return _env("WMILL_WORKSPACE")


@pytest.fixture(scope="module")
def auth_headers() -> dict:
    return {"Authorization": f"Bearer {_env('WMILL_TOKEN')}"}


@pytest.fixture(scope="module")
def expected_api_url(run_id: str) -> str:
    return f"https://api.example.com/{run_id}"


@pytest.fixture(scope="module")
def resource_type_name(sanitized_run_id: str) -> str:
    return f"my_api_creds_{sanitized_run_id}"


@pytest.fixture(scope="module")
def resource_path(sanitized_run_id: str) -> str:
    return f"f/zealt/creds_{sanitized_run_id}"


@pytest.fixture(scope="module")
def script_path(sanitized_run_id: str) -> str:
    return f"f/zealt/read_api_url_{sanitized_run_id}"


def test_output_log_contains_api_url(expected_api_url: str):
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(
        r"apiUrl:\s*" + re.escape(expected_api_url),
        re.MULTILINE,
    )
    assert pattern.search(content), (
        f"Log file {LOG_FILE} must contain a line matching 'apiUrl: {expected_api_url}'."
        f" Got:\n{content}"
    )


def test_resource_type_exists_with_expected_schema(
    base_url: str,
    workspace: str,
    auth_headers: dict,
    resource_type_name: str,
):
    url = f"{base_url}/api/w/{workspace}/resources/type/get/{resource_type_name}"
    response = requests.get(url, headers=auth_headers, timeout=30)
    assert response.status_code == 200, (
        f"Resource type {resource_type_name} not found via {url}: "
        f"status={response.status_code}, body={response.text}"
    )
    body = response.json()
    schema = body.get("schema")
    assert isinstance(schema, dict), (
        f"Resource type {resource_type_name} must have a JSON Schema 'schema' object,"
        f" got: {body}"
    )
    assert schema.get("type") == "object", (
        f"Resource type schema must have type=='object', got: {schema.get('type')}"
    )
    properties = schema.get("properties", {})
    assert isinstance(properties, dict), (
        f"Resource type schema must have a 'properties' object, got: {properties!r}"
    )

    api_url_prop = properties.get("apiUrl")
    assert isinstance(api_url_prop, dict), (
        f"Resource type schema must declare property 'apiUrl', got properties: {properties}"
    )
    assert api_url_prop.get("type") == "string", (
        f"'apiUrl' must be type 'string', got: {api_url_prop.get('type')}"
    )

    token_prop = properties.get("token")
    assert isinstance(token_prop, dict), (
        f"Resource type schema must declare property 'token', got properties: {properties}"
    )
    assert token_prop.get("type") == "string", (
        f"'token' must be type 'string', got: {token_prop.get('type')}"
    )
    assert token_prop.get("format") == "password", (
        f"'token' must be marked with format 'password', got: {token_prop.get('format')}"
    )

    required = schema.get("required") or []
    assert "apiUrl" in required and "token" in required, (
        f"Both 'apiUrl' and 'token' must be in the schema's 'required' list, got: {required}"
    )


def test_resource_instance_exists_with_expected_value(
    base_url: str,
    workspace: str,
    auth_headers: dict,
    resource_path: str,
    resource_type_name: str,
    expected_api_url: str,
):
    url = f"{base_url}/api/w/{workspace}/resources/get/{resource_path}"
    response = requests.get(url, headers=auth_headers, timeout=30)
    assert response.status_code == 200, (
        f"Resource at {resource_path} not found via {url}: "
        f"status={response.status_code}, body={response.text}"
    )
    body = response.json()
    assert body.get("resource_type") == resource_type_name, (
        f"Resource at {resource_path} must have resource_type=='{resource_type_name}',"
        f" got: {body.get('resource_type')}"
    )
    value = body.get("value")
    assert isinstance(value, dict), (
        f"Resource at {resource_path} must have an object 'value', got: {value!r}"
    )
    assert value.get("apiUrl") == expected_api_url, (
        f"Resource value.apiUrl must equal '{expected_api_url}', got: {value.get('apiUrl')}"
    )


def test_deployed_script_returns_api_url(
    base_url: str,
    workspace: str,
    auth_headers: dict,
    script_path: str,
    expected_api_url: str,
):
    url = f"{base_url}/api/w/{workspace}/jobs/run_wait_result/p/{script_path}"
    response = requests.post(url, headers=auth_headers, json={}, timeout=120)
    assert response.status_code == 200, (
        f"Failed to run script at {script_path} via {url}: "
        f"status={response.status_code}, body={response.text}"
    )
    try:
        result = response.json()
    except ValueError:
        result = response.text.strip().strip('"')
    if isinstance(result, str):
        actual = result
    else:
        actual = str(result)
    assert actual == expected_api_url, (
        f"Deployed script must return '{expected_api_url}', got: {actual!r}"
    )
