import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"
RISKY_TS = os.path.join(SCRIPTS_DIR, "risky_operation.ts")
HANDLE_TS = os.path.join(SCRIPTS_DIR, "handle_error.ts")
FLOW_YAML = os.path.join(FLOWS_DIR, "resilient_pipeline.yaml")


def _strip_ts(src: str) -> str:
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    return js.replace("export async function", "async function")


def _eval_ts(path: str, call: str) -> str:
    with open(path) as fh:
        src = fh.read()
    js = _strip_ts(src)
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed for {path}: {result.stderr}"
    return result.stdout.strip()


def test_risky_ts_exists():
    assert os.path.isfile(RISKY_TS)


def test_handle_error_ts_exists():
    assert os.path.isfile(HANDLE_TS)


def test_flow_yaml_exists():
    assert os.path.isfile(FLOW_YAML)


def test_risky_operation_success():
    """Priority 1: main(false) → status='ok'"""
    out = json.loads(_eval_ts(RISKY_TS, "main(false).then(r => console.log(JSON.stringify(r)));"))
    assert out.get("status") == "ok", f"Expected status='ok', got {out.get('status')}"


def test_risky_operation_throws():
    """Priority 1: main(true) → throws 'Intentional failure'"""
    with open(RISKY_TS) as fh:
        src = fh.read()
    js = _strip_ts(src)
    call = (
        "main(true)"
        ".then(() => process.stdout.write('NO_ERROR'))"
        ".catch(e => process.stdout.write(e.message));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert "Intentional failure" in result.stdout, (
        f"Expected 'Intentional failure' in error, got: {repr(result.stdout)}"
    )


def test_handle_error_runtime():
    """Priority 1: handle_error returns alert=true with context in message."""
    out = json.loads(_eval_ts(
        HANDLE_TS,
        "main('Test error', 'my/flow', 'step-a').then(r => console.log(JSON.stringify(r)));"
    ))
    assert out.get("alert") is True, f"Expected alert=true, got {out.get('alert')}"
    msg = out.get("message", "")
    assert "my/flow" in msg, f"message must reference flow path 'my/flow', got: {repr(msg)}"
    assert "step-a" in msg, f"message must reference step id 'step-a', got: {repr(msg)}"
    assert "Test error" in msg, f"message must include error text, got: {repr(msg)}"


def test_flow_has_error_handler():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "error_handler" in content, "Flow YAML must define an error_handler."
    assert "handle_error" in content, "error_handler must reference the handle_error script."


def test_flow_references_risky_operation():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "risky_operation" in content, "Flow must reference the risky_operation script."
