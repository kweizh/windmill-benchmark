"""Initial state verification and setup for multi_env_promote_yaml_cli.

This module both prepares and verifies the cloud-side initial state, namely:
  * The staging workspace contains the script `f/promote_${run-id}/hello`.
  * The production workspace contains the canary script
    `f/canary_${run-id}/keep_me` (so we can verify that the agent's sync did
    not delete unrelated assets).
  * The production workspace does NOT yet contain `f/promote_${run-id}/hello`.

It also asserts that the local project folder, the `wmill` CLI, and all
required environment variables are present before evaluation begins.
"""

import json
import os
import shutil
import urllib.error
import urllib.request

import pytest

PROJECT_DIR = "/home/user/promote-project"

REQUIRED_ENV_VARS = (
    "ZEALT_RUN_ID",
    "WMILL_BASE_URL",
    "WMILL_TOKEN",
    "WMILL_STAGING_WORKSPACE_ID",
    "WMILL_PROD_WORKSPACE_ID",
)


def _env(name: str) -> str:
    value = os.environ.get(name)
    assert value, f"Environment variable {name} must be set in the task environment."
    return value


def _request(method: str, url: str, token: str, body: object | None = None) -> tuple[int, bytes]:
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _script_exists(base_url: str, workspace_id: str, token: str, path: str) -> bool:
    url = f"{base_url}/api/w/{workspace_id}/scripts/get/p/{path}"
    status, _ = _request("GET", url, token)
    return status == 200


def _delete_script_if_exists(base_url: str, workspace_id: str, token: str, path: str) -> None:
    """Best-effort: delete a script (and any history) at the given path."""
    url = f"{base_url}/api/w/{workspace_id}/scripts/delete/p/{path}"
    _request("POST", url, token)


def _create_script(
    base_url: str,
    workspace_id: str,
    token: str,
    path: str,
    content: str,
    language: str,
    summary: str,
    description: str,
    schema: dict,
) -> None:
    url = f"{base_url}/api/w/{workspace_id}/scripts/create"
    body = {
        "path": path,
        "summary": summary,
        "description": description,
        "content": content,
        "language": language,
        "schema": schema,
        "is_template": False,
    }
    status, payload = _request("POST", url, token, body)
    assert status in (200, 201), (
        f"Failed to create script {path!r} in workspace {workspace_id!r} (HTTP {status}): "
        f"{payload!r}"
    )


def _ensure_folder(base_url: str, workspace_id: str, token: str, folder_name: str) -> None:
    """Best-effort: create a folder so the script path resolves cleanly."""
    url = f"{base_url}/api/w/{workspace_id}/folders/create"
    _request("POST", url, token, {"name": folder_name, "summary": "", "owners": []})


def _setup_cloud_state() -> None:
    base_url = _env("WMILL_BASE_URL").rstrip("/")
    token = _env("WMILL_TOKEN")
    run_id = _env("ZEALT_RUN_ID")
    staging_ws = _env("WMILL_STAGING_WORKSPACE_ID")
    prod_ws = _env("WMILL_PROD_WORKSPACE_ID")

    promote_path = f"f/promote_{run_id}/hello"
    canary_path = f"f/canary_{run_id}/keep_me"

    # Reset: ensure the production workspace does not already have the
    # promoted script from a previous failed run.
    _delete_script_if_exists(base_url, prod_ws, token, promote_path)

    # Pre-create folders to avoid 404s on script create.
    _ensure_folder(base_url, staging_ws, token, f"promote_{run_id}")
    _ensure_folder(base_url, prod_ws, token, f"canary_{run_id}")

    hello_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "name": {"type": "string", "default": "world"},
        },
        "required": ["name"],
    }
    hello_content = (
        "export async function main(name: string) {\n"
        "  return `hello ${name}`;\n"
        "}\n"
    )

    if not _script_exists(base_url, staging_ws, token, promote_path):
        _create_script(
            base_url,
            staging_ws,
            token,
            promote_path,
            hello_content,
            "bun",
            "Hello world (staging)",
            "Greets the caller by name. Deployed in staging; to be promoted to production.",
            hello_schema,
        )

    canary_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {},
    }
    canary_content = (
        "export async function main() {\n"
        "  return \"canary\";\n"
        "}\n"
    )
    if not _script_exists(base_url, prod_ws, token, canary_path):
        _create_script(
            base_url,
            prod_ws,
            token,
            canary_path,
            canary_content,
            "bun",
            "Canary (production)",
            "Pre-existing production-only asset used to verify that the promotion sync was non-destructive.",
            canary_schema,
        )


# Module-level setup: prepare the cloud state exactly once before the
# assertions below run.
_setup_cloud_state()


@pytest.mark.parametrize("name", REQUIRED_ENV_VARS)
def test_required_env_var_is_set(name: str) -> None:
    assert os.environ.get(name), f"Required environment variable {name} is not set."


def test_wmill_cli_is_available() -> None:
    assert shutil.which("wmill") is not None, "The `wmill` CLI must be installed and on PATH."


def test_project_dir_exists() -> None:
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} must exist."


def test_project_dir_is_writable() -> None:
    assert os.access(PROJECT_DIR, os.W_OK), f"Project directory {PROJECT_DIR} must be writable."


def test_staging_workspace_has_script_to_promote() -> None:
    base_url = os.environ["WMILL_BASE_URL"].rstrip("/")
    token = os.environ["WMILL_TOKEN"]
    run_id = os.environ["ZEALT_RUN_ID"]
    staging_ws = os.environ["WMILL_STAGING_WORKSPACE_ID"]
    path = f"f/promote_{run_id}/hello"
    assert _script_exists(base_url, staging_ws, token, path), (
        f"Expected script {path!r} to already exist in the staging workspace "
        f"{staging_ws!r} before evaluation begins."
    )


def test_production_workspace_has_canary_script() -> None:
    base_url = os.environ["WMILL_BASE_URL"].rstrip("/")
    token = os.environ["WMILL_TOKEN"]
    run_id = os.environ["ZEALT_RUN_ID"]
    prod_ws = os.environ["WMILL_PROD_WORKSPACE_ID"]
    path = f"f/canary_{run_id}/keep_me"
    assert _script_exists(base_url, prod_ws, token, path), (
        f"Expected canary script {path!r} to already exist in the production workspace "
        f"{prod_ws!r} so the test can verify non-destructive promotion."
    )


def test_production_workspace_does_not_yet_have_promoted_script() -> None:
    base_url = os.environ["WMILL_BASE_URL"].rstrip("/")
    token = os.environ["WMILL_TOKEN"]
    run_id = os.environ["ZEALT_RUN_ID"]
    prod_ws = os.environ["WMILL_PROD_WORKSPACE_ID"]
    path = f"f/promote_{run_id}/hello"
    assert not _script_exists(base_url, prod_ws, token, path), (
        f"Script {path!r} must NOT exist in the production workspace {prod_ws!r} "
        f"before the executor performs the promotion."
    )
