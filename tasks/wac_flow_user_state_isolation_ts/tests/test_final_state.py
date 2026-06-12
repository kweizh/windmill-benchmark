import json
import os
import re
import subprocess


PROJECT_DIR = "/home/user/wac_accumulator"
LOG_PATH = os.path.join(PROJECT_DIR, "output.log")


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set."
    return run_id


def _script_path() -> str:
    return f"f/zealt_{_run_id()}/wac_accumulator"


def _script_file() -> str:
    return os.path.join(
        PROJECT_DIR, "f", f"zealt_{_run_id()}", "wac_accumulator.ts"
    )


def test_source_file_exists():
    path = _script_file()
    assert os.path.isfile(path), (
        f"Expected WAC TypeScript source at {path} after deployment."
    )


def test_source_imports_windmill_client():
    with open(_script_file(), "r", encoding="utf-8") as f:
        source = f.read()
    assert re.search(r"""from\s+['"]windmill-client['"]""", source), (
        "Source must import from 'windmill-client' (the documented SDK package). "
        f"Got:\n{source}"
    )


def test_source_uses_documented_user_state_sdk_calls():
    with open(_script_file(), "r", encoding="utf-8") as f:
        source = f.read()
    assert "getFlowUserState" in source, (
        "Source must reference the documented SDK identifier 'getFlowUserState'."
    )
    assert "setFlowUserState" in source, (
        "Source must reference the documented SDK identifier 'setFlowUserState'."
    )


def test_source_main_accepts_number_array():
    with open(_script_file(), "r", encoding="utf-8") as f:
        source = f.read()
    # Match async function main(values: number[]) OR Array<number>
    pattern = re.compile(
        r"async\s+function\s+main\s*\(\s*\w+\s*:\s*(number\s*\[\s*\]|Array\s*<\s*number\s*>)",
        re.DOTALL,
    )
    assert pattern.search(source), (
        "Expected `async function main(<name>: number[])` (or `Array<number>`) "
        f"signature. Got:\n{source}"
    )


def test_log_file_exists():
    assert os.path.isfile(LOG_PATH), (
        f"Expected the output log file at {LOG_PATH} after running the flow."
    )


def _parse_runs():
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]

    run_objs = {}
    pattern = re.compile(r"^RUN\s+(\d+)\s+RESULT:\s*(\{.*\})\s*$")
    for ln in lines:
        m = pattern.match(ln)
        if not m:
            continue
        run_idx = int(m.group(1))
        payload = m.group(2)
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError as e:
            raise AssertionError(
                f"Failed to parse JSON from log line {ln!r}: {e}"
            )
        run_objs[run_idx] = obj
    return run_objs


def test_log_contains_two_run_results():
    runs = _parse_runs()
    assert 1 in runs and 2 in runs, (
        "Expected both 'RUN 1 RESULT:' and 'RUN 2 RESULT:' lines in "
        f"{LOG_PATH}. Got runs: {sorted(runs.keys())}"
    )


def test_each_run_has_numeric_accumulator():
    runs = _parse_runs()
    for idx in (1, 2):
        obj = runs[idx]
        assert "accumulator" in obj, (
            f"RUN {idx} result must contain key 'accumulator'. Got: {obj!r}"
        )
        assert isinstance(obj["accumulator"], (int, float)) and not isinstance(
            obj["accumulator"], bool
        ), (
            f"RUN {idx} accumulator must be numeric. Got: {obj['accumulator']!r}"
        )


def test_within_run_accumulation_correct():
    """Run 1's accumulator must equal 1+2+3 = 6, proving the
    per-flow user state correctly carries the running total across steps
    inside a single execution."""
    runs = _parse_runs()
    assert runs[1]["accumulator"] == 6, (
        "Expected RUN 1 accumulator == 6 (sum of [1,2,3]). "
        f"Got: {runs[1]['accumulator']!r}"
    )


def test_runs_are_isolated_from_each_other():
    """Run 2's accumulator must equal Run 1's accumulator, proving that
    flow user state does NOT leak across separate flow runs. If state leaked,
    Run 2 would start at 6 and end at 12 (or larger)."""
    runs = _parse_runs()
    assert runs[1]["accumulator"] == runs[2]["accumulator"], (
        "Per-flow user state must be isolated across runs: both runs should "
        "produce the same final accumulator value. "
        f"Got RUN 1={runs[1]['accumulator']!r}, RUN 2={runs[2]['accumulator']!r}."
    )
    assert runs[2]["accumulator"] == 6, (
        "Expected RUN 2 accumulator == 6 (sum of [1,2,3]) — i.e. state was "
        f"freshly initialized for the second run. Got: {runs[2]['accumulator']!r}"
    )


def test_script_is_deployed_on_cloud_workspace():
    """Use the wmill CLI to confirm the script was actually pushed to
    the Windmill Cloud workspace."""
    result = subprocess.run(
        ["wmill", "script", "list", "--json"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"'wmill script list --json' failed (rc={result.returncode}): "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    try:
        items = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"Could not parse 'wmill script list --json' output as JSON: {e}\n"
            f"stdout was: {result.stdout!r}"
        )
    paths = [item.get("path") for item in items if isinstance(item, dict)]
    expected_path = _script_path()
    assert expected_path in paths, (
        f"Expected the deployed script path {expected_path!r} to appear "
        f"in the workspace script listing. Got paths: {paths!r}"
    )
