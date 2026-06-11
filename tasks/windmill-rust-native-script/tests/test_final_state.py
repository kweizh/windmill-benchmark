import json
import os
import re
import subprocess

import pytest

PROJECT_DIR = "/home/user/myproject"
RS_PATH = os.path.join(PROJECT_DIR, "f", "eval", "rust_doubler.rs")
YAML_PATH = os.path.join(PROJECT_DIR, "f", "eval", "rust_doubler.script.yaml")
WMILL_RUN_TIMEOUT_SECONDS = 180


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_trailing_json(stdout: str):
    """Extract the last JSON object/array from the stdout of `wmill script run`.

    The CLI streams log lines before printing the final result, even with
    `-s/--silent`.  We try strict whole-output parsing first, then fall back to
    scanning for the last balanced JSON object.
    """

    stdout = stdout.strip()
    if not stdout:
        raise AssertionError("`wmill script run` produced no stdout.")

    # Try the trivial case: the entire stdout is valid JSON.
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        pass

    # Scan from the end backwards for the last balanced top-level JSON object.
    decoder = json.JSONDecoder()
    best = None
    for i in range(len(stdout)):
        if stdout[i] not in "{[":
            continue
        try:
            obj, _end = decoder.raw_decode(stdout[i:])
        except json.JSONDecodeError:
            continue
        best = obj  # keep the latest successful decode in textual order
    if best is None:
        raise AssertionError(
            f"Could not find a JSON object in `wmill script run` stdout:\n{stdout}"
        )
    return best


def _run_wmill_script(payload: dict):
    cmd = [
        "wmill",
        "script",
        "run",
        "f/eval/rust_doubler",
        "-d",
        json.dumps(payload),
        "-s",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=WMILL_RUN_TIMEOUT_SECONDS,
    )
    return result


def test_rust_source_file_exists():
    assert os.path.isfile(RS_PATH), f"Expected Rust source file at {RS_PATH}, but it does not exist."


def test_script_yaml_exists_and_declares_rust_language():
    assert os.path.isfile(YAML_PATH), f"Expected YAML companion at {YAML_PATH}, but it does not exist."
    content = _read_text(YAML_PATH)
    assert re.search(r"^\s*language:\s*['\"]?rust['\"]?\s*$", content, re.IGNORECASE | re.MULTILINE), (
        f"{YAML_PATH} must declare `language: rust`. Current contents:\n{content}"
    )


def test_main_signature_has_required_parameters():
    content = _read_text(RS_PATH)
    # Be permissive about whitespace/return type so we accept either `-> serde_json::Value`
    # or `-> anyhow::Result<...>` styles.
    assert re.search(r"fn\s+main\s*\(", content), (
        f"{RS_PATH} must define a `main` function."
    )
    assert re.search(r"name\s*:\s*String", content), (
        f"`main` in {RS_PATH} must accept a parameter `name: String`."
    )
    assert re.search(r"threshold\s*:\s*i32", content), (
        f"`main` in {RS_PATH} must accept a parameter `threshold: i32`."
    )


def test_inline_cargo_dependency_block_declares_serde_json():
    content = _read_text(RS_PATH)
    # Look for Windmill's documented partial-Cargo annotation block.
    match = re.search(r"//!\s*```cargo(.*?)//!\s*```", content, re.DOTALL)
    assert match, (
        f"{RS_PATH} must contain a `//!` doc-comment block with a ```cargo fenced section "
        "declaring inline Cargo dependencies."
    )
    block = match.group(1)
    assert "serde_json" in block, (
        f"The inline Cargo annotation block must declare `serde_json` as a dependency. Block:\n{block}"
    )


def test_script_listed_in_cloud_workspace():
    """Verify the script was deployed to the cloud workspace (not just authored locally)."""
    result = subprocess.run(
        ["wmill", "script", "list"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"`wmill script list` failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "f/eval/rust_doubler" in result.stdout, (
        f"Path `f/eval/rust_doubler` not present in `wmill script list` output, "
        f"meaning the script was not deployed.\nOutput:\n{result.stdout}"
    )


def test_cloud_execution_positive_threshold():
    result = _run_wmill_script({"name": "alpha", "threshold": 21})
    assert result.returncode == 0, (
        f"`wmill script run` exited with {result.returncode} for positive case.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    payload = _extract_trailing_json(result.stdout)
    assert isinstance(payload, dict), f"Expected a JSON object, got: {payload!r}"
    assert payload.get("status") == "ok", f"Expected status=='ok', got: {payload!r}"
    assert payload.get("computed") == 42, f"Expected computed==42 for threshold=21, got: {payload!r}"
    assert payload.get("target") == "alpha", f"Expected target=='alpha', got: {payload!r}"


def test_cloud_execution_negative_threshold():
    result = _run_wmill_script({"name": "beta", "threshold": -5})
    assert result.returncode == 0, (
        f"`wmill script run` exited with {result.returncode} for negative case.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    payload = _extract_trailing_json(result.stdout)
    assert isinstance(payload, dict), f"Expected a JSON object, got: {payload!r}"
    assert payload.get("status") == "ok", f"Expected status=='ok', got: {payload!r}"
    assert payload.get("computed") == -10, f"Expected computed==-10 for threshold=-5, got: {payload!r}"
    assert payload.get("target") == "beta", f"Expected target=='beta', got: {payload!r}"
