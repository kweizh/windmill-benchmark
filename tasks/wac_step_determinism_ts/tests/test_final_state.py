import json
import os
import re

import pytest
import requests


PROJECT_DIR = "/home/user/myproject"
BASE_URL = os.environ.get("WMILL_BASE_URL", "https://app.windmill.dev")
TOKEN = os.environ.get("WMILL_TOKEN", "")
WORKSPACE = os.environ.get("WMILL_WORKSPACE", "evaluation-ws")
RUN_ID = os.environ.get("ZEALT_RUN_ID", "")

SCRIPT_PATH = f"f/zealt_{RUN_ID}/wac_step_determinism"
LOCAL_TS_FILE = os.path.join(PROJECT_DIR, f"f/zealt_{RUN_ID}/wac_step_determinism.ts")
LOCAL_YAML_FILE = os.path.join(PROJECT_DIR, f"f/zealt_{RUN_ID}/wac_step_determinism.script.yaml")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")

ISO_TS_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})$"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _auth_headers():
    return {"Authorization": f"Bearer {TOKEN}"}


def _strip_step_calls(source: str) -> str:
    """Remove every `step(...)` call (including its callback body) from the source.

    The remaining text represents the workflow body excluding step wrappers. We
    use it to assert that no unwrapped non-deterministic calls live directly in
    the workflow body.
    """
    out_chars = []
    i = 0
    n = len(source)
    while i < n:
        # Look for `step(` as a token boundary
        if (
            source[i:i + 5] == "step("
            and (i == 0 or not (source[i - 1].isalnum() or source[i - 1] == "_"))
        ):
            depth = 1
            j = i + 5
            in_str = None
            escape = False
            while j < n and depth > 0:
                ch = source[j]
                if in_str:
                    if escape:
                        escape = False
                    elif ch == "\\":
                        escape = True
                    elif ch == in_str:
                        in_str = None
                elif ch in ("'", '"', "`"):
                    in_str = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                j += 1
            i = j  # skip past closing paren
        else:
            out_chars.append(source[i])
            i += 1
    return "".join(out_chars)


def test_run_id_present():
    assert RUN_ID, "ZEALT_RUN_ID is required for verification."


def test_local_ts_source_exists():
    assert os.path.isfile(LOCAL_TS_FILE), (
        f"Expected WAC TypeScript source at {LOCAL_TS_FILE}"
    )


def test_local_yaml_metadata_exists():
    assert os.path.isfile(LOCAL_YAML_FILE), (
        f"Expected WAC script metadata at {LOCAL_YAML_FILE}"
    )


def test_local_source_uses_step_and_workflow_imports():
    with open(LOCAL_TS_FILE) as f:
        src = f.read()
    assert ("from \"windmill-client\"" in src) or ("from 'windmill-client'" in src), (
        "Source must import from 'windmill-client'."
    )
    assert re.search(r"\bstep\b", src), "Source must reference `step`."
    assert re.search(r"\bworkflow\b", src), "Source must reference `workflow`."


def test_local_source_uses_init_time_step():
    with open(LOCAL_TS_FILE) as f:
        src = f.read()
    assert (
        'step("init_time"' in src or "step('init_time'" in src
    ), 'Source must contain a literal step("init_time", ...) checkpoint call.'


def test_local_source_has_no_unwrapped_nondeterminism():
    with open(LOCAL_TS_FILE) as f:
        src = f.read()
    stripped = _strip_step_calls(src)
    forbidden = ["Date.now", "new Date", "Math.random", "fetch("]
    leaked = [tok for tok in forbidden if tok in stripped]
    assert not leaked, (
        "Workflow body contains unwrapped non-deterministic calls outside step(...) wrappers: "
        f"{leaked}. All such calls must live inside `step(\"<key>\", () => ...)`."
    )


def test_script_deployed_on_windmill_cloud():
    url = f"{BASE_URL}/api/w/{WORKSPACE}/scripts/get/p/{SCRIPT_PATH}"
    resp = requests.get(url, headers=_auth_headers(), timeout=30)
    assert resp.status_code == 200, (
        f"Windmill script lookup failed for {SCRIPT_PATH}: "
        f"HTTP {resp.status_code} body={resp.text[:500]}"
    )
    data = resp.json()
    language = data.get("language") or ""
    assert language in ("bun", "deno", "nativets", "typescript"), (
        f"Deployed script language expected to be TypeScript-family, got {language!r}."
    )
    content = data.get("content") or ""
    assert (
        'step("init_time"' in content or "step('init_time'" in content
    ), "Deployed script content must contain step(\"init_time\", ...)."
    assert "workflow(" in content, "Deployed script content must use workflow(...)."


def test_output_log_present_and_parseable():
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}"
    with open(LOG_FILE) as f:
        text = f.read()
    uuid_match = re.search(r"Job UUID:\s*([0-9a-fA-F-]+)", text)
    assert uuid_match, "Log must contain a `Job UUID: <uuid>` line."
    job_uuid = uuid_match.group(1).strip()
    assert UUID_RE.match(job_uuid), f"Job UUID {job_uuid!r} is not a valid UUID."

    result_match = re.search(r"Result:\s*(\{.*\})", text, re.DOTALL)
    assert result_match, "Log must contain a `Result: <json>` line."
    raw_json = result_match.group(1).strip()
    try:
        result_obj = json.loads(raw_json)
    except json.JSONDecodeError as e:
        pytest.fail(f"Result JSON in log is not valid JSON: {e}; raw={raw_json!r}")
    assert isinstance(result_obj, dict), (
        f"Result in log must be a JSON object, got {type(result_obj).__name__}."
    )


def _read_log_uuid_and_result():
    with open(LOG_FILE) as f:
        text = f.read()
    uuid_match = re.search(r"Job UUID:\s*([0-9a-fA-F-]+)", text)
    result_match = re.search(r"Result:\s*(\{.*\})", text, re.DOTALL)
    assert uuid_match and result_match, "Log file missing required UUID/Result lines."
    return uuid_match.group(1).strip(), json.loads(result_match.group(1).strip())


def test_job_completed_successfully_on_cloud():
    job_uuid, _ = _read_log_uuid_and_result()
    url = f"{BASE_URL}/api/w/{WORKSPACE}/jobs_u/completed/get/{job_uuid}"
    resp = requests.get(url, headers=_auth_headers(), timeout=30)
    assert resp.status_code == 200, (
        f"Could not fetch completed job {job_uuid}: HTTP {resp.status_code} body={resp.text[:500]}"
    )
    job = resp.json()
    assert job.get("success") is True, (
        f"Windmill job {job_uuid} did not succeed: success={job.get('success')!r}, "
        f"result={job.get('result')!r}"
    )
    result = job.get("result")
    assert isinstance(result, dict), (
        f"Windmill job result must be a JSON object, got {type(result).__name__}: {result!r}"
    )


def test_result_schema_timestamp_and_derived_field():
    job_uuid, log_result = _read_log_uuid_and_result()

    # Fetch server-side result
    url = f"{BASE_URL}/api/w/{WORKSPACE}/jobs_u/completed/get/{job_uuid}"
    resp = requests.get(url, headers=_auth_headers(), timeout=30)
    assert resp.status_code == 200, f"Failed to fetch job {job_uuid}: HTTP {resp.status_code}"
    server_result = resp.json().get("result")
    assert isinstance(server_result, dict), "Server-side result must be a JSON object."

    # Server and log must agree
    assert server_result == log_result, (
        "Server-side result and locally logged result must match. "
        f"server={server_result!r}, log={log_result!r}"
    )

    iso_values = [v for v in server_result.values() if isinstance(v, str) and ISO_TS_RE.match(v)]
    assert iso_values, (
        f"Result must contain an ISO-8601 timestamp string. Got: {server_result!r}"
    )
    iso_ts = iso_values[0]
    expected_date = iso_ts[:10]

    date_values = [
        v for v in server_result.values()
        if isinstance(v, str) and DATE_RE.match(v) and v == expected_date
    ]
    assert date_values, (
        "Result must contain a downstream YYYY-MM-DD field equal to the first 10 chars of the "
        f"captured timestamp {iso_ts!r} (expected {expected_date!r}). Got: {server_result!r}"
    )
