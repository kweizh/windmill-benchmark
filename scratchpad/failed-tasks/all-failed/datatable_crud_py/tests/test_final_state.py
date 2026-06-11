import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/wmill-project"
WRITER_PY = os.path.join(PROJECT_DIR, "f", "eval", "datatable_writer.py")
WRITER_YAML = os.path.join(PROJECT_DIR, "f", "eval", "datatable_writer.script.yaml")
READER_PY = os.path.join(PROJECT_DIR, "f", "eval", "datatable_reader.py")
READER_YAML = os.path.join(PROJECT_DIR, "f", "eval", "datatable_reader.script.yaml")

FORBIDDEN_PATTERNS = [
    r"\bpsycopg\b",
    r"\bpsycopg2\b",
    r"\basyncpg\b",
    r"\bpg8000\b",
    r"\bpsql\b",
    r"postgresql://",
    r"postgres://",
]


def _run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "").strip()
    assert rid, "ZEALT_RUN_ID env var is required for verification but missing."
    return rid


def _expected_table_name() -> str:
    return f"eval_orders_{_run_id()}"


def _read(path: str) -> str:
    assert os.path.isfile(path), f"Expected file {path} to exist."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _wmill_run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["wmill", "script", "run", *args, "-s"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=180,
    )


def _parse_json_stdout(stdout: str):
    stdout = stdout.strip()
    # The CLI may emit multiple lines; pick the last non-empty JSON-looking line.
    candidates = [ln for ln in stdout.splitlines() if ln.strip()]
    last_err: Exception | None = None
    for line in reversed(candidates):
        try:
            return json.loads(line)
        except json.JSONDecodeError as exc:  # try the next candidate
            last_err = exc
    # Fallback: try the whole stdout as JSON.
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Could not parse wmill stdout as JSON.\nstdout={stdout!r}\nlast_err={last_err}"
        ) from exc


# ---------------------------------------------------------------------------
# 1. File layout
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "path",
    [WRITER_PY, WRITER_YAML, READER_PY, READER_YAML],
)
def test_required_files_exist(path):
    assert os.path.isfile(path), (
        f"Required Windmill script asset {path} is missing. "
        "Both the .py file and its sibling .script.yaml metadata file must be present."
    )


# ---------------------------------------------------------------------------
# 2. No raw drivers, must use the datatable SDK
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [WRITER_PY, READER_PY])
def test_no_raw_postgres_driver(path):
    content = _read(path).lower()
    for pat in FORBIDDEN_PATTERNS:
        assert not re.search(pat, content), (
            f"File {path} contains forbidden pattern {pat!r}. "
            "Both scripts must use the official `wmill.datatable()` SDK rather than a raw "
            "Postgres driver or connection string."
        )


@pytest.mark.parametrize("path", [WRITER_PY, READER_PY])
def test_uses_datatable_sdk(path):
    content = _read(path)
    assert "wmill" in content, (
        f"File {path} does not reference the wmill SDK at all."
    )
    assert re.search(r"datatable\s*\(", content), (
        f"File {path} must call `wmill.datatable(...)` to obtain a Built-In Data Tables client."
    )


# ---------------------------------------------------------------------------
# 3. Run-id-scoped table name
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [WRITER_PY, READER_PY])
def test_table_name_includes_run_id(path):
    expected = _expected_table_name()
    content = _read(path)
    assert expected in content, (
        f"File {path} must use the run-id-scoped table name {expected!r} so concurrent "
        f"trials do not collide on the shared cloud workspace."
    )


# ---------------------------------------------------------------------------
# 4 & 5. Writer + reader round-trip
# ---------------------------------------------------------------------------

INITIAL_RECORDS = [
    {"id": 1, "status": "new"},
    {"id": 2, "status": "paid"},
    {"id": 3, "status": "shipped"},
]


def test_writer_inserts_records():
    payload = json.dumps({"records": INITIAL_RECORDS})
    result = _wmill_run(["f/eval/datatable_writer", "-d", payload])
    assert result.returncode == 0, (
        f"`wmill script run f/eval/datatable_writer` exited with {result.returncode}.\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    body = _parse_json_stdout(result.stdout)
    assert isinstance(body, dict), f"Writer must return a JSON object, got: {body!r}"
    assert body.get("inserted") == len(INITIAL_RECORDS), (
        f"Writer must return {{'inserted': {len(INITIAL_RECORDS)}}}, got: {body!r}"
    )


def test_reader_returns_inserted_rows_in_id_order():
    # The writer above is a prerequisite. Re-run it to make this test deterministic
    # even if previous test ordering changes.
    payload = json.dumps({"records": INITIAL_RECORDS})
    writer_result = _wmill_run(["f/eval/datatable_writer", "-d", payload])
    assert writer_result.returncode == 0, (
        f"Pre-populating writer failed: {writer_result.stderr!r}"
    )

    reader_result = _wmill_run(["f/eval/datatable_reader"])
    assert reader_result.returncode == 0, (
        f"`wmill script run f/eval/datatable_reader` exited with "
        f"{reader_result.returncode}.\nstdout={reader_result.stdout!r}\n"
        f"stderr={reader_result.stderr!r}"
    )

    body = _parse_json_stdout(reader_result.stdout)
    assert isinstance(body, dict), f"Reader must return a JSON object, got: {body!r}"
    rows = body.get("rows")
    assert isinstance(rows, list), f"Reader response must contain a 'rows' list, got: {body!r}"

    projected = [{"id": r.get("id"), "status": r.get("status")} for r in rows]
    projected_sorted = sorted(projected, key=lambda r: r["id"])
    assert projected_sorted == INITIAL_RECORDS, (
        f"Expected rows (sorted by id) to equal {INITIAL_RECORDS}, "
        f"got: {projected_sorted}"
    )
    # rows must already be sorted by id ascending per the acceptance criteria.
    assert projected == sorted(projected, key=lambda r: r["id"]), (
        f"Reader must return rows sorted by id ascending, got: {projected}"
    )


# ---------------------------------------------------------------------------
# 6. Second-run idempotency
# ---------------------------------------------------------------------------

SECOND_RECORDS = [
    {"id": 10, "status": "refund"},
    {"id": 11, "status": "void"},
]


def test_second_writer_run_then_reader():
    payload = json.dumps({"records": SECOND_RECORDS})
    writer_result = _wmill_run(["f/eval/datatable_writer", "-d", payload])
    assert writer_result.returncode == 0, (
        f"Second writer run failed: stdout={writer_result.stdout!r} "
        f"stderr={writer_result.stderr!r}"
    )
    body = _parse_json_stdout(writer_result.stdout)
    assert body.get("inserted") == len(SECOND_RECORDS), (
        f"Second writer must return {{'inserted': {len(SECOND_RECORDS)}}}, got: {body!r}"
    )

    reader_result = _wmill_run(["f/eval/datatable_reader"])
    assert reader_result.returncode == 0, (
        f"Reader after second write failed: {reader_result.stderr!r}"
    )
    reader_body = _parse_json_stdout(reader_result.stdout)
    rows = reader_body.get("rows")
    assert isinstance(rows, list), f"Reader must return a 'rows' list, got: {reader_body!r}"

    projected = [{"id": r.get("id"), "status": r.get("status")} for r in rows]
    for expected in SECOND_RECORDS:
        assert expected in projected, (
            f"Expected record {expected} to appear in reader response, got: {projected}"
        )

    new_only = [r for r in projected if r in SECOND_RECORDS]
    assert new_only == sorted(new_only, key=lambda r: r["id"]), (
        f"Reader must return the new records sorted by id ascending, got: {new_only}"
    )
