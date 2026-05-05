import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
SEND_EMAIL_TS = os.path.join(SCRIPTS_DIR, "send_email.ts")
SEND_EMAIL_YAML = os.path.join(SCRIPTS_DIR, "send_email.script.yaml")


def test_send_email_ts_exists():
    assert os.path.isfile(SEND_EMAIL_TS)


def test_send_email_yaml_exists():
    assert os.path.isfile(SEND_EMAIL_YAML)


def _eval_send_email(recipient: dict, subject: str, body: str, dry_run: bool = True) -> dict:
    with open(SEND_EMAIL_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*\{[^}]+\}", "", src)
    js = re.sub(r":\s*(number|string|boolean)", "", js)
    js = js.replace("export async function", "async function")
    call = (
        f"main({json.dumps(recipient)}, {json.dumps(subject)}, {json.dumps(body)}, {'true' if dry_run else 'false'})"
        f".then(r => console.log(JSON.stringify(r)));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_dry_run_default():
    """Priority 1: dry_run=true by default → sent=false."""
    r = _eval_send_email({"email": "alice@example.com", "name": "Alice"}, "Hello", "Hi there")
    assert r.get("to") == "Alice <alice@example.com>", f"Got to={repr(r.get('to'))}"
    assert r.get("sent") is False, f"Expected sent=false, got {r.get('sent')}"
    assert r.get("subject") == "Hello"
    assert r.get("body") == "Hi there"
    assert "Alice" in r.get("preview", ""), "Preview should contain recipient name."


def test_sent_true_when_not_dry_run():
    """Priority 1: dry_run=false → sent=true."""
    r = _eval_send_email({"email": "bob@example.com", "name": "Bob"}, "Test", "Body", False)
    assert r.get("sent") is True, f"Expected sent=true when dry_run=false, got {r.get('sent')}"


def _parse_simple_yaml(path: str) -> dict:
    result = {}
    with open(path) as fh:
        for line in fh:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip()] = v.strip().strip('"').strip("'")
    return result


def test_yaml_language():
    assert _parse_simple_yaml(SEND_EMAIL_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(SEND_EMAIL_YAML).get("summary") == "Compose and optionally send an email"
