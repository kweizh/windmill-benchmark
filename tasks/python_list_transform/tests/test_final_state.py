import os
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
ORDERS_PY = os.path.join(SCRIPTS_DIR, "process_orders.py")
ORDERS_YAML = os.path.join(SCRIPTS_DIR, "process_orders.script.yaml")

SAMPLE_ORDERS = [
    {"id": 1, "product": "Widget A", "amount": 10.0, "shipped": True},
    {"id": 2, "product": "Widget B", "amount": 50.0, "shipped": False},
    {"id": 3, "product": "Widget C", "amount": 5.0, "shipped": True},
]


def test_orders_py_exists():
    assert os.path.isfile(ORDERS_PY), f"Expected '{ORDERS_PY}' but not found."


def test_orders_yaml_exists():
    assert os.path.isfile(ORDERS_YAML), f"Expected '{ORDERS_YAML}' but not found."


def _run_main(orders: list, min_amount: float = 0.0) -> dict:
    script = (
        f"import importlib.util, json\n"
        f"spec = importlib.util.spec_from_file_location('po', '{ORDERS_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(json.dumps(mod.main({json.dumps(orders)}, {min_amount})))\n"
    )
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"python3 failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_filter_by_min_amount():
    """Priority 1: min_amount=10 filters out Widget C (amount=5)."""
    r = _run_main(SAMPLE_ORDERS, min_amount=10.0)
    assert r.get("total_orders") == 2, f"Expected 2, got {r.get('total_orders')}"
    assert r.get("total_amount") == 60.0, f"Expected total=60.0, got {r.get('total_amount')}"
    assert r.get("shipped_count") == 1, f"Expected shipped_count=1 (Widget A only), got {r.get('shipped_count')}"
    item_ids = [i["id"] for i in r.get("items", [])]
    assert sorted(item_ids) == [1, 2], f"Expected item ids [1,2], got {item_ids}"


def test_no_filter():
    """Priority 1: min_amount=0 returns all 3 orders."""
    r = _run_main(SAMPLE_ORDERS, min_amount=0.0)
    assert r.get("total_orders") == 3


def test_empty_list():
    """Priority 1: empty input returns zero counts."""
    r = _run_main([])
    assert r.get("total_orders") == 0
    assert r.get("items") == []


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
    assert _parse_simple_yaml(ORDERS_YAML).get("language") == "python3"


def test_yaml_summary():
    assert _parse_simple_yaml(ORDERS_YAML).get("summary") == "Filter and summarize a list of orders"
