import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

import pytest

PROJECT_DIR = "/home/user/project"
LOCAL_FOLDER_DIR = os.path.join(PROJECT_DIR, "f", "eval")
VARIABLE_PATH = "f/eval/session_token"
INITIAL_VALUE = "INITIAL_SECRET"
WINDMILL_BASE_URL = "https://app.windmill.dev"
WMILL_WORKSPACE_ALIAS = "evaluation"


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    assert value, f"Environment variable {name} must be set in the evaluation environment."
    return value


def _api_request(method: str, path: str, *, body: dict | None = None) -> tuple[int, str]:
    token = _required_env("WINDMILL_TOKEN")
    workspace = _required_env("WINDMILL_WORKSPACE")
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, headers=headers, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # nosec - trusted external API
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_environment():
    """Prepare the local Windmill workspace folder and seed the cloud workspace state."""
    token = _required_env("WINDMILL_TOKEN")
    workspace = _required_env("WINDMILL_WORKSPACE")

    # 1. Ensure the on-disk project directory exists and looks like a wmill workspace.
    os.makedirs(PROJECT_DIR, exist_ok=True)
    os.makedirs(LOCAL_FOLDER_DIR, exist_ok=True)

    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    if not os.path.isfile(wmill_yaml):
        with open(wmill_yaml, "w", encoding="utf-8") as f:
            # A minimal wmill.yaml describing the default sync layout.
            f.write(
                "defaultTs: bun\n"
                "includes:\n"
                "  - f/**\n"
                "excludes: []\n"
                "codebases: []\n"
            )

    folder_meta = os.path.join(LOCAL_FOLDER_DIR, "folder.meta.yaml")
    if not os.path.isfile(folder_meta):
        with open(folder_meta, "w", encoding="utf-8") as f:
            f.write("summary: Evaluation folder\nowners: []\nextra_perms: {}\n")

    # 2. Register the workspace with the wmill CLI (idempotent).
    subprocess.run(
        [
            "wmill",
            "workspace",
            "add",
            WMILL_WORKSPACE_ALIAS,
            workspace,
            WINDMILL_BASE_URL,
            "--token",
            token,
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    subprocess.run(
        ["wmill", "workspace", "switch", WMILL_WORKSPACE_ALIAS],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )

    # 3. Ensure the remote `eval` folder exists.
    status, _ = _api_request("GET", "/folders/get/eval")
    if status == 404:
        _api_request(
            "POST",
            "/folders/create",
            body={
                "name": "eval",
                "summary": "Evaluation folder",
                "owners": [],
                "extra_perms": {},
            },
        )

    # 4. Ensure the secret variable exists with the expected initial value.
    status, _ = _api_request("GET", f"/variables/get/{VARIABLE_PATH}")
    if status == 404:
        create_status, create_body = _api_request(
            "POST",
            "/variables/create",
            body={
                "path": VARIABLE_PATH,
                "value": INITIAL_VALUE,
                "is_secret": True,
                "description": "Evaluation session token (rotated by the task script).",
            },
        )
        assert create_status < 400, (
            f"Failed to create variable {VARIABLE_PATH}: status={create_status} body={create_body!r}"
        )
    else:
        update_status, update_body = _api_request(
            "POST",
            f"/variables/update/{VARIABLE_PATH}",
            body={"value": INITIAL_VALUE, "is_secret": True},
        )
        assert update_status < 400, (
            f"Failed to reset variable {VARIABLE_PATH} to initial value: status={update_status} body={update_body!r}"
        )

    yield


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, "wmill CLI was not found in PATH."


def test_bun_runtime_available():
    assert shutil.which("bun") is not None, (
        "bun runtime (required by Windmill TypeScript scripts) was not found in PATH."
    )


def test_required_env_vars_present():
    for name in ("WINDMILL_TOKEN", "WINDMILL_WORKSPACE"):
        assert os.environ.get(name), f"Environment variable {name} is required but is not set."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_project_is_initialized_windmill_workspace():
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert os.path.isfile(wmill_yaml), (
        f"Expected a Windmill workspace configuration at {wmill_yaml}."
    )


def test_eval_folder_exists_on_disk():
    assert os.path.isdir(LOCAL_FOLDER_DIR), (
        f"Expected the local folder {LOCAL_FOLDER_DIR} representing the `f/eval` Windmill folder to exist."
    )


def test_var_rotate_script_not_yet_created():
    script_path = os.path.join(LOCAL_FOLDER_DIR, "var_rotate.ts")
    assert not os.path.exists(script_path), (
        f"Expected {script_path} to not yet exist before the agent runs."
    )


def test_remote_variable_exists_with_initial_value():
    token = _required_env("WINDMILL_TOKEN")
    workspace = _required_env("WINDMILL_WORKSPACE")
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/variables/get_value/{VARIABLE_PATH}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosec
            body = resp.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        pytest.fail(
            f"Failed to query the initial value of variable {VARIABLE_PATH} from Windmill Cloud: {exc!r}"
        )
    try:
        decoded = json.loads(body)
    except json.JSONDecodeError:
        decoded = body
    assert decoded == INITIAL_VALUE, (
        f"Expected the initial value of {VARIABLE_PATH} to be {INITIAL_VALUE!r}, got {decoded!r}."
    )


def test_remote_variable_is_marked_secret():
    status, body = _api_request("GET", f"/variables/get/{VARIABLE_PATH}")
    assert status == 200, (
        f"Failed to fetch variable metadata for {VARIABLE_PATH}: status={status} body={body!r}"
    )
    payload = json.loads(body)
    assert payload.get("is_secret") is True, (
        f"Expected variable {VARIABLE_PATH} to be marked as a secret; got payload {payload!r}."
    )


def test_wmill_workspace_is_configured():
    result = subprocess.run(
        ["wmill", "workspace", "whoami"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        "Expected `wmill workspace whoami` to succeed, indicating the evaluation workspace is configured. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
