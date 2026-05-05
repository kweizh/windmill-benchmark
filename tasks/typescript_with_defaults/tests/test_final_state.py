import os
import re
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FORMAT_PRICE_TS = os.path.join(SCRIPTS_DIR, "format_price.ts")
FORMAT_PRICE_YAML = os.path.join(SCRIPTS_DIR, "format_price.script.yaml")


def test_format_price_ts_exists():
    assert os.path.isfile(FORMAT_PRICE_TS), f"Expected '{FORMAT_PRICE_TS}' but not found."


def test_format_price_yaml_exists():
    assert os.path.isfile(FORMAT_PRICE_YAML), f"Expected '{FORMAT_PRICE_YAML}' but not found."


def _eval_format_price(*args) -> str:
    with open(FORMAT_PRICE_TS) as fh:
        src = fh.read()
    js = re.sub(r":\s*(number|string|boolean)", "", src)
    js = js.replace("export async function", "async function")
    arg_str = ", ".join(repr(a) if isinstance(a, str) else str(a) for a in args)
    call = f"main({arg_str}).then(r => process.stdout.write(r));"
    result = subprocess.run(["node", "-e", js + "\n" + call], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"node failed: {result.stderr}"
    return result.stdout


def test_default_all():
    """Priority 1: main(9.5) → '9.50 USD'"""
    assert _eval_format_price(9.5) == "9.50 USD", f"Got: {repr(_eval_format_price(9.5))}"


def test_custom_currency_zero_decimals_prefix():
    """Priority 1: main(1234.5, 'EUR', 0, '~') → '~1235 EUR'"""
    assert _eval_format_price(1234.5, "EUR", 0, "~") == "~1235 EUR"


def test_custom_prefix():
    """Priority 1: main(100, 'GBP', 2, '$') → '$100.00 GBP'"""
    assert _eval_format_price(100, "GBP", 2, "$") == "$100.00 GBP"


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
    assert _parse_simple_yaml(FORMAT_PRICE_YAML).get("language") == "typescript"


def test_yaml_summary():
    assert _parse_simple_yaml(FORMAT_PRICE_YAML).get("summary") == "Format a monetary amount as a price string"
