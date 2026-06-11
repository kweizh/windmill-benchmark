import json
import os
import re
import subprocess

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PY = os.path.join(PROJECT_DIR, "f", "eval", "exec_counter.py")
SCRIPT_YAML = os.path.join(PROJECT_DIR, "f", "eval", "exec_counter.script.yaml")

WINDMILL_BASE_URL = os.environ.get("WINDMILL_BASE_URL", "https://app.windmill.dev").rstrip("/")
WINDMILL_TOKEN = os.environ.get("WINDMILL_TOKEN", "")
WINDMILL_WORKSPACE = os.environ.get("WINDMILL_WORKSPACE", "")
SCRIPT_REMOTE_PATH = "f/eval/exec_counter"
STATE_RESOURCE_PATH = f"{SCRIPT_REMOTE_PATH}/user"


def _auth_headers():
    return {"Authorization": f"Bearer {WINDMILL_TOKEN}"}


def _delete_state_resource():
    """Best-effort reset of the persisted Windmill state for the deployed script.

    The Windmill state is stored as a `state`-typed resource whose path matches
    `<script_path>/<trigger>` where the trigger is the literal string ``user``
    for ad-hoc executions. Deleting it ensures the counter starts from `None`.
    A `404` is treated as success.
    """
    url = (
        f"{WINDMILL_BASE_URL}/api/w/{WINDMILL_WORKSPACE}/resources/delete/"
        f"{STATE_RESOURCE_PATH}"
    )
    try:
        resp = requests.delete(url, headers=_auth_headers(), timeout=30)
    except requests.RequestException as exc:  # pragma: no cover - network sanity
        raise RuntimeError(f"Failed to contact Windmill API at {url}: {exc}") from exc
    if resp.status_code not in (200, 204, 404):
        raise RuntimeError(
            f"Unexpected status {resp.status_code} from Windmill while deleting "
            f"state resource at {STATE_RESOURCE_PATH}: {resp.text}"
        )


def _run_wmill_script(timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["wmill", "script", "run", SCRIPT_REMOTE_PATH, "-s"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=timeout,
    )


def _parse_last_json(stdout: str):
    """Locate the trailing JSON object emitted by `wmill script run -s`."""
    stripped = stdout.strip()
    if not stripped:
        return None
    # Try whole stdout first.
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    # Fall back to the last non-empty line.
    for line in reversed(stripped.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return None


@pytest.fixture(scope="module")
def script_source() -> str:
    assert os.path.isfile(SCRIPT_PY), (
        f"Expected Python script at {SCRIPT_PY} to be authored by the agent."
    )
    with open(SCRIPT_PY, "r", encoding="utf-8") as fh:
        return fh.read()


def test_script_yaml_exists_and_declares_python3():
    assert os.path.isfile(SCRIPT_YAML), (
        f"Expected companion metadata file at {SCRIPT_YAML}."
    )
    with open(SCRIPT_YAML, "r", encoding="utf-8") as fh:
        content = fh.read()
    assert re.search(r"(?mi)^\s*language\s*:\s*python3\s*$", content), (
        "The .script.yaml must declare `language: python3` so Windmill executes the "
        "script with the Python runtime."
    )


def test_script_imports_wmill(script_source: str):
    has_import = re.search(r"(?m)^\s*import\s+wmill\b", script_source) is not None
    has_from = re.search(r"(?m)^\s*from\s+wmill\b", script_source) is not None
    assert has_import or has_from, (
        "The script must import the `wmill` SDK (e.g. `import wmill`)."
    )


def test_script_uses_get_state_and_set_state(script_source: str):
    assert "get_state(" in script_source, (
        "The script body must call `get_state(` from the wmill SDK to read the "
        "persisted counter."
    )
    assert "set_state(" in script_source, (
        "The script body must call `set_state(` from the wmill SDK to persist the "
        "incremented counter."
    )


def test_script_defines_zero_arg_main(script_source: str):
    assert re.search(r"(?m)^\s*def\s+main\s*\(\s*\)\s*:", script_source), (
        "The script must define a `def main():` entrypoint with no arguments."
    )


def test_script_does_not_hardcode_3(script_source: str):
    # Strip out comments and string literals before scanning so that a docstring
    # containing the word "3" is tolerated, but actual code is not.
    cleaned_lines = []
    for raw_line in script_source.splitlines():
        line = re.sub(r"#.*$", "", raw_line)
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"'''.*?'''", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'""".*?"""', "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"'(?:\\.|[^'\\])*'", "", cleaned)
    cleaned = re.sub(r'"(?:\\.|[^"\\])*"', "", cleaned)
    assert "3" not in cleaned, (
        "The Python script must not hard-code the digit `3` anywhere in executable "
        "code; the counter must come from `wmill.get_state` / `wmill.set_state`."
    )


def test_three_sequential_runs_increment_state_to_3():
    assert WINDMILL_TOKEN, "WINDMILL_TOKEN must be set in the verifier environment."
    assert WINDMILL_WORKSPACE, (
        "WINDMILL_WORKSPACE must be set in the verifier environment."
    )

    # Ensure the persisted counter starts from a clean slate.
    _delete_state_resource()

    last_result = None
    for attempt in range(1, 4):
        proc = _run_wmill_script()
        assert proc.returncode == 0, (
            f"Run #{attempt} of `wmill script run {SCRIPT_REMOTE_PATH}` failed with "
            f"exit code {proc.returncode}.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
        last_result = _parse_last_json(proc.stdout)
        assert last_result is not None, (
            f"Run #{attempt} produced unparseable stdout (expected a JSON object).\n"
            f"stdout was:\n{proc.stdout}"
        )

    assert isinstance(last_result, dict), (
        "The third invocation must return a JSON object as its result, but got: "
        f"{last_result!r}"
    )
    assert last_result.get("runs") == 3, (
        "After three sequential invocations the persisted `runs` counter must equal "
        f"3, but the third invocation returned: {last_result!r}"
    )
