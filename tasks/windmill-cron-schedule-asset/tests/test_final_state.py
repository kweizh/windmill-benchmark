import os
import re

import requests

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
BASE_URL = "https://app.windmill.dev"

EXPECTED_CRON = "0 * * * * *"
EXPECTED_TIMEZONE = "Asia/Shanghai"


def _env(name: str) -> str:
    value = os.environ.get(name, "")
    assert value, f"Required environment variable {name} is not set."
    return value


def _read_log() -> str:
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()


def _extract_path(label: str, log_text: str, run_id: str) -> str:
    pattern = rf"^{re.escape(label)}:\s*(f/eval_{re.escape(run_id)}/[A-Za-z0-9_./-]+)\s*$"
    matches = re.findall(pattern, log_text, flags=re.MULTILINE)
    assert matches, (
        f"Could not find a line matching '{label}: f/eval_{run_id}/...' in "
        f"{LOG_FILE}. Log contents:\n{log_text}"
    )
    return matches[-1].strip()


def test_log_file_contains_script_path():
    run_id = _env("ZEALT_RUN_ID")
    log_text = _read_log()
    script_path = _extract_path("Script path", log_text, run_id)
    assert script_path.startswith(f"f/eval_{run_id}/"), (
        f"Script path '{script_path}' does not start with the expected "
        f"run-id-scoped prefix 'f/eval_{run_id}/'."
    )


def test_log_file_contains_schedule_path():
    run_id = _env("ZEALT_RUN_ID")
    log_text = _read_log()
    schedule_path = _extract_path("Schedule path", log_text, run_id)
    assert schedule_path.startswith(f"f/eval_{run_id}/"), (
        f"Schedule path '{schedule_path}' does not start with the expected "
        f"run-id-scoped prefix 'f/eval_{run_id}/'."
    )


def test_script_deployed_to_windmill():
    run_id = _env("ZEALT_RUN_ID")
    token = _env("WINDMILL_TOKEN")
    workspace = _env("WINDMILL_WORKSPACE")
    log_text = _read_log()
    script_path = _extract_path("Script path", log_text, run_id)

    url = f"{BASE_URL}/api/w/{workspace}/scripts/get/p/{script_path}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"GET {url} returned HTTP {resp.status_code}. Body: {resp.text}"
    )
    data = resp.json()
    assert data.get("path") == script_path, (
        f"Windmill API reported script path '{data.get('path')}', expected "
        f"'{script_path}'."
    )
    assert data.get("language") == "python3", (
        f"Windmill API reported script language '{data.get('language')}', "
        f"expected 'python3'."
    )


def test_schedule_deployed_with_expected_fields():
    run_id = _env("ZEALT_RUN_ID")
    token = _env("WINDMILL_TOKEN")
    workspace = _env("WINDMILL_WORKSPACE")
    log_text = _read_log()
    script_path = _extract_path("Script path", log_text, run_id)
    schedule_path = _extract_path("Schedule path", log_text, run_id)

    url = f"{BASE_URL}/api/w/{workspace}/schedules/get/{schedule_path}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    assert resp.status_code == 200, (
        f"GET {url} returned HTTP {resp.status_code}. Body: {resp.text}"
    )
    data = resp.json()

    assert data.get("schedule") == EXPECTED_CRON, (
        f"Schedule cron expression is '{data.get('schedule')}', expected "
        f"'{EXPECTED_CRON}' (croner 6-field form for every minute at second 0)."
    )
    assert data.get("timezone") == EXPECTED_TIMEZONE, (
        f"Schedule timezone is '{data.get('timezone')}', expected "
        f"'{EXPECTED_TIMEZONE}'."
    )
    assert data.get("script_path") == script_path, (
        f"Schedule script_path is '{data.get('script_path')}', expected "
        f"'{script_path}'."
    )
    assert data.get("enabled") is True, (
        f"Schedule enabled is {data.get('enabled')!r}, expected boolean True."
    )
    assert data.get("is_flow") is False, (
        f"Schedule is_flow is {data.get('is_flow')!r}, expected boolean False "
        f"(the schedule must target a script, not a flow)."
    )
