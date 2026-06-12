import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "script.ts")


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _schema(run_id: str) -> str:
    return f"zr_{run_id}"


def _script_path_remote(run_id: str) -> str:
    return f"f/{_schema(run_id)}/query_events"


def _extract_json_object(text: str):
    """Find the last JSON object/array in CLI stdout."""
    # Prefer matching a balanced object or array at the tail of the output.
    candidates = re.findall(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
    for cand in reversed(candidates):
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            continue
    # Last resort: try parsing the whole stdout.
    return json.loads(text.strip())


def _run_query(kind: str, run_id: str):
    payload = json.dumps({"kind": kind})
    result = subprocess.run(
        [
            "wmill",
            "script",
            "run",
            _script_path_remote(run_id),
            "-d",
            payload,
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"`wmill script run {_script_path_remote(run_id)} -d {payload}` failed "
        f"with exit {result.returncode}. stdout={result.stdout!r}, stderr={result.stderr!r}"
    )
    data = _extract_json_object(result.stdout)
    assert isinstance(data, dict), (
        f"Expected the script to return a JSON object, got: {data!r} "
        f"(stdout={result.stdout!r})"
    )
    assert "count" in data and "rows" in data, (
        f"Expected the returned JSON object to contain 'count' and 'rows' keys. "
        f"Got: {data!r}"
    )
    assert isinstance(data["count"], int), (
        f"Expected 'count' to be an integer. Got: {data['count']!r}"
    )
    assert isinstance(data["rows"], list), (
        f"Expected 'rows' to be a list. Got: {data['rows']!r}"
    )
    return data


def test_script_artifact_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the TypeScript script at {SCRIPT_PATH} to exist."
    )
    content = open(SCRIPT_PATH).read()
    assert "windmill-client" in content, (
        f"Expected {SCRIPT_PATH} to import from 'windmill-client'."
    )
    assert re.search(r"datatable\s*\(", content, flags=re.IGNORECASE), (
        f"Expected {SCRIPT_PATH} to call wmill.datatable() to obtain the Data "
        f"Table client."
    )


def test_script_deployed_to_workspace():
    run_id = _run_id()
    remote_path = _script_path_remote(run_id)
    result = subprocess.run(
        ["wmill", "script", "show", remote_path],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"`wmill script show {remote_path}` failed with exit "
        f"{result.returncode}. stdout={result.stdout!r}, "
        f"stderr={result.stderr!r}"
    )


@pytest.fixture(scope="module")
def seeded_rows():
    """Snapshot the contents of zr_${run_id}.events by deploying an ad-hoc
    verifier script and invoking it through wmill."""
    run_id = _run_id()
    schema = _schema(run_id)
    verifier_dir = os.path.join("/tmp", f"verify_seed_{run_id}")
    os.makedirs(verifier_dir, exist_ok=True)
    verifier_ts = os.path.join(verifier_dir, "verify_seed.ts")
    with open(verifier_ts, "w") as f:
        f.write(
            "import * as wmill from 'windmill-client';\n"
            "export async function main() {\n"
            f"  const sql = wmill.datatable(':{schema}');\n"
            "  const rows = await sql`SELECT id, kind FROM events`.fetch();\n"
            "  return rows;\n"
            "}\n"
        )
    remote_path = f"f/{schema}/verify_seed"
    deploy = subprocess.run(
        [
            "wmill",
            "script",
            "push",
            verifier_ts,
            "--remote-path",
            remote_path,
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    # If `push` is not the right subcommand on this version of the CLI, fall
    # back to `wmill script run` against the local file path (Bun preview).
    if deploy.returncode != 0:
        run = subprocess.run(
            ["wmill", "script", "run", verifier_ts],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert run.returncode == 0, (
            "Both `wmill script push` and `wmill script run <file>` failed for "
            f"the seed verifier. push stderr={deploy.stderr!r}, run "
            f"stderr={run.stderr!r}"
        )
        data = _extract_json_object(run.stdout)
    else:
        run = subprocess.run(
            ["wmill", "script", "run", remote_path],
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert run.returncode == 0, (
            f"`wmill script run {remote_path}` (seed verifier) failed. "
            f"stdout={run.stdout!r}, stderr={run.stderr!r}"
        )
        data = _extract_json_object(run.stdout)
    assert isinstance(data, list), (
        f"Expected the seed verifier to return a JSON array. Got: {data!r}"
    )
    return [(int(r["id"]), str(r["kind"])) for r in data]


EXPECTED_SEED = {
    (1, "login"),
    (2, "logout"),
    (3, "login"),
    (4, "signup"),
    (5, "login"),
}


def test_seed_rows_present(seeded_rows):
    got = set(seeded_rows)
    assert got == EXPECTED_SEED, (
        "events table is not seeded with the expected rows.\n"
        f"  expected: {sorted(EXPECTED_SEED)}\n"
        f"  got:      {sorted(got)}"
    )


def test_query_kind_login_returns_three_rows():
    run_id = _run_id()
    data = _run_query("login", run_id)
    assert data["count"] == 3, (
        f"Expected count==3 for kind='login'. Got: {data!r}"
    )
    got = {(int(r["id"]), str(r["kind"])) for r in data["rows"]}
    expected = {(1, "login"), (3, "login"), (5, "login")}
    assert got == expected, (
        f"Expected rows for kind='login' to equal {sorted(expected)} as a set; "
        f"got {sorted(got)}"
    )


def test_query_kind_signup_returns_one_row():
    run_id = _run_id()
    data = _run_query("signup", run_id)
    assert data["count"] == 1, (
        f"Expected count==1 for kind='signup'. Got: {data!r}"
    )
    got = {(int(r["id"]), str(r["kind"])) for r in data["rows"]}
    expected = {(4, "signup")}
    assert got == expected, (
        f"Expected rows for kind='signup' to equal {sorted(expected)} as a "
        f"set; got {sorted(got)}"
    )


def test_query_kind_missing_returns_empty():
    run_id = _run_id()
    data = _run_query("missing", run_id)
    assert data["count"] == 0, (
        f"Expected count==0 for kind='missing'. Got: {data!r}"
    )
    assert data["rows"] == [], (
        f"Expected rows==[] for kind='missing'. Got: {data!r}"
    )
