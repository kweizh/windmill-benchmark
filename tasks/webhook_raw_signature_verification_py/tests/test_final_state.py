import hashlib
import hmac
import os
import re

import pytest
import requests


PROJECT_DIR = "/home/user/wmtask"
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    assert value, f"Required environment variable {name} is not set."
    return value


@pytest.fixture(scope="module")
def run_id() -> str:
    return _env("ZEALT_RUN_ID")


@pytest.fixture(scope="module")
def wm_token() -> str:
    return _env("WM_TOKEN")


@pytest.fixture(scope="module")
def wm_workspace() -> str:
    return _env("WM_WORKSPACE")


@pytest.fixture(scope="module")
def wm_base_url() -> str:
    return os.environ.get("WM_BASE_URL", "https://app.windmill.dev").rstrip("/")


@pytest.fixture(scope="module")
def auth_headers(wm_token: str) -> dict:
    return {"Authorization": f"Bearer {wm_token}"}


@pytest.fixture(scope="module")
def log_content() -> str:
    assert os.path.isfile(LOG_PATH), (
        f"Expected log file {LOG_PATH} to exist after the executor completes the task, "
        "but it is missing."
    )
    with open(LOG_PATH, "r", encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def script_path(run_id: str, log_content: str) -> str:
    expected = f"f/zealt_{run_id}/sig_verify"
    pattern = rf"Script path:\s*{re.escape(expected)}\b"
    assert re.search(pattern, log_content), (
        f"Expected the log file {LOG_PATH} to contain a line "
        f"'Script path: {expected}', but it did not. Log content:\n{log_content}"
    )
    return expected


@pytest.fixture(scope="module")
def variable_path(run_id: str) -> str:
    return f"f/zealt_{run_id}/webhook_secret"


@pytest.fixture(scope="module")
def signature_header(log_content: str) -> str:
    match = re.search(r"Signature header name:\s*([A-Za-z0-9_\-]+)", log_content)
    assert match, (
        f"Expected the log file {LOG_PATH} to contain a line "
        "'Signature header name: <header>', but no such line was found."
    )
    header = match.group(1).strip()
    assert header, "Signature header name parsed from output.log is empty."
    return header


def test_script_deployed_with_required_imports(
    wm_base_url: str,
    wm_workspace: str,
    auth_headers: dict,
    script_path: str,
) -> None:
    url = f"{wm_base_url}/api/w/{wm_workspace}/scripts/get/p/{script_path}"
    resp = requests.get(url, headers=auth_headers, timeout=30)
    assert resp.status_code == 200, (
        f"Failed to fetch deployed script at {script_path}: "
        f"HTTP {resp.status_code} {resp.text}"
    )
    body = resp.json()
    language = (body.get("language") or "").lower()
    assert "python" in language, (
        f"Expected the deployed script's language to be Python, got '{language}'."
    )
    content = body.get("content") or ""
    assert "import hmac" in content, (
        "Expected the deployed script to 'import hmac' from the Python standard library."
    )
    assert re.search(r"hashlib", content) and re.search(r"sha256", content), (
        "Expected the deployed script to use hashlib.sha256 for the HMAC digest."
    )
    assert re.search(r"wmill\.get_variable\s*\(", content), (
        "Expected the deployed script to read its signing secret via wmill.get_variable(...)."
    )


def test_variable_is_secret(
    wm_base_url: str,
    wm_workspace: str,
    auth_headers: dict,
    variable_path: str,
) -> None:
    url = f"{wm_base_url}/api/w/{wm_workspace}/variables/get/{variable_path}"
    resp = requests.get(url, headers=auth_headers, timeout=30)
    assert resp.status_code == 200, (
        f"Failed to fetch Variable {variable_path}: HTTP {resp.status_code} {resp.text}"
    )
    data = resp.json()
    assert data.get("is_secret") is True, (
        f"Expected Windmill Variable at {variable_path} to be marked as a secret, "
        f"got is_secret={data.get('is_secret')}."
    )


@pytest.fixture(scope="module")
def signing_secret(
    wm_base_url: str,
    wm_workspace: str,
    auth_headers: dict,
    variable_path: str,
) -> str:
    url = f"{wm_base_url}/api/w/{wm_workspace}/variables/get_value/{variable_path}"
    resp = requests.get(url, headers=auth_headers, timeout=30)
    assert resp.status_code == 200, (
        f"Failed to fetch Variable value at {variable_path}: "
        f"HTTP {resp.status_code} {resp.text}"
    )
    # The endpoint returns the decrypted value as a JSON-encoded string.
    try:
        value = resp.json()
    except ValueError:
        value = resp.text
    assert isinstance(value, str) and value, (
        f"Expected Windmill Variable at {variable_path} to have a non-empty string value, "
        f"got: {value!r}"
    )
    return value


def _webhook_url(
    wm_base_url: str,
    wm_workspace: str,
    script_path: str,
    signature_header: str,
) -> str:
    return (
        f"{wm_base_url}/api/w/{wm_workspace}/jobs/run_wait_result/p/{script_path}"
        f"?raw=true&include_header={signature_header}"
    )


def _is_rejection(resp: requests.Response) -> bool:
    """A request is 'rejected' if it returns non-2xx, an error result, or {'valid': false}."""
    if resp.status_code < 200 or resp.status_code >= 300:
        return True
    try:
        body = resp.json()
    except ValueError:
        # Non-JSON response on a successful status — treat as ambiguous; not a clear pass.
        return False
    if isinstance(body, dict):
        if body.get("valid") is False:
            return True
        # Windmill returns errors from sync endpoints as {"error": {...}} with status 200.
        if "error" in body and body.get("valid") is not True:
            return True
    return False


def test_correctly_signed_request_returns_valid_true(
    wm_base_url: str,
    wm_workspace: str,
    auth_headers: dict,
    script_path: str,
    signature_header: str,
    signing_secret: str,
    run_id: str,
) -> None:
    payload = f"hello-windmill-zealt-{run_id}".encode("utf-8")
    good_sig = hmac.new(signing_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    url = _webhook_url(wm_base_url, wm_workspace, script_path, signature_header)
    headers = {
        **auth_headers,
        signature_header: good_sig,
        "Content-Type": "text/plain",
    }
    resp = requests.post(url, headers=headers, data=payload, timeout=60)
    assert resp.status_code == 200, (
        f"Expected the synchronous webhook to return HTTP 200 for a correctly-signed "
        f"request, got {resp.status_code}. Body: {resp.text}"
    )
    try:
        body = resp.json()
    except ValueError:
        pytest.fail(f"Webhook response was not valid JSON: {resp.text!r}")
    assert isinstance(body, dict) and body.get("valid") is True, (
        f"Expected webhook response to be {{'valid': true}} for a correct signature, "
        f"got: {body!r}"
    )


def test_incorrectly_signed_request_is_rejected(
    wm_base_url: str,
    wm_workspace: str,
    auth_headers: dict,
    script_path: str,
    signature_header: str,
    signing_secret: str,
    run_id: str,
) -> None:
    payload = f"hello-windmill-zealt-{run_id}".encode("utf-8")
    bad_sig = "deadbeef" * 8  # 64 hex chars — well-formed but wrong digest
    url = _webhook_url(wm_base_url, wm_workspace, script_path, signature_header)
    headers = {
        **auth_headers,
        signature_header: bad_sig,
        "Content-Type": "text/plain",
    }
    resp = requests.post(url, headers=headers, data=payload, timeout=60)
    assert _is_rejection(resp), (
        "Expected the webhook to reject an incorrectly-signed request "
        "(either by returning {'valid': false}, a non-success HTTP status, or an error "
        f"result). Got HTTP {resp.status_code} with body: {resp.text!r}"
    )


def test_tampered_body_is_rejected(
    wm_base_url: str,
    wm_workspace: str,
    auth_headers: dict,
    script_path: str,
    signature_header: str,
    signing_secret: str,
    run_id: str,
) -> None:
    original = f"hello-windmill-zealt-{run_id}".encode("utf-8")
    tampered = original + b"!"
    good_sig_for_original = hmac.new(
        signing_secret.encode("utf-8"), original, hashlib.sha256
    ).hexdigest()
    url = _webhook_url(wm_base_url, wm_workspace, script_path, signature_header)
    headers = {
        **auth_headers,
        signature_header: good_sig_for_original,
        "Content-Type": "text/plain",
    }
    resp = requests.post(url, headers=headers, data=tampered, timeout=60)
    assert _is_rejection(resp), (
        "Expected the webhook to reject a request where the body was tampered with "
        "after signing. Got HTTP "
        f"{resp.status_code} with body: {resp.text!r}"
    )
