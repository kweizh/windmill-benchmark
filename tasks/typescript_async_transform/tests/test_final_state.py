import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
ENRICH_TS = os.path.join(SCRIPTS_DIR, "enrich_products.ts")
ENRICH_YAML = os.path.join(SCRIPTS_DIR, "enrich_products.script.yaml")


def test_enrich_ts_exists():
    assert os.path.isfile(ENRICH_TS)


def test_enrich_yaml_exists():
    assert os.path.isfile(ENRICH_YAML)


def _eval_enrich(products: list, tax_rate: float = 0.1) -> dict:
    with open(ENRICH_TS) as fh:
        src = fh.read()
    js = re.sub(r"Array<[^>]+>", "", src)
    js = re.sub(r":\s*(number|string|boolean)", "", js)
    js = js.replace("export async function", "async function")
    call = (
        f"main({json.dumps(products)}, {tax_rate})"
        f".then(r => console.log(JSON.stringify(r)));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_single_product():
    """Priority 1: single product with 10% tax."""
    r = _eval_enrich([{"id": 1, "name": "Widget", "price": 10}], 0.1)
    assert r.get("count") == 1
    assert r.get("tax_rate") == 0.1
    products = r.get("products", [])
    assert len(products) == 1
    p = products[0]
    assert p.get("tax") == 1.0, f"Expected tax=1.0, got {p.get('tax')}"
    assert p.get("total") == 11.0, f"Expected total=11.0, got {p.get('total')}"
    assert p.get("label") == "Widget ($10)", f"Expected label='Widget ($10)', got {repr(p.get('label'))}"


def test_two_products():
    """Priority 1: two products, 20% tax."""
    r = _eval_enrich([{"id": 1, "name": "A", "price": 100}, {"id": 2, "name": "B", "price": 200}], 0.2)
    assert r.get("count") == 2
    ps = r.get("products", [])
    assert ps[0].get("total") == 120.0, f"Expected 120.0, got {ps[0].get('total')}"
    assert ps[1].get("total") == 240.0, f"Expected 240.0, got {ps[1].get('total')}"


def test_empty_products():
    """Priority 1: empty input."""
    r = _eval_enrich([])
    assert r.get("count") == 0
    assert r.get("products") == []


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
    assert _parse_simple_yaml(ENRICH_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(ENRICH_YAML).get("summary") == "Enrich a list of products with tax and total price"
