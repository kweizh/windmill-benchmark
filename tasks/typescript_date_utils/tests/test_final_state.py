import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
DATE_UTILS_TS = os.path.join(SCRIPTS_DIR, "date_utils.ts")
DATE_UTILS_YAML = os.path.join(SCRIPTS_DIR, "date_utils.script.yaml")


def test_date_utils_ts_exists():
    assert os.path.isfile(DATE_UTILS_TS), f"Expected '{DATE_UTILS_TS}' but not found."


def test_date_utils_yaml_exists():
    assert os.path.isfile(DATE_UTILS_YAML), f"Expected '{DATE_UTILS_YAML}' but not found."


def _eval_date_utils(iso_date: str, label: str = "") -> dict:
    with open(DATE_UTILS_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    js = js.replace("export async function", "async function")
    if label:
        call = f"main({repr(iso_date)}, {repr(label)}).then(r => console.log(JSON.stringify(r)));"
    else:
        call = f"main({repr(iso_date)}).then(r => console.log(JSON.stringify(r)));"
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_formatted_date_december_31():
    """Priority 1: formatted field uses full English month name."""
    r = _eval_date_utils("2025-12-31")
    assert r.get("iso") == "2025-12-31", f"Expected iso='2025-12-31', got {repr(r.get('iso'))}"
    assert r.get("label") == "Event", f"Expected default label='Event', got {repr(r.get('label'))}"
    assert "December" in r.get("formatted", ""), (
        f"Expected 'December' in formatted, got {repr(r.get('formatted'))}"
    )
    assert "31" in r.get("formatted", ""), "Expected day '31' in formatted."
    assert "2025" in r.get("formatted", ""), "Expected year '2025' in formatted."
    assert isinstance(r.get("days_from_today"), (int, float)), "days_from_today must be a number."


def test_past_date_has_negative_days():
    """Priority 1: Y2K is in the past — days_from_today must be negative."""
    r = _eval_date_utils("2000-01-01", "Y2K")
    assert r.get("label") == "Y2K"
    assert r.get("days_from_today", 0) < 0, (
        f"Expected negative days_from_today for past date, got {r.get('days_from_today')}"
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
    assert _parse_simple_yaml(DATE_UTILS_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(DATE_UTILS_YAML).get("summary") == "Format a date and compute days from today"
