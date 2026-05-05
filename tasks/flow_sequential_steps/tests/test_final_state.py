import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"
GEN_MSG_TS = os.path.join(SCRIPTS_DIR, "generate_message.ts")
WRAP_MSG_TS = os.path.join(SCRIPTS_DIR, "wrap_message.ts")
FLOW_YAML = os.path.join(FLOWS_DIR, "greet_and_wrap.yaml")


def test_generate_message_ts_exists():
    assert os.path.isfile(GEN_MSG_TS), f"Expected '{GEN_MSG_TS}' but not found."


def test_wrap_message_ts_exists():
    assert os.path.isfile(WRAP_MSG_TS), f"Expected '{WRAP_MSG_TS}' but not found."


def test_flow_yaml_exists():
    assert os.path.isfile(FLOW_YAML), f"Expected '{FLOW_YAML}' but not found."


def _strip_ts(src: str) -> str:
    js = re.sub(r"Promise<[^>]+>", "", src)
    js = re.sub(r":\s*(number|string|boolean|void)", "", js)
    return js.replace("export async function", "async function")


def test_generate_message_runtime():
    """Priority 1: generate_message.ts main('Windmill') returns message and timestamp."""
    with open(GEN_MSG_TS) as fh:
        src = fh.read()
    js = _strip_ts(src)
    call = "main('Windmill').then(r => console.log(JSON.stringify(r)));"
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    obj = json.loads(result.stdout.strip())
    assert obj.get("message") == "Hello, Windmill!", (
        f"Expected message='Hello, Windmill!', got {repr(obj.get('message'))}"
    )
    assert "timestamp" in obj, "Expected 'timestamp' key in result."


def test_wrap_message_runtime():
    """Priority 1: wrap_message.ts main('Hello, World!') returns '>>> Hello, World!'"""
    with open(WRAP_MSG_TS) as fh:
        src = fh.read()
    js = _strip_ts(src)
    call = "main('Hello, World!').then(r => process.stdout.write(r));"
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    assert result.stdout == ">>> Hello, World!", f"Got: {repr(result.stdout)}"


def _read_flow_yaml_text() -> str:
    with open(FLOW_YAML) as fh:
        return fh.read()


def test_flow_yaml_has_summary():
    content = _read_flow_yaml_text()
    assert "Greet and wrap a message" in content, (
        f"Flow YAML missing summary 'Greet and wrap a message'"
    )


def test_flow_yaml_has_module_ids_a_and_b():
    content = _read_flow_yaml_text()
    assert "id: a" in content, "Flow YAML missing module id 'a'."
    assert "id: b" in content, "Flow YAML missing module id 'b'."


def test_flow_yaml_input_transform_uses_javascript_expression():
    content = _read_flow_yaml_text()
    assert "results.a.message" in content, (
        "Flow YAML step 'b' must reference 'results.a.message' via a javascript expression."
    )
    assert "type: javascript" in content, (
        "Flow YAML step 'b' must use 'type: javascript' for the message input transform."
    )


def test_flow_yaml_step_a_has_static_name():
    content = _read_flow_yaml_text()
    assert "type: static" in content, (
        "Flow YAML step 'a' must use 'type: static' for the name input transform."
    )
    assert "Windmill" in content, "Flow YAML step 'a' must supply static value 'Windmill' for name."


def test_generate_message_metadata_exists():
    assert os.path.isfile(os.path.join(SCRIPTS_DIR, "generate_message.script.yaml"))


def test_wrap_message_metadata_exists():
    assert os.path.isfile(os.path.join(SCRIPTS_DIR, "wrap_message.script.yaml"))
