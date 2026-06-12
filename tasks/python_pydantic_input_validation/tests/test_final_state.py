import json
import math
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/project"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID must be set during verification."
    return run_id


def _remote_path() -> str:
    return f"f/zealt/pydantic_input_{_run_id()}"


def _local_pair() -> tuple[str, str]:
    base = os.path.join(PROJECT_DIR, "f", "zealt", f"pydantic_input_{_run_id()}")
    return base + ".py", base + ".script.yaml"


def _wmill_run(payload: str) -> subprocess.CompletedProcess[str]:
    """Invoke `wmill script run` from the project directory and capture both streams."""
    return subprocess.run(
        ["wmill", "script", "run", _remote_path(), "-s", "-d", payload],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=180,
    )


def test_script_file_pair_exists():
    """The executor must leave both the .py and .script.yaml files at the documented path."""
    py_path, yaml_path = _local_pair()
    assert os.path.isfile(py_path), (
        f"Python script file not found at {py_path}. Expected the executor to author it."
    )
    assert os.path.isfile(yaml_path), (
        f"Script metadata file not found at {yaml_path}. "
        "Expected the executor to deploy the script (which generates the .script.yaml pair)."
    )


def test_valid_input_returns_expected_json():
    """A valid payload must pass Pydantic validation and produce the expected processed JSON."""
    payload = json.dumps(
        {"data": {"item": "widget", "quantity": 3, "unit_price": 2.5}}
    )
    result = _wmill_run(payload)
    assert result.returncode == 0, (
        f"`wmill script run` with valid input exited with code {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    combined = (result.stdout or "") + "\n" + (result.stderr or "")

    parsed: dict | None = None
    # First try parsing stdout directly as a JSON document.
    stdout_stripped = (result.stdout or "").strip()
    if stdout_stripped:
        try:
            parsed_candidate = json.loads(stdout_stripped)
            if isinstance(parsed_candidate, dict):
                parsed = parsed_candidate
        except json.JSONDecodeError:
            parsed = None

    # Fall back to scanning for the last JSON object embedded in the output.
    if parsed is None:
        matches = re.findall(r"\{[^{}]*\}", combined, flags=re.DOTALL)
        for candidate in reversed(matches):
            try:
                obj = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "item" in obj and "total" in obj:
                parsed = obj
                break

    if parsed is not None:
        assert parsed.get("item") == "widget", (
            f"Expected returned `item` to equal 'widget', got: {parsed!r}"
        )
        total = parsed.get("total")
        assert isinstance(total, (int, float)), (
            f"Expected numeric `total` field in response, got: {parsed!r}"
        )
        assert math.isclose(float(total), 7.5, rel_tol=1e-6, abs_tol=1e-6), (
            f"Expected `total` to equal 7.5 (3 * 2.5), got: {total!r}"
        )
    else:
        # No JSON could be parsed; fall back to substring assertions on the raw output.
        assert "widget" in combined, (
            f"Expected the valid-input response to mention `widget`. Output:\n{combined}"
        )
        assert re.search(r"\b7(?:\.50*)?\b", combined), (
            f"Expected the valid-input response to mention a total of 7.5. Output:\n{combined}"
        )


def test_invalid_input_is_rejected_by_pydantic():
    """A payload missing required Pydantic fields must surface as a script-level failure."""
    payload = json.dumps({"data": {"item": "widget"}})
    result = _wmill_run(payload)

    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    lowered = combined.lower()

    # The successful processed value must not appear when the script rejects the payload.
    assert not re.search(r'"total"\s*:\s*7(?:\.50*)?\b', combined), (
        "Invalid payload unexpectedly produced the same numeric total as the valid run; "
        "Pydantic validation does not appear to be rejecting the input.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    failure_markers = (
        "error",
        "validation",
        "field required",
        "missing",
        "traceback",
        "pydantic",
        "invalid",
    )

    nonzero = result.returncode != 0
    has_marker = any(marker in lowered for marker in failure_markers)

    assert nonzero or has_marker, (
        "Expected `wmill script run` with an invalid payload to either exit with a non-zero "
        "status or to surface a script-level failure marker (e.g. 'error', 'validation', "
        f"'field required', 'missing', 'traceback'). Got exit code {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
