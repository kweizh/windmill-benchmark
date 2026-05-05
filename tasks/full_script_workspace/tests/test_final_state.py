import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"
FETCH_TS = os.path.join(SCRIPTS_DIR, "fetch_users.ts")
ENRICH_TS = os.path.join(SCRIPTS_DIR, "enrich_users.ts")
EXPORT_TS = os.path.join(SCRIPTS_DIR, "export_csv.ts")
FLOW_YAML = os.path.join(FLOWS_DIR, "user_export_pipeline.yaml")


def _strip_ts(src: str) -> str:
    js = re.sub(r"Promise<[^>]+>", "", src)
    js = re.sub(r"Array<[^>]+>", "", js)
    js = re.sub(r"Record<[^>]+>", "", js)
    js = re.sub(r":\s*(number|string|boolean)", "", js)
    return js.replace("export async function", "async function")


def _eval_ts(path: str, call: str) -> object:
    with open(path) as fh:
        src = fh.read()
    js = _strip_ts(src)
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed for {path}: {result.stderr}"
    return json.loads(result.stdout.strip())


# Existence checks
def test_fetch_users_ts_exists():
    assert os.path.isfile(FETCH_TS)


def test_enrich_users_ts_exists():
    assert os.path.isfile(ENRICH_TS)


def test_export_csv_ts_exists():
    assert os.path.isfile(EXPORT_TS)


def test_flow_yaml_exists():
    assert os.path.isfile(FLOW_YAML)


for script_name in ["fetch_users", "enrich_users", "export_csv"]:
    def _meta_test(name):
        def test_fn():
            assert os.path.isfile(os.path.join(SCRIPTS_DIR, f"{name}.script.yaml")), \
                f"{name}.script.yaml not found."
        test_fn.__name__ = f"test_{name}_metadata_exists"
        return test_fn
    globals()[f"test_{script_name}_metadata_exists"] = _meta_test(script_name)


# Runtime checks
def test_fetch_users_generates_correct_count():
    """Priority 1: fetch_users(3) returns exactly 3 users with ids 1,2,3."""
    users = _eval_ts(FETCH_TS, "main(3).then(r => console.log(JSON.stringify(r)));")
    assert len(users) == 3, f"Expected 3 users, got {len(users)}"
    assert users[0].get("id") == 1
    assert users[2].get("id") == 3
    assert "@example.com" in users[0].get("email", "")


def test_enrich_users_adds_display_field():
    """Priority 1: enrich_users adds display field to each user."""
    sample = [{"id": 1, "name": "Alice", "email": "alice@example.com"}]
    enriched = _eval_ts(ENRICH_TS,
        f"main({json.dumps(sample)}, '').then(r => console.log(JSON.stringify(r)));")
    assert len(enriched) == 1
    assert "display" in enriched[0], "enrich_users must add 'display' field."
    assert "Alice" in enriched[0]["display"]


def test_enrich_users_domain_filter():
    """Priority 1: domain_filter removes non-matching users."""
    sample = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@other.com"},
    ]
    enriched = _eval_ts(ENRICH_TS,
        f"main({json.dumps(sample)}, '@example.com').then(r => console.log(JSON.stringify(r)));")
    assert len(enriched) == 1
    assert enriched[0]["id"] == 1


def test_export_csv_basic():
    """Priority 1: export_csv produces correct CSV with header and rows."""
    records = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
    r = _eval_ts(EXPORT_TS,
        f"main({json.dumps(records)}).then(r => console.log(JSON.stringify(r)));")
    assert r.get("row_count") == 2, f"Expected row_count=2, got {r.get('row_count')}"
    csv = r.get("csv", "")
    lines = csv.split("\n")
    assert lines[0] in ("a,b", "b,a"), f"Expected CSV header 'a,b', got {repr(lines[0])}"


def test_export_csv_empty():
    """Priority 1: empty records → csv='' and row_count=0."""
    r = _eval_ts(EXPORT_TS, "main([]).then(r => console.log(JSON.stringify(r)));")
    assert r.get("row_count") == 0
    assert r.get("csv") == ""


def test_flow_yaml_has_three_steps():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "fetch" in content, "Flow must have step 'fetch'."
    assert "enrich" in content, "Flow must have step 'enrich'."
    assert "export" in content, "Flow must have step 'export'."


def test_flow_yaml_wires_results():
    with open(FLOW_YAML) as fh:
        content = fh.read()
    assert "results.fetch" in content, "Flow must wire results.fetch to enrich step."
    assert "results.enrich" in content, "Flow must wire results.enrich to export step."
