import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
ETL_TS = os.path.join(SCRIPTS_DIR, "etl_pipeline.ts")
ETL_YAML = os.path.join(SCRIPTS_DIR, "etl_pipeline.script.yaml")

RAW_RECORDS = [
    {"name": "A", "value": "10", "category": "x"},
    {"name": "B", "value": "bad", "category": "x"},
    {"name": "C", "value": "20", "category": "y"},
]


def test_etl_ts_exists():
    assert os.path.isfile(ETL_TS)


def test_etl_yaml_exists():
    assert os.path.isfile(ETL_YAML)


def _eval_etl(records: list, filter_cat: str = "", multiplier: float = 1) -> dict:
    with open(ETL_TS) as fh:
        src = fh.read()
    js = re.sub(r"Array<[^>]+>", "", src)
    js = re.sub(r"Record<[^>]+>", "", js)
    js = re.sub(r":\s*(number|string|boolean)", "", js)
    js = js.replace("export async function", "async function")
    call = (
        f"main({json.dumps(records)}, {repr(filter_cat)}, {multiplier})"
        f".then(r => console.log(JSON.stringify(r)));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_parse_filter_transform_aggregate():
    """Priority 1: full pipeline — parse error, filter by category, multiply."""
    r = _eval_etl(RAW_RECORDS, filter_cat="x", multiplier=2)
    assert r.get("input_count") == 3, f"Expected input_count=3, got {r.get('input_count')}"
    assert r.get("parse_errors") == 1, f"Expected parse_errors=1 (for 'bad'), got {r.get('parse_errors')}"
    assert r.get("filter_category") == "x"
    # After parse: A=10, C=20; after filter by 'x': A=10; after multiply by 2: A=20
    assert r.get("output_count") == 1, f"Expected output_count=1, got {r.get('output_count')}"
    records = r.get("records", [])
    assert len(records) == 1 and records[0].get("name") == "A"
    assert records[0].get("value") == 20.0, f"Expected value=20 (10*2), got {records[0].get('value')}"
    agg = r.get("aggregate", {})
    assert agg.get("total") == 20.0


def test_no_filter_all_valid():
    """Priority 1: no filter, all valid records included."""
    records = [{"name": "X", "value": "5", "category": "a"}, {"name": "Y", "value": "15", "category": "b"}]
    r = _eval_etl(records, filter_cat="", multiplier=1)
    assert r.get("output_count") == 2
    assert r.get("parse_errors") == 0


def test_empty_input():
    """Priority 1: empty input → all zeros."""
    r = _eval_etl([])
    assert r.get("input_count") == 0
    assert r.get("output_count") == 0
    assert r.get("aggregate", {}).get("average") == 0


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
    assert _parse_simple_yaml(ETL_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(ETL_YAML).get("summary") == "Multi-stage ETL pipeline: parse, filter, transform, aggregate"
