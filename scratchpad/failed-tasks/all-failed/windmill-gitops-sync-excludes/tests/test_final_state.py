import fnmatch
import json
import os
import re
import subprocess

import pytest
import requests
import yaml

PROJECT_DIR = "/home/user/myproject"
WINDMILL_API_BASE = "https://app.windmill.dev/api"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "")
    assert rid, "ZEALT_RUN_ID environment variable is not set."
    assert re.fullmatch(r"zr-[a-z0-9]+", rid), (
        f"ZEALT_RUN_ID '{rid}' does not match expected pattern 'zr-[a-z0-9]+'."
    )
    return rid.replace("-", "_")


def _folder_name(safe_id: str) -> str:
    return f"gitops_{safe_id}"


def _remote_path(safe_id: str, name: str) -> str:
    return f"f/{_folder_name(safe_id)}/{name}"


def _headers() -> dict:
    token = os.environ.get("WINDMILL_TOKEN", "")
    assert token, "WINDMILL_TOKEN environment variable is not set."
    return {"Authorization": f"Bearer {token}"}


def _workspace() -> str:
    workspace = os.environ.get("WINDMILL_WORKSPACE", "")
    assert workspace, "WINDMILL_WORKSPACE environment variable is not set."
    return workspace


def _get_remote_script(workspace: str, path: str) -> requests.Response:
    return requests.get(
        f"{WINDMILL_API_BASE}/w/{workspace}/scripts/get/p/{path}",
        headers=_headers(),
        timeout=30,
    )


def _archive_remote_script(workspace: str, path: str) -> None:
    try:
        requests.post(
            f"{WINDMILL_API_BASE}/w/{workspace}/scripts/archive/p/{path}",
            headers=_headers(),
            timeout=15,
        )
    except Exception:
        pass


def _extract_last_json(text: str):
    """Return the last top-level JSON value parsed from `text`."""
    text = text.strip()
    if not text:
        raise AssertionError("wmill stdout was empty; no JSON result to parse.")

    try:
        return json.loads(text)
    except Exception:
        pass

    lines = text.splitlines()
    for start in range(len(lines)):
        candidate = "\n".join(lines[start:]).strip()
        if not candidate:
            continue
        if candidate[0] not in "[{":
            continue
        try:
            return json.loads(candidate)
        except Exception:
            continue

    raise AssertionError(
        f"Could not parse a JSON result from wmill stdout. Raw stdout:\n{text}"
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_output_log_exists_and_contains_expected_lines():
    log_path = os.path.join(PROJECT_DIR, "output.log")
    assert os.path.isfile(log_path), (
        f"Expected agent to write {log_path} summarising the deploy. "
        "It must contain 'Deployed folder:' and 'Excludes glob:' lines."
    )
    with open(log_path, "r", encoding="utf-8") as f:
        log_content = f.read()

    safe_id = _safe_id()
    folder = _folder_name(safe_id)

    folder_match = re.search(
        rf"^Deployed folder:\s*f/{re.escape(folder)}\s*$",
        log_content,
        re.MULTILINE,
    )
    assert folder_match, (
        f"Expected a line of the form 'Deployed folder: f/{folder}' in {log_path}. "
        f"Got:\n{log_content}"
    )

    excludes_match = re.search(
        r"^Excludes glob:\s*(\S.*?)\s*$", log_content, re.MULTILINE
    )
    assert excludes_match, (
        f"Expected a line of the form 'Excludes glob: <pattern>' in {log_path}. "
        f"Got:\n{log_content}"
    )
    pattern = excludes_match.group(1).strip().strip('"').strip("'")
    legacy_path = f"f/{folder}/legacy.ts"
    assert fnmatch.fnmatch(legacy_path, pattern), (
        f"Logged excludes glob '{pattern}' does not match the legacy script "
        f"path '{legacy_path}' under fnmatch semantics."
    )


def test_local_script_files_and_metadata_exist():
    safe_id = _safe_id()
    base = os.path.join(PROJECT_DIR, "f", _folder_name(safe_id))
    expected = [
        ("alpha", "ts"),
        ("beta", "ts"),
        ("gamma", "py"),
    ]
    for name, ext in expected:
        script_path = os.path.join(base, f"{name}.{ext}")
        meta_path = os.path.join(base, f"{name}.script.yaml")
        assert os.path.isfile(script_path), (
            f"Expected agent to create local script file at {script_path}."
        )
        assert os.path.isfile(meta_path), (
            f"Expected agent to create script metadata at {meta_path} so the "
            "CLI recognises it as a deployable script asset."
        )


def test_wmill_yaml_excludes_matches_legacy_path():
    """`excludes:` MUST be a YAML list with a glob matching legacy.ts."""
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert os.path.isfile(wmill_yaml), (
        f"wmill.yaml is missing at {wmill_yaml}; the agent must not delete it."
    )
    with open(wmill_yaml, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert isinstance(cfg, dict), (
        f"wmill.yaml must be a YAML mapping at the top level; got: {cfg!r}"
    )

    excludes = cfg.get("excludes")
    assert isinstance(excludes, list) and len(excludes) > 0, (
        "wmill.yaml must have a non-empty `excludes:` list to protect the "
        "pre-existing remote legacy.ts script from `wmill sync push --yes`. "
        f"Got: {excludes!r}"
    )

    safe_id = _safe_id()
    legacy_path = f"f/{_folder_name(safe_id)}/legacy.ts"
    matched = [
        entry for entry in excludes
        if isinstance(entry, str) and fnmatch.fnmatch(legacy_path, entry)
    ]
    assert matched, (
        f"No entry in `excludes:` matches {legacy_path!r} under fnmatch "
        f"semantics. Got excludes={excludes!r}."
    )


def test_remote_legacy_script_still_exists():
    """Pre-seeded legacy.ts must still be on the remote workspace after sync push."""
    safe_id = _safe_id()
    workspace = _workspace()
    path = _remote_path(safe_id, "legacy")
    resp = _get_remote_script(workspace, path)
    assert resp.status_code == 200, (
        f"GET scripts/get/p/{path} returned {resp.status_code}: {resp.text}. "
        "The pre-seeded legacy script appears to have been deleted by "
        "`wmill sync push --yes` — the `excludes:` glob did not protect it."
    )
    body = resp.json()
    assert body.get("path") == path, (
        f"Remote legacy script reports unexpected path: {body!r}"
    )


@pytest.mark.parametrize(
    "name,expected_language",
    [
        ("alpha", "bun"),
        ("beta", "bun"),
        ("gamma", "python3"),
    ],
)
def test_remote_new_scripts_were_deployed(name: str, expected_language: str):
    safe_id = _safe_id()
    workspace = _workspace()
    path = _remote_path(safe_id, name)
    resp = _get_remote_script(workspace, path)
    assert resp.status_code == 200, (
        f"GET scripts/get/p/{path} returned {resp.status_code}: {resp.text}. "
        f"Script {name!r} was not deployed by `wmill sync push --yes`."
    )
    body = resp.json()
    assert body.get("path") == path, (
        f"Remote {name!r} script reports unexpected path: {body!r}"
    )
    assert body.get("language") == expected_language, (
        f"Remote {name!r} script reports language={body.get('language')!r}; "
        f"expected {expected_language!r}."
    )


def test_alpha_script_runtime_invocation():
    """`wmill script run` against the deployed alpha script must succeed."""
    safe_id = _safe_id()
    probe = f"harbor-probe-{safe_id}"
    deployed_path = _remote_path(safe_id, "alpha")
    payload = json.dumps({"message": probe})

    env = os.environ.copy()
    result = subprocess.run(
        ["wmill", "script", "run", deployed_path, "-d", payload],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert result.returncode == 0, (
        f"`wmill script run {deployed_path}` failed (rc={result.returncode}).\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )

    parsed = _extract_last_json(result.stdout)
    assert isinstance(parsed, dict), (
        f"Expected JSON object result; got {type(parsed).__name__}: {parsed!r}"
    )
    assert parsed.get("script") == "alpha", (
        f"Expected result.script == 'alpha'; got {parsed!r}"
    )
    assert parsed.get("echo") == probe, (
        f"Expected result.echo == {probe!r}; got {parsed!r}"
    )


def test_zz_cleanup_remote_scripts():
    """Best-effort cleanup. Failures here MUST NOT fail the test suite."""
    try:
        safe_id = _safe_id()
        workspace = _workspace()
    except Exception:
        return
    for name in ("legacy", "alpha", "beta", "gamma"):
        _archive_remote_script(workspace, _remote_path(safe_id, name))
