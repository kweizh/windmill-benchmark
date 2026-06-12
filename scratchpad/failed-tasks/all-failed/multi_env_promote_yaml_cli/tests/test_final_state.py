"""Final-state verification for multi_env_promote_yaml_cli.

These tests run after the executor has finished the task. They check that:
  * The local `wmill.yaml` declares both workspaces with the documented shape
    and a sufficiently narrow `includes:` scope.
  * The promoted script files exist on disk under `f/promote_${run-id}/`.
  * The script `f/promote_${run-id}/hello` now exists in the cloud production
    workspace and is callable via the Windmill HTTP API.
  * The pre-existing canary script `f/canary_${run-id}/keep_me` in production
    is still there (i.e., the sync was non-destructive).
  * The expected log line was appended to `output.log`.
"""

import json
import os
import re
import urllib.error
import urllib.request

import pytest
import yaml

PROJECT_DIR = "/home/user/promote-project"
WMILL_YAML = os.path.join(PROJECT_DIR, "wmill.yaml")
OUTPUT_LOG = os.path.join(PROJECT_DIR, "output.log")
EXPECTED_BASE_URL = "https://app.windmill.dev"


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


@pytest.fixture(scope="session")
def env() -> dict[str, str]:
    required = (
        "ZEALT_RUN_ID",
        "WMILL_BASE_URL",
        "WMILL_TOKEN",
        "WMILL_STAGING_WORKSPACE_ID",
        "WMILL_PROD_WORKSPACE_ID",
    )
    values: dict[str, str] = {}
    for name in required:
        v = os.environ.get(name)
        assert v, f"Environment variable {name} must be set."
        values[name] = v
    values["WMILL_BASE_URL"] = values["WMILL_BASE_URL"].rstrip("/")
    return values


@pytest.fixture(scope="session")
def wmill_yaml() -> dict:
    assert os.path.isfile(WMILL_YAML), (
        f"Expected wmill.yaml at {WMILL_YAML}, but it does not exist. The agent must "
        f"create a declarative wmill.yaml that declares the two workspaces."
    )
    with open(WMILL_YAML, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"wmill.yaml is not valid YAML: {e}")
    assert isinstance(data, dict), "wmill.yaml must parse to a mapping at the top level."
    return data


def test_wmill_yaml_declares_workspaces_mapping(wmill_yaml: dict) -> None:
    assert "workspaces" in wmill_yaml, (
        "wmill.yaml must contain a top-level `workspaces:` mapping per "
        "https://www.windmill.dev/docs/advanced/cli/sync"
    )
    workspaces = wmill_yaml["workspaces"]
    assert isinstance(workspaces, dict), "`workspaces:` must be a mapping."
    expected_keys = {"staging", "production"}
    actual_keys = {k for k in workspaces.keys() if k != "commonSpecificItems"}
    assert actual_keys == expected_keys, (
        f"`workspaces:` must declare exactly the two entries {sorted(expected_keys)}, "
        f"got {sorted(actual_keys)}."
    )


def test_wmill_yaml_staging_entry(wmill_yaml: dict, env: dict[str, str]) -> None:
    staging = wmill_yaml["workspaces"]["staging"]
    assert isinstance(staging, dict), "`workspaces.staging` must be a mapping."
    assert staging.get("baseUrl") == EXPECTED_BASE_URL, (
        f"`workspaces.staging.baseUrl` must equal {EXPECTED_BASE_URL!r}, got "
        f"{staging.get('baseUrl')!r}."
    )
    expected_id = env["WMILL_STAGING_WORKSPACE_ID"]
    actual_id = staging.get("workspaceId", "staging")
    assert actual_id == expected_id, (
        f"`workspaces.staging.workspaceId` must equal {expected_id!r}, got {actual_id!r}."
    )


def test_wmill_yaml_production_entry(wmill_yaml: dict, env: dict[str, str]) -> None:
    prod = wmill_yaml["workspaces"]["production"]
    assert isinstance(prod, dict), "`workspaces.production` must be a mapping."
    assert prod.get("baseUrl") == EXPECTED_BASE_URL, (
        f"`workspaces.production.baseUrl` must equal {EXPECTED_BASE_URL!r}, got "
        f"{prod.get('baseUrl')!r}."
    )
    expected_id = env["WMILL_PROD_WORKSPACE_ID"]
    actual_id = prod.get("workspaceId", "production")
    assert actual_id == expected_id, (
        f"`workspaces.production.workspaceId` must equal {expected_id!r}, got {actual_id!r}."
    )


def test_wmill_yaml_includes_scopes_to_promote_folder(
    wmill_yaml: dict, env: dict[str, str]
) -> None:
    """The `includes:` patterns must restrict the sync to the promote folder so
    that the destructive `wmill sync push` does not delete unrelated assets.
    """
    run_id = env["ZEALT_RUN_ID"]
    includes = wmill_yaml.get("includes")
    assert isinstance(includes, list) and includes, (
        "wmill.yaml must declare a non-empty top-level `includes:` list scoping the sync."
    )
    folder = f"f/promote_{run_id}/"
    matched = any(folder in str(pat) for pat in includes)
    assert matched, (
        f"`includes:` must contain a pattern that scopes the sync to {folder!r}, "
        f"got {includes!r}."
    )
    # Forbid the wide-open default that would touch every asset.
    assert "f/**" not in [str(pat).strip() for pat in includes], (
        "`includes:` must NOT use the wide-open default `f/**`, which would let "
        "`wmill sync push` reconcile and delete unrelated production assets."
    )


def test_promoted_script_file_exists_locally(env: dict[str, str]) -> None:
    run_id = env["ZEALT_RUN_ID"]
    folder = os.path.join(PROJECT_DIR, "f", f"promote_{run_id}")
    candidates = [
        os.path.join(folder, "hello.ts"),
        os.path.join(folder, "hello.bun.ts"),
    ]
    existing = [p for p in candidates if os.path.isfile(p) and os.path.getsize(p) > 0]
    assert existing, (
        f"Expected a non-empty TypeScript source file for the promoted script under "
        f"{folder} (one of: {candidates})."
    )


def test_promoted_script_metadata_exists_locally(env: dict[str, str]) -> None:
    run_id = env["ZEALT_RUN_ID"]
    metadata = os.path.join(PROJECT_DIR, "f", f"promote_{run_id}", "hello.script.yaml")
    assert os.path.isfile(metadata) and os.path.getsize(metadata) > 0, (
        f"Expected the script metadata YAML at {metadata} to exist and be non-empty."
    )


def test_script_exists_in_production_workspace(env: dict[str, str]) -> None:
    run_id = env["ZEALT_RUN_ID"]
    prod_ws = env["WMILL_PROD_WORKSPACE_ID"]
    path = f"f/promote_{run_id}/hello"
    url = f"{env['WMILL_BASE_URL']}/api/w/{prod_ws}/scripts/get/p/{path}"
    status, payload = _request("GET", url, env["WMILL_TOKEN"])
    assert status == 200, (
        f"Expected script {path!r} to exist in the production workspace {prod_ws!r}. "
        f"GET {url} returned HTTP {status}: {payload!r}."
    )
    try:
        body = json.loads(payload)
    except json.JSONDecodeError as e:
        pytest.fail(f"Production script GET response was not JSON: {e}: {payload!r}")
    assert body.get("path") == path, (
        f"Production script payload must report path={path!r}, got {body.get('path')!r}."
    )


def test_promoted_script_is_callable_in_production(env: dict[str, str]) -> None:
    run_id = env["ZEALT_RUN_ID"]
    prod_ws = env["WMILL_PROD_WORKSPACE_ID"]
    path = f"f/promote_{run_id}/hello"
    url = f"{env['WMILL_BASE_URL']}/api/w/{prod_ws}/jobs/run_wait_result/p/{path}"
    status, payload = _request("POST", url, env["WMILL_TOKEN"], {"name": "prod"})
    assert status == 200, (
        f"Expected the promoted script {path!r} to be callable in production "
        f"workspace {prod_ws!r}. POST {url} returned HTTP {status}: {payload!r}."
    )
    text = payload.decode("utf-8", errors="replace").strip()
    # Windmill returns the JSON-encoded result, so a string result is `"hello prod"`.
    assert text in ('"hello prod"', "hello prod"), (
        f"Expected promoted script to return \"hello prod\", got {text!r}."
    )


def test_canary_script_was_not_deleted_in_production(env: dict[str, str]) -> None:
    run_id = env["ZEALT_RUN_ID"]
    prod_ws = env["WMILL_PROD_WORKSPACE_ID"]
    path = f"f/canary_{run_id}/keep_me"
    url = f"{env['WMILL_BASE_URL']}/api/w/{prod_ws}/scripts/get/p/{path}"
    status, payload = _request("GET", url, env["WMILL_TOKEN"])
    assert status == 200, (
        f"The canary script {path!r} must still exist in production workspace "
        f"{prod_ws!r} after promotion (the sync must be non-destructive). "
        f"GET {url} returned HTTP {status}: {payload!r}."
    )
    try:
        body = json.loads(payload)
    except json.JSONDecodeError as e:
        pytest.fail(f"Canary script GET response was not JSON: {e}: {payload!r}")
    assert body.get("path") == path, (
        f"Canary script payload must report path={path!r}, got {body.get('path')!r}."
    )


def test_output_log_contains_promotion_line(env: dict[str, str]) -> None:
    assert os.path.isfile(OUTPUT_LOG), (
        f"Expected log file {OUTPUT_LOG} to exist after the promotion."
    )
    with open(OUTPUT_LOG, "r", encoding="utf-8") as f:
        contents = f.read()
    run_id = env["ZEALT_RUN_ID"]
    prod_ws = env["WMILL_PROD_WORKSPACE_ID"]
    expected = (
        rf"^Promoted: f/promote_{re.escape(run_id)}/hello -> "
        rf"{re.escape(prod_ws)}\s*$"
    )
    matched = any(re.match(expected, line) for line in contents.splitlines())
    assert matched, (
        f"Expected {OUTPUT_LOG} to contain a line matching {expected!r}; "
        f"got:\n{contents}"
    )
