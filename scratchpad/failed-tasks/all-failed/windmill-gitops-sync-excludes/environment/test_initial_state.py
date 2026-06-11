import os
import re
import shutil
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
WORKSPACE_NAME = "evaluation-ws"
WINDMILL_REMOTE = "https://app.windmill.dev/"
WINDMILL_API_BASE = "https://app.windmill.dev/api"

LEGACY_TS_CONTENT = """// Pre-seeded remote-only legacy script.
// This file does NOT exist on disk in /home/user/myproject; it was uploaded
// directly to the cloud workspace via the Windmill REST API so the agent must
// rely on the `excludes:` glob in wmill.yaml to prevent
// `wmill sync push --yes` from deleting it.
export async function main(message: string) {
  return { script: "legacy", echo: message };
}
"""


def _safe_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "")
    assert rid, "ZEALT_RUN_ID environment variable is not set."
    assert re.fullmatch(r"zr-[a-z0-9]+", rid), (
        f"ZEALT_RUN_ID '{rid}' does not match expected pattern 'zr-[a-z0-9]+'."
    )
    return rid.replace("-", "_")


def _folder_name(safe_id: str) -> str:
    # Windmill folder identifier (no leading "f/").
    return f"gitops_{safe_id}"


def _legacy_remote_path(safe_id: str) -> str:
    return f"f/{_folder_name(safe_id)}/legacy"


@pytest.fixture(scope="session", autouse=True)
def _register_windmill_workspace():
    """Register the Windmill cloud workspace using the runtime-provided token.

    The Docker image cannot bake in WINDMILL_TOKEN (it is a per-evaluation
    secret), so we configure `wmill` here, before any other initial-state
    assertion runs. This also leaves the workspace registered for the agent
    to use during task execution.
    """
    token = os.environ.get("WINDMILL_TOKEN", "")
    workspace = os.environ.get("WINDMILL_WORKSPACE", "")
    if not token or not workspace:
        # Let the dedicated env-var assertions below produce the helpful
        # failure message instead of crashing here.
        yield
        return

    # Best-effort: drop any prior registration for the same name so we never
    # leave a stale workspace pointer in the container's wmill config.
    subprocess.run(
        ["wmill", "workspace", "remove", WORKSPACE_NAME],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )

    result = subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            WORKSPACE_NAME,
            workspace,
            WINDMILL_REMOTE,
            "--token",
            token,
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"`wmill workspace add` failed (rc={result.returncode}). "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    yield


@pytest.fixture(scope="session", autouse=True)
def _seed_legacy_remote_script(_register_windmill_workspace):
    """Seed the pre-existing legacy script directly on the cloud workspace.

    The legacy script is INTENTIONALLY not present on disk: the whole point
    of the task is that the agent must add an `excludes:` glob to wmill.yaml
    so the destructive `wmill sync push --yes` cannot delete this remote-only
    asset. We seed it via the documented REST endpoints (folder create +
    script create) so that the agent's solution can be evaluated against a
    realistic GitOps preservation scenario.
    """
    token = os.environ.get("WINDMILL_TOKEN", "")
    workspace = os.environ.get("WINDMILL_WORKSPACE", "")
    rid = os.environ.get("ZEALT_RUN_ID", "")
    if not token or not workspace or not rid:
        yield
        return
    if not re.fullmatch(r"zr-[a-z0-9]+", rid):
        yield
        return

    safe_id = rid.replace("-", "_")
    folder = _folder_name(safe_id)
    legacy_path = _legacy_remote_path(safe_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 1. Ensure the f/<folder> exists. Idempotent: 409/400 means already exists.
    folder_resp = requests.post(
        f"{WINDMILL_API_BASE}/w/{workspace}/folders/create",
        headers=headers,
        json={"name": folder, "summary": "harbor gitops sync excludes folder"},
        timeout=30,
    )
    assert folder_resp.status_code in (200, 201, 400, 409), (
        f"Folder create at f/{folder} returned unexpected status "
        f"{folder_resp.status_code}: {folder_resp.text}"
    )

    # 2. Best-effort archive of any stale legacy script from a previous run
    #    with the same ZEALT_RUN_ID (very unlikely but keep idempotent).
    requests.post(
        f"{WINDMILL_API_BASE}/w/{workspace}/scripts/archive/p/{legacy_path}",
        headers=headers,
        timeout=30,
    )

    # 3. Create the legacy script via the documented REST endpoint.
    create_resp = requests.post(
        f"{WINDMILL_API_BASE}/w/{workspace}/scripts/create",
        headers=headers,
        json={
            "path": legacy_path,
            "summary": "harbor gitops excludes legacy script",
            "description": (
                "Pre-seeded remote-only script. Must survive "
                "`wmill sync push --yes` thanks to the `excludes:` glob."
            ),
            "content": LEGACY_TS_CONTENT,
            "schema": {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
                "order": ["message"],
            },
            "is_template": False,
            "language": "bun",
            "kind": "script",
        },
        timeout=60,
    )
    assert create_resp.status_code in (200, 201), (
        f"Failed to seed legacy script at {legacy_path}: "
        f"{create_resp.status_code} {create_resp.text}"
    )

    yield

    # Best-effort cleanup attempt at the end of the initial-state session is
    # NOT performed here — the final-state test still needs the legacy script
    # to exist after the agent runs. Cleanup is performed by the final-state
    # test (best effort) and is the responsibility of the verifier stage.


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill CLI binary not found in PATH."


def test_node_binary_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH (required by wmill CLI)."
    )


def test_python3_binary_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_wmill_yaml_exists():
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert os.path.isfile(wmill_yaml), (
        f"Expected pre-initialised Windmill workspace config at {wmill_yaml}."
    )


def test_wmill_yaml_has_default_includes_and_empty_excludes():
    """Sanity-check that the bootstrap-provided wmill.yaml is the default shape.

    The agent is expected to ADD an `excludes:` glob; if the bootstrap already
    contained one, the task would be trivial.
    """
    import yaml  # PyYAML is preinstalled in the image

    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    with open(wmill_yaml, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert isinstance(cfg, dict), (
        f"wmill.yaml is not a YAML mapping at the top level: {cfg!r}"
    )
    includes = cfg.get("includes", [])
    assert isinstance(includes, list) and "f/**" in includes, (
        f"Expected bootstrap wmill.yaml to include 'f/**'; got includes={includes!r}"
    )
    excludes = cfg.get("excludes", [])
    assert isinstance(excludes, list) and excludes == [], (
        "Expected bootstrap wmill.yaml `excludes:` to start empty so the "
        f"agent's added glob is the only protection. Got: {excludes!r}"
    )


def test_local_legacy_script_must_not_exist():
    """The legacy script is remote-only by design — there must be no on-disk copy."""
    safe_id = _safe_id()
    legacy_local = os.path.join(
        PROJECT_DIR, "f", _folder_name(safe_id), "legacy.ts"
    )
    assert not os.path.exists(legacy_local), (
        f"Legacy script {legacy_local} must NOT exist on disk; it is meant to "
        "be a remote-only asset protected by the `excludes:` glob."
    )


def test_initial_new_scripts_not_present():
    """The agent's deliverables must NOT already exist before evaluation."""
    safe_id = _safe_id()
    base = os.path.join(PROJECT_DIR, "f", _folder_name(safe_id))
    for fname in ("alpha.ts", "beta.ts", "gamma.py"):
        target = os.path.join(base, fname)
        assert not os.path.exists(target), (
            f"Initial state must not contain {target}; the agent is supposed "
            "to create it."
        )


def test_windmill_token_env_present():
    assert os.environ.get("WINDMILL_TOKEN"), (
        "WINDMILL_TOKEN environment variable is not set; required to authenticate "
        "against https://app.windmill.dev."
    )


def test_windmill_workspace_env_present():
    assert os.environ.get("WINDMILL_WORKSPACE"), (
        "WINDMILL_WORKSPACE environment variable is not set; required to target the "
        "correct Windmill cloud workspace."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID", "")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    assert re.fullmatch(r"zr-[a-z0-9]+", run_id), (
        f"ZEALT_RUN_ID '{run_id}' does not match expected pattern 'zr-[a-z0-9]+'."
    )


def test_wmill_workspace_registered():
    """Confirm the cloud workspace is registered after the autouse setup ran."""
    result = subprocess.run(
        ["wmill", "workspace", "list"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"`wmill workspace list` failed (rc={result.returncode}). "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    combined = result.stdout + result.stderr
    assert "app.windmill.dev" in combined, (
        "No Windmill cloud workspace is registered with `wmill workspace add`. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_legacy_script_seeded_on_remote():
    """The pre-seeded legacy script MUST be reachable via the script-get REST API."""
    token = os.environ["WINDMILL_TOKEN"]
    workspace = os.environ["WINDMILL_WORKSPACE"]
    safe_id = _safe_id()
    legacy_path = _legacy_remote_path(safe_id)

    resp = requests.get(
        f"{WINDMILL_API_BASE}/w/{workspace}/scripts/get/p/{legacy_path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"GET scripts/get/p/{legacy_path} returned {resp.status_code}: "
        f"{resp.text}. Initial bootstrap should have seeded this script."
    )
    body = resp.json()
    assert body.get("path") == legacy_path, (
        f"Seeded legacy script reports unexpected path: {body!r}"
    )
    assert body.get("language") == "bun", (
        f"Seeded legacy script language should be 'bun'; got {body.get('language')!r}"
    )
