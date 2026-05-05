import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
CONFIG_TS = os.path.join(SCRIPTS_DIR, "build_config.ts")
CONFIG_YAML = os.path.join(SCRIPTS_DIR, "build_config.script.yaml")


def test_config_ts_exists():
    assert os.path.isfile(CONFIG_TS)


def test_config_yaml_exists():
    assert os.path.isfile(CONFIG_YAML)


def _eval_config(env: str, url: str, debug: bool = False, max_retries: int = 3, timeout: int = 5000) -> dict:
    with open(CONFIG_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    js = js.replace("export async function", "async function")
    call = (
        f"main({repr(env)}, {repr(url)}, {'true' if debug else 'false'}, {max_retries}, {timeout})"
        f".then(r => console.log(JSON.stringify(r)));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def _eval_expect_error(env: str, url: str) -> str:
    with open(CONFIG_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    js = js.replace("export async function", "async function")
    call = (
        f"main({repr(env)}, {repr(url)})"
        f".then(() => process.stdout.write('NO_ERROR'))"
        f".catch(e => process.stdout.write(e.message));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    return result.stdout.strip()


def test_production_config():
    """Priority 1: production env → is_production=true, debug forced false, trailing slash stripped, log_level=warn."""
    r = _eval_config("production", "https://api.example.com/", True, 5, 10000)
    assert r.get("is_production") is True
    assert r.get("debug") is False, "debug must be False in production even if caller passes True"
    assert r.get("api_base_url") == "https://api.example.com", (
        f"Expected no trailing slash, got {repr(r.get('api_base_url'))}"
    )
    assert r.get("log_level") == "warn", f"Expected log_level='warn', got {repr(r.get('log_level'))}"


def test_development_config():
    """Priority 1: development env → debug=true allowed, log_level=debug."""
    r = _eval_config("development", "http://localhost:3000", True)
    assert r.get("debug") is True
    assert r.get("log_level") == "debug"
    assert r.get("is_production") is False


def test_invalid_environment_throws():
    """Priority 1: unknown environment → throws error."""
    msg = _eval_expect_error("invalid", "http://x.com")
    assert msg != "NO_ERROR", "Expected error for invalid environment."
    assert "Unknown environment" in msg or "invalid" in msg.lower(), (
        f"Expected error about unknown environment, got: {repr(msg)}"
    )


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
    assert _parse_simple_yaml(CONFIG_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(CONFIG_YAML).get("summary") == "Build an environment-specific configuration object"
