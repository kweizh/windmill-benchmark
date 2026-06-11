import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

import pytest

PROJECT_DIR = "/home/user/myproject"
WMILL_REMOTE = "https://app.windmill.dev"

# Public, read-only PostgreSQL mirror provided by RNAcentral
# (see https://rnacentral.org/help/public-database).
PG_RESOURCE_VALUE = {
    "host": "hh-pgsql-public.ebi.ac.uk",
    "port": 5432,
    "user": "reader",
    "dbname": "pfmegrnargs",
    "sslmode": "prefer",
    "password": "NWDMCE5xdipIjRrp",
}


def _windmill_env() -> tuple[str, str]:
    token = os.environ.get("WINDMILL_TOKEN")
    workspace = os.environ.get("WINDMILL_WORKSPACE")
    if not token:
        pytest.skip("WINDMILL_TOKEN not set; cannot configure the Windmill workspace.")
    if not workspace:
        pytest.skip("WINDMILL_WORKSPACE not set; cannot configure the Windmill workspace.")
    return token, workspace


@pytest.fixture(scope="session", autouse=True)
def windmill_bootstrap() -> None:
    """Configure the local Windmill CLI workspace and pre-seed the resource.

    This fixture is run BEFORE any test in the initial-state suite. It is
    idempotent so that repeated runs (including concurrent runs sharing the
    same workspace) are safe.
    """
    token, workspace = _windmill_env()

    # 1. Register the local CLI workspace entry. This is idempotent: re-running
    #    it overwrites any prior local entry with the same name.
    add_cmd = [
        "wmill",
        "workspace",
        "add",
        workspace,
        workspace,
        WMILL_REMOTE,
        "--token",
        token,
    ]
    add = subprocess.run(
        add_cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert add.returncode == 0, (
        "Failed to register the Windmill workspace with the CLI: "
        f"stdout={add.stdout[-500:]!r}, stderr={add.stderr[-500:]!r}"
    )

    # 2. Pre-seed (or replace) the Postgresql resource at f/eval/pg_resource via
    #    the REST API. Using PUT-like semantics (create or update).
    base = f"{WMILL_REMOTE}/api/w/{workspace}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Ensure the parent folder exists (best-effort).
    folder_payload = json.dumps(
        {"name": "eval", "summary": "Eval folder for benchmark tasks", "owners": []}
    ).encode("utf-8")
    folder_req = urllib.request.Request(
        f"{base}/folders/create",
        data=folder_payload,
        headers=headers,
        method="POST",
    )
    try:
        urllib.request.urlopen(folder_req, timeout=30).read()
    except urllib.error.HTTPError as exc:
        # 409/400 = already exists; that is fine.
        if exc.code not in (400, 409):
            raise AssertionError(
                f"Failed to create folder 'eval' (HTTP {exc.code}): {exc.read().decode('utf-8', errors='replace')[:300]}"
            ) from exc
    except urllib.error.URLError as exc:
        pytest.skip(f"Cannot reach Windmill cloud: {exc}")
        return

    # Check whether the resource already exists.
    exists_req = urllib.request.Request(
        f"{base}/resources/exists/f/eval/pg_resource",
        headers={"Authorization": f"Bearer {token}"},
    )
    resource_exists = False
    try:
        with urllib.request.urlopen(exists_req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            resource_exists = body.strip().lower() == "true"
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise AssertionError(
                f"Failed to query resource existence (HTTP {exc.code}): "
                f"{exc.read().decode('utf-8', errors='replace')[:300]}"
            ) from exc
    except urllib.error.URLError as exc:
        pytest.skip(f"Cannot reach Windmill cloud while checking resource: {exc}")
        return

    resource_body = {
        "path": "f/eval/pg_resource",
        "value": PG_RESOURCE_VALUE,
        "description": "Public RNAcentral read-only Postgres mirror used by the benchmark.",
        "resource_type": "postgresql",
    }
    encoded = json.dumps(resource_body).encode("utf-8")

    if resource_exists:
        # Update: PUT /resources/update_value/{path} accepts {"value": ...}.
        upd_payload = json.dumps({"value": PG_RESOURCE_VALUE}).encode("utf-8")
        upd_req = urllib.request.Request(
            f"{base}/resources/update_value/f/eval/pg_resource",
            data=upd_payload,
            headers=headers,
            method="POST",
        )
        try:
            urllib.request.urlopen(upd_req, timeout=30).read()
        except urllib.error.HTTPError as exc:
            raise AssertionError(
                f"Failed to update the seeded Postgres resource (HTTP {exc.code}): "
                f"{exc.read().decode('utf-8', errors='replace')[:300]}"
            ) from exc
    else:
        create_req = urllib.request.Request(
            f"{base}/resources/create",
            data=encoded,
            headers=headers,
            method="POST",
        )
        try:
            urllib.request.urlopen(create_req, timeout=30).read()
        except urllib.error.HTTPError as exc:
            # If the resource was created concurrently by another worker,
            # accept the conflict.
            if exc.code not in (400, 409):
                raise AssertionError(
                    f"Failed to create the seeded Postgres resource (HTTP {exc.code}): "
                    f"{exc.read().decode('utf-8', errors='replace')[:300]}"
                ) from exc


# ---------- Initial state assertions ----------


def test_wmill_binary_available() -> None:
    assert shutil.which("wmill") is not None, (
        "Windmill CLI 'wmill' not found in PATH. The cloud benchmark requires it."
    )


def test_bun_binary_available() -> None:
    assert shutil.which("bun") is not None, (
        "Bun runtime 'bun' not found in PATH. The benchmark targets the bun Windmill runtime."
    )


def test_project_dir_exists() -> None:
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory '{PROJECT_DIR}' to exist before the task starts."
    )


def test_wmill_yaml_exists() -> None:
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert os.path.isfile(wmill_yaml), (
        f"Expected '{wmill_yaml}' to exist so the agent can `wmill` against the cloud workspace."
    )


def test_windmill_env_vars_set() -> None:
    assert os.environ.get("WINDMILL_TOKEN"), (
        "Environment variable WINDMILL_TOKEN must be set for cloud authentication."
    )
    assert os.environ.get("WINDMILL_WORKSPACE"), (
        "Environment variable WINDMILL_WORKSPACE must be set to identify the target workspace."
    )


def test_pg_resource_pre_seeded() -> None:
    """The bootstrap fixture must have created (or updated) the resource."""
    token, workspace = _windmill_env()

    url = f"https://app.windmill.dev/api/w/{workspace}/resources/get/f/eval/pg_resource"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise AssertionError(
            f"Pre-seeded resource 'f/eval/pg_resource' was not found in workspace "
            f"'{workspace}' (HTTP {exc.code}). Bootstrap did not run correctly."
        ) from exc
    except urllib.error.URLError as exc:
        pytest.skip(f"Cannot reach Windmill cloud to verify resource: {exc}")
        return

    payload = json.loads(body)
    assert payload.get("resource_type") == "postgresql", (
        "Pre-seeded resource 'f/eval/pg_resource' has unexpected resource_type "
        f"{payload.get('resource_type')!r}; expected 'postgresql'."
    )


def test_script_path_not_yet_created() -> None:
    """The agent is expected to create the script; verify it does NOT exist yet."""
    script_path = os.path.join(PROJECT_DIR, "f", "eval", "pg_row_count.ts")
    assert not os.path.isfile(script_path), (
        f"'{script_path}' should not exist before the task starts; the agent must create it."
    )


def test_wmill_cli_can_list_scripts() -> None:
    """Best-effort check that the CLI is wired up and authenticated against the workspace."""
    result = subprocess.run(
        ["wmill", "script", "list"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        "`wmill script list` failed in initial state: "
        f"stdout={result.stdout[-500:]!r}, stderr={result.stderr[-500:]!r}"
    )
