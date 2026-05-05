import os
import re
import json
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
INVOICE_TS = os.path.join(SCRIPTS_DIR, "invoice.ts")
INVOICE_YAML = os.path.join(SCRIPTS_DIR, "invoice.script.yaml")


def test_invoice_ts_exists():
    assert os.path.isfile(INVOICE_TS)


def test_invoice_yaml_exists():
    assert os.path.isfile(INVOICE_YAML)


def _eval_invoice(items: list, tax_rate: float = 0.1, currency: str = "USD") -> dict:
    with open(INVOICE_TS) as fh:
        src = fh.read()
    js = re.sub(r"Array<[^>]+>", "", src)
    js = re.sub(r":\s*(number|string|boolean)", "", js)
    js = js.replace("export async function", "async function")
    call = (
        f"main({json.dumps(items)}, {tax_rate}, {repr(currency)})"
        f".then(r => console.log(JSON.stringify(r)));"
    )
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_single_line_item():
    """Priority 1: qty=2, unit_price=5, tax=10% → subtotal=$10, tax=$1, total=$11."""
    r = _eval_invoice([{"name": "Widget", "qty": 2, "unit_price": 5}], 0.1, "USD")
    assert r.get("subtotal") == "USD 10.00", f"Expected 'USD 10.00', got {repr(r.get('subtotal'))}"
    assert r.get("tax") == "USD 1.00", f"Expected 'USD 1.00', got {repr(r.get('tax'))}"
    assert r.get("total") == "USD 11.00", f"Expected 'USD 11.00', got {repr(r.get('total'))}"
    line_items = r.get("line_items", [])
    assert len(line_items) == 1
    assert line_items[0].get("amount") == "USD 10.00"
    assert line_items[0].get("name") == "Widget"


def test_two_line_items():
    """Priority 1: A:$100 + B:$60 = $160 subtotal."""
    items = [{"name": "A", "qty": 1, "unit_price": 100}, {"name": "B", "qty": 3, "unit_price": 20}]
    r = _eval_invoice(items, 0.1, "USD")
    assert r.get("subtotal") == "USD 160.00", f"Got subtotal={repr(r.get('subtotal'))}"
    assert r.get("total") == "USD 176.00", f"Got total={repr(r.get('total'))}"


def test_helper_not_exported():
    """Priority 4 structural: helper functions must not be exported (no 'export function formatCurrency')."""
    # Weak check justified: there's no runtime way to inspect what's exported without a module system.
    with open(INVOICE_TS) as fh:
        src = fh.read()
    assert "export function formatCurrency" not in src, \
        "formatCurrency must NOT be exported — it is a helper function."
    assert "export function computeSubtotal" not in src, \
        "computeSubtotal must NOT be exported — it is a helper function."


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
    assert _parse_simple_yaml(INVOICE_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(INVOICE_YAML).get("summary") == "Generate an invoice summary from line items"
