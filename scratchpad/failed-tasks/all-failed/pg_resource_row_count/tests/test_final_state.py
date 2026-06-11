import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "f", "eval", "pg_row_count.ts")
METADATA_PATH = os.path.join(PROJECT_DIR, "f", "eval", "pg_row_count.script.yaml")


# ---------- File / source level checks ----------


def test_script_file_exists() -> None:
    """Final state: the agent must have authored f/eval/pg_row_count.ts."""
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the script file '{SCRIPT_PATH}' to exist in the workspace folder "
        "synced from the agent's submission."
    )


def test_metadata_file_exists() -> None:
    """The companion .script.yaml metadata file must also be present."""
    assert os.path.isfile(METADATA_PATH), (
        f"Expected the metadata file '{METADATA_PATH}' to exist alongside the script."
    )


def test_script_imports_windmill_client() -> None:
    """The script must import the windmill-client package."""
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(r"""from\s+['"]windmill-client['"]""")
    assert pattern.search(content) is not None, (
        "The script must import from 'windmill-client' "
        "(e.g., `import * as wmill from \"windmill-client\"`)."
    )


def test_script_signature_main_pg_postgresql() -> None:
    """The script must export `async function main(pg: Postgresql)`."""
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    # Tolerant of extra spaces and additional trailing parameters / closing paren on next line.
    pattern = re.compile(
        r"export\s+async\s+function\s+main\s*\(\s*pg\s*:\s*Postgresql\b",
    )
    assert pattern.search(content) is not None, (
        "The script must export an async function with the signature "
        "`export async function main(pg: Postgresql)` (the first parameter must be "
        "literally named `pg` and typed as `Postgresql`)."
    )


# ---------- End-to-end CLI verification ----------


def _wmill_env() -> dict:
    env = os.environ.copy()
    # Ensure the cloud credentials are present; both are populated via envs.json.
    assert env.get("WINDMILL_TOKEN"), (
        "WINDMILL_TOKEN is required for the verifier to call the cloud workspace."
    )
    assert env.get("WINDMILL_WORKSPACE"), (
        "WINDMILL_WORKSPACE is required to identify the target workspace."
    )
    return env


def test_script_push_succeeds() -> None:
    """Re-push the agent's local script to make sure the cloud workspace has the latest version."""
    env = _wmill_env()
    result = subprocess.run(
        ["wmill", "script", "push", "f/eval/pg_row_count.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    assert result.returncode == 0, (
        "Failed to push the script to the cloud workspace: "
        f"stdout={result.stdout[-1000:]!r}, stderr={result.stderr[-1000:]!r}"
    )


def test_wmill_script_run_returns_nonnegative_integer_count() -> None:
    """End-to-end: run the script remotely with the seeded resource and validate the JSON output."""
    env = _wmill_env()
    result = subprocess.run(
        [
            "wmill",
            "script",
            "run",
            "f/eval/pg_row_count",
            "-d",
            '{"pg": "$res:f/eval/pg_resource"}',
            "-s",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    assert result.returncode == 0, (
        "`wmill script run f/eval/pg_row_count` exited with non-zero code: "
        f"code={result.returncode}, stdout={result.stdout[-1500:]!r}, "
        f"stderr={result.stderr[-1500:]!r}"
    )

    stdout = (result.stdout or "").strip()
    assert stdout, (
        f"`wmill script run` produced no stdout. stderr={result.stderr[-1500:]!r}"
    )

    # The CLI may print log lines before the final JSON result. Find the JSON
    # object that contains a `count` field — we don't enforce a specific value.
    payload = None
    last_error: Exception | None = None

    # Try whole stdout first.
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        last_error = exc

    # Try last non-empty line.
    if not isinstance(payload, dict) or "count" not in payload:
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                candidate = json.loads(line)
            except json.JSONDecodeError as exc:
                last_error = exc
                continue
            if isinstance(candidate, dict) and "count" in candidate:
                payload = candidate
                break

    # Try to extract the last balanced JSON object from stdout.
    if not isinstance(payload, dict) or "count" not in payload:
        matches = re.findall(r"\{[\s\S]*?\}", stdout)
        for candidate_str in reversed(matches):
            try:
                candidate = json.loads(candidate_str)
            except json.JSONDecodeError as exc:
                last_error = exc
                continue
            if isinstance(candidate, dict) and "count" in candidate:
                payload = candidate
                break

    assert isinstance(payload, dict) and "count" in payload, (
        "Could not locate a JSON object containing a `count` field in the script "
        f"output. last_decode_error={last_error!r}, stdout={stdout[-1500:]!r}"
    )

    count = payload["count"]
    # Accept booleans? Booleans are technically int subclasses in Python; explicitly reject.
    assert isinstance(count, int) and not isinstance(count, bool), (
        f"`count` field must be an integer, got {type(count).__name__}={count!r}."
    )
    assert count >= 0, f"`count` field must be >= 0, got {count}."
