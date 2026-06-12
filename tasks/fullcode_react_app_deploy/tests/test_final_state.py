import os
import re
import glob

import pytest
import requests
import yaml

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    assert value, f"Required environment variable {name} is not set."
    return value


def _ids() -> tuple[str, str]:
    run_id = _env("ZEALT_RUN_ID")
    safe_run_id = run_id.replace("-", "_")
    return run_id, safe_run_id


def _base_url() -> str:
    return os.environ.get("WM_BASE_URL", "https://app.windmill.dev").rstrip("/")


def _scaffold_dir() -> str:
    _, safe_run_id = _ids()
    base = os.path.join(PROJECT_DIR, "f", "harbor")
    assert os.path.isdir(base), (
        f"Expected scaffold parent directory {base} to exist."
    )
    candidates = [
        os.path.join(base, f"fullcode_{safe_run_id}.raw_app"),
        os.path.join(base, f"fullcode_{safe_run_id}__raw_app"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    raise AssertionError(
        f"Could not find Full-Code App scaffold directory; expected one of: {candidates}"
    )


def test_scaffold_directory_layout():
    scaffold = _scaffold_dir()
    for required in ("raw_app.yaml", "package.json", "index.tsx", "App.tsx"):
        path = os.path.join(scaffold, required)
        assert os.path.isfile(path), (
            f"Expected required scaffold file {required} at {path} but it was not found."
        )
    backend_dir = os.path.join(scaffold, "backend")
    assert os.path.isdir(backend_dir), (
        f"Expected backend/ subdirectory at {backend_dir} but it was not found."
    )
    ts_files = [
        f for f in os.listdir(backend_dir)
        if f.endswith(".ts") and not f.endswith(".d.ts")
    ]
    assert ts_files, (
        f"Expected at least one *.ts backend runnable in {backend_dir}, found: "
        f"{os.listdir(backend_dir)}"
    )
    yaml_files = [f for f in os.listdir(backend_dir) if f.endswith(".yaml")]
    assert yaml_files, (
        f"Expected at least one *.yaml backend metadata file in {backend_dir}, "
        f"found: {os.listdir(backend_dir)}"
    )


def test_frontend_uses_auto_generated_wmill_client():
    scaffold = _scaffold_dir()
    tsx_files = [
        os.path.join(scaffold, f)
        for f in os.listdir(scaffold)
        if f.endswith(".tsx")
    ]
    assert tsx_files, f"No frontend .tsx files found in {scaffold}."

    import_re = re.compile(
        r"""import\s+[^;]*?from\s+['"](\./wmill(?:\.ts|\.tsx)?)['"]""",
        re.DOTALL,
    )
    call_re = re.compile(
        r"\b(?:backend|backendAsync)\.[A-Za-z_][A-Za-z0-9_]*\s*\(|"
        r"\bwaitJob\s*\(|\bgetJob\s*\(|\bstreamJob\s*\("
    )

    has_import = False
    has_call = False
    for path in tsx_files:
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        if import_re.search(content):
            has_import = True
        if call_re.search(content):
            has_call = True

    assert has_import, (
        "No frontend .tsx file in the scaffold root imports from the auto-generated "
        "'./wmill' client module."
    )
    assert has_call, (
        "No frontend .tsx file calls the auto-generated client "
        "(expected backend.<name>(...), backendAsync.<name>(...), waitJob(...), "
        "getJob(...), or streamJob(...))."
    )


def test_raw_app_yaml_public_and_custom_path():
    run_id, _ = _ids()
    scaffold = _scaffold_dir()
    with open(os.path.join(scaffold, "raw_app.yaml"), encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), "raw_app.yaml did not parse as a YAML mapping."
    assert data.get("public") is True, (
        f"raw_app.yaml must set `public: true`; got: {data.get('public')!r}"
    )
    expected_custom = f"harbor-fullcode-{run_id}"
    assert data.get("custom_path") == expected_custom, (
        f"raw_app.yaml must set `custom_path: {expected_custom}`; "
        f"got: {data.get('custom_path')!r}"
    )


def test_app_deployed_via_windmill_api():
    _, safe_run_id = _ids()
    workspace = _env("WM_WORKSPACE")
    token = _env("WM_TOKEN")
    base = _base_url()
    path = f"f/harbor/fullcode_{safe_run_id}"
    url = f"{base}/api/w/{workspace}/apps/get/p/{path}"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    assert response.status_code == 200, (
        f"GET {url} expected HTTP 200, got {response.status_code}: {response.text[:500]}"
    )
    try:
        body = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"Windmill API response was not valid JSON: {response.text[:500]}"
        ) from exc
    assert body.get("path") == path, (
        f"Expected app `path` to be {path!r}, got {body.get('path')!r} in response."
    )


def test_public_custom_path_http_ok():
    run_id, _ = _ids()
    base = _base_url()
    url = f"{base}/apps/custom/harbor-fullcode-{run_id}"
    response = requests.get(url, timeout=30, allow_redirects=True)
    assert response.status_code == 200, (
        f"Unauthenticated GET {url} expected HTTP 200, got {response.status_code}: "
        f"{response.text[:500]}"
    )


def test_log_contains_app_url():
    run_id, _ = _ids()
    base = _base_url()
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}."
    with open(LOG_FILE, encoding="utf-8") as fh:
        content = fh.read()
    expected_line = f"App URL: {base}/apps/custom/harbor-fullcode-{run_id}"
    assert expected_line in content, (
        f"Expected log line {expected_line!r} in {LOG_FILE}; got:\n{content}"
    )
