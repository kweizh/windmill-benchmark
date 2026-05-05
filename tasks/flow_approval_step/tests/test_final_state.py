import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"
PREPARE_TS = os.path.join(SCRIPTS_DIR, "prepare_deployment.ts")
EXECUTE_TS = os.path.join(SCRIPTS_DIR, "execute_deployment.ts")
FLOW_YAML = os.path.join(FLOWS_DIR, "deploy_with_approval.yaml")


def _strip_ts(src: str) -> str:
    js = re.sub(r"Promise<[^>]+>", "", src)
    js = re.sub(r":\s*(number|string|boolean)", "", js)
    return js.replace("export async function", "async function")


def _eval_ts(path: str, call: str) -> dict:
    with open(path) as fh:
        src = fh.read()
    js = _strip_ts(src)
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed for {path}: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_prepare_ts_exists():
    assert os.path.isfile(PREPARE_TS)


def test_execute_ts_exists():
    assert os.path.isfile(EXECUTE_TS)


def test_flow_yaml_exists():
    assert os.path.isfile(FLOW_YAML)


def test_prepare_deployment():
    """Priority 1: prepare_deployment returns deploy_command and requires_approval=true."""
    r = _eval_ts(PREPARE_TS,
        "main('api-server', 'v1.2.3', 'production').then(r => console.log(JSON.stringify(r)));")
    assert r.get("requires_approval") is True
    assert "kubectl" in r.get("deploy_command", ""), f"deploy_command should contain kubectl: {r}"
    assert "api-server" in r.get("deploy_command", "")
    assert "v1.2.3" in r.get("deploy_command", "")


def test_execute_deployment_approved():
    """Priority 1: approved=true → status='deployed'."""
    r = _eval_ts(EXECUTE_TS,
        "main('kubectl set image ...', true).then(r => console.log(JSON.stringify(r)));")
    assert r.get("status") == "deployed", f"Expected status='deployed', got {r.get('status')}"


def test_execute_deployment_not_approved():
    """Priority 1: approved=false → status='cancelled'."""
    r = _eval_ts(EXECUTE_TS,
        "main('kubectl set image ...', false).then(r => console.log(JSON.stringify(r)));")
    assert r.get("status") == "cancelled", f"Expected status='cancelled', got {r.get('status')}"


def test_flow_has_approval_step():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "hub/0/approval" in content, "Flow must include 'hub/0/approval' as the approval step."


def test_flow_has_correct_step_ids():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "id: prepare" in content or "prepare" in content, "Flow must have step id 'prepare'."
    assert "id: deploy" in content or "deploy" in content, "Flow must have step id 'deploy'."


def test_flow_wires_deploy_command():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "prepare.deploy_command" in content or "results.prepare" in content, (
        "Flow must wire deploy_command from prepare step result."
    )
