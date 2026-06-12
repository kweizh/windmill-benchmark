import os
import re
import uuid

import pytest
import requests
import yaml

PROJECT_DIR = "/home/user/myproject"


def _run_id_safe() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for verification."
    return run_id.replace("-", "_")


def _asset_dir() -> str:
    return os.path.join(PROJECT_DIR, "f", f"secret_masking_{_run_id_safe()}")


def _variable_path() -> str:
    return f"f/secret_masking_{_run_id_safe()}/api_key"


def _expected_secret_value() -> str:
    return f"secret_value_{_run_id_safe()}_padding"


def _expected_mask_prefix() -> str:
    # Per https://www.windmill.dev/changelog/secret-masking-job-logs:
    # the first 3 characters of the secret are kept and the rest replaced by *****.
    return _expected_secret_value()[:3] + "*****"


def _windmill_env() -> tuple[str, str, str]:
    base_url = os.environ.get("WMILL_BASE_URL")
    workspace = os.environ.get("WMILL_WORKSPACE")
    token = os.environ.get("WMILL_TOKEN")
    assert base_url, "WMILL_BASE_URL environment variable must be set."
    assert workspace, "WMILL_WORKSPACE environment variable must be set."
    assert token, "WMILL_TOKEN environment variable must be set."
    return base_url.rstrip("/"), workspace, token


def test_wmill_yaml_exists():
    path = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert os.path.isfile(path), (
        f"Expected {path} to exist after the executor bootstrapped the Windmill project."
    )


def test_variable_manifest_exists_and_is_secret():
    path = os.path.join(_asset_dir(), "api_key.variable.yaml")
    assert os.path.isfile(path), (
        f"Expected the declarative variable manifest at {path}."
    )
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    # The Windmill CLI variable schema documents `is_secret`; older specs sometimes use `secret`.
    secret_flag = data.get("is_secret")
    if secret_flag is None:
        secret_flag = data.get("secret")
    assert secret_flag is True, (
        f"Variable manifest at {path} must mark the variable as a secret "
        f"(is_secret: true). Got: {data!r}"
    )


def test_script_file_pair_exists_and_calls_get_variable():
    py_path = os.path.join(_asset_dir(), "print_secret.py")
    meta_path = os.path.join(_asset_dir(), "print_secret.script.yaml")
    assert os.path.isfile(py_path), f"Expected Python script at {py_path}."
    assert os.path.isfile(meta_path), (
        f"Expected the script metadata file at {meta_path}."
    )
    with open(py_path) as f:
        source = f.read()
    pattern = re.compile(
        r"wmill\s*\.\s*get_variable\s*\(\s*['\"]"
        + re.escape(_variable_path())
        + r"['\"]\s*\)"
    )
    assert pattern.search(source), (
        f"The script at {py_path} must call wmill.get_variable(\"{_variable_path()}\")."
    )


def test_output_log_contains_job_id():
    path = os.path.join(PROJECT_DIR, "output.log")
    assert os.path.isfile(path), f"Expected {path} to exist with the job UUID."
    with open(path) as f:
        contents = f.read()
    match = re.search(r"Job ID:\s*([0-9a-fA-F-]{36})", contents)
    assert match, (
        f"{path} must contain a line in the form 'Job ID: <uuid>'. Got:\n{contents}"
    )
    # Validate UUID parsability.
    uuid.UUID(match.group(1))


def _read_job_id() -> str:
    path = os.path.join(PROJECT_DIR, "output.log")
    with open(path) as f:
        contents = f.read()
    match = re.search(r"Job ID:\s*([0-9a-fA-F-]{36})", contents)
    assert match, f"Could not parse Job ID from {path}."
    return match.group(1)


def test_remote_variable_is_secret_via_api():
    base_url, workspace, token = _windmill_env()
    url = f"{base_url}/api/w/{workspace}/variables/get/{_variable_path()}"
    response = requests.get(
        url, headers={"Authorization": f"Bearer {token}"}, timeout=30
    )
    assert response.status_code == 200, (
        f"GET {url} should return 200, got {response.status_code}: {response.text}"
    )
    payload = response.json()
    is_secret = payload.get("is_secret")
    if is_secret is None:
        is_secret = payload.get("secret")
    assert is_secret is True, (
        f"Remote variable at {_variable_path()} must be marked as a secret. "
        f"Got payload: {payload!r}"
    )


def test_job_logs_show_masked_secret():
    base_url, workspace, token = _windmill_env()
    job_id = _read_job_id()
    url = f"{base_url}/api/w/{workspace}/jobs_u/get_logs/{job_id}"
    response = requests.get(
        url, headers={"Authorization": f"Bearer {token}"}, timeout=30
    )
    assert response.status_code == 200, (
        f"GET {url} should return 200, got {response.status_code}: {response.text}"
    )
    logs = response.text
    expected_mask = _expected_mask_prefix()
    plaintext = _expected_secret_value()

    assert plaintext not in logs, (
        "Windmill must mask the secret value in job logs; the plaintext value "
        f"{plaintext!r} must not appear. Logs were:\n{logs}"
    )
    assert expected_mask in logs, (
        "Windmill's documented mask format keeps the first 3 characters of the "
        "secret followed by '*****' (see "
        "https://www.windmill.dev/changelog/secret-masking-job-logs). Expected "
        f"to find {expected_mask!r} in the job logs. Logs were:\n{logs}"
    )
