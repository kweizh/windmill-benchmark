import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/windmill-project"
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "f", "scripts")
GREET_TS = os.path.join(SCRIPTS_DIR, "greet.ts")
GREET_YAML = os.path.join(SCRIPTS_DIR, "greet.script.yaml")


# ---------------------------------------------------------------------------
# Priority 3 (file existence) – no CLI can check file presence meaningfully
# ---------------------------------------------------------------------------

def test_greet_ts_exists():
    # File existence is a necessary prerequisite for all runtime checks below.
    assert os.path.isfile(GREET_TS), (
        f"Expected TypeScript script at '{GREET_TS}' but it was not found."
    )


def test_greet_script_yaml_exists():
    assert os.path.isfile(GREET_YAML), (
        f"Expected metadata file at '{GREET_YAML}' but it was not found."
    )


# ---------------------------------------------------------------------------
# Priority 1 – Execute the agent's script logic with node and assert runtime
# behaviour.  We inline the TS source via -e so that ts-node / tsc is not
# required: Node evaluates a thin JS shim that imports the *transpiled* JS
# equivalent.  Because the script is pure ES2015 template literals with
# default parameters — both natively supported by Node.js v20+ — we can
# strip the TypeScript type annotations on the fly with a simple sed and then
# evaluate the result with `node -e`.
# ---------------------------------------------------------------------------

def _run_greet_via_node(name: str, greeting: str | None = None) -> str:
    """
    Strip TypeScript type annotations from greet.ts with sed, then evaluate
    the resulting JavaScript with node to call main() and return its output.

    Node.js v20+ supports async/await, default parameters, and template
    literals natively — no transpiler needed once type annotations are removed.
    """
    with open(GREET_TS) as fh:
        ts_source = fh.read()

    # Remove TypeScript-specific type annotations:
    #   `: string` parameter annotations  →  (empty)
    # This is intentionally minimal — just enough for this script's shape.
    import re
    js_source = re.sub(r":\s*string", "", ts_source)
    # Remove `export` keyword so we can call main() directly
    js_source = js_source.replace("export async function", "async function")

    if greeting is None:
        call = f'main({repr(name)}).then(r => {{ process.stdout.write(r); }})'
    else:
        call = f'main({repr(name)}, {repr(greeting)}).then(r => {{ process.stdout.write(r); }})'

    node_script = js_source + "\n" + call

    result = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, (
        f"node evaluation failed (exit {result.returncode}):\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return result.stdout


def test_main_default_greeting():
    """Priority 1: main('World') should return 'Hello, World!'"""
    output = _run_greet_via_node("World")
    assert output == "Hello, World!", (
        f"Expected 'Hello, World!' but got: {repr(output)}"
    )


def test_main_custom_greeting():
    """Priority 1: main('Alice', 'Hi') should return 'Hi, Alice!'"""
    output = _run_greet_via_node("Alice", "Hi")
    assert output == "Hi, Alice!", (
        f"Expected 'Hi, Alice!' but got: {repr(output)}"
    )


def test_main_another_name():
    """Priority 1: main('Bob', 'Hey') should return 'Hey, Bob!'"""
    output = _run_greet_via_node("Bob", "Hey")
    assert output == "Hey, Bob!", (
        f"Expected 'Hey, Bob!' but got: {repr(output)}"
    )


# ---------------------------------------------------------------------------
# Priority 1 – Structural check: verify the exported function signature by
# inspecting the parsed source for required identifiers (export, async,
# main, name, greeting).  This is a structural sanity check only; the
# runtime tests above are the authoritative correctness checks.
# ---------------------------------------------------------------------------

def test_greet_ts_exports_main_function():
    """Priority 1 structural: greet.ts must export an async main function."""
    with open(GREET_TS) as fh:
        source = fh.read()

    assert "export" in source, (
        "greet.ts does not contain the 'export' keyword — main must be exported."
    )
    assert "async function main" in source or ("async" in source and "main" in source), (
        "greet.ts does not appear to define an async main function."
    )
    assert "name" in source, (
        "greet.ts does not reference the 'name' parameter."
    )
    assert "greeting" in source, (
        "greet.ts does not reference the 'greeting' parameter."
    )


# ---------------------------------------------------------------------------
# Priority 1 – Parse greet.script.yaml with the PyYAML-equivalent stdlib
# trick (no third-party imports allowed).  We use a minimal hand-rolled YAML
# key:value parser since the file only contains simple scalar fields.
# ---------------------------------------------------------------------------

def _parse_simple_yaml(path: str) -> dict:
    """
    Parse a flat YAML file (key: value lines only) without third-party libs.
    Strips surrounding quotes from values.
    """
    result = {}
    with open(path) as fh:
        for line in fh:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                result[key] = value
    return result


def test_yaml_language_is_typescript():
    """Priority 1: greet.script.yaml must declare language: typescript"""
    data = _parse_simple_yaml(GREET_YAML)
    assert "language" in data, (
        f"'language' key missing from greet.script.yaml. Contents: {data}"
    )
    assert data["language"] == "typescript", (
        f"Expected language 'typescript' but got: {repr(data['language'])}"
    )


def test_yaml_summary_is_greet_a_user():
    """Priority 1: greet.script.yaml must have summary: 'Greet a user'"""
    data = _parse_simple_yaml(GREET_YAML)
    assert "summary" in data, (
        f"'summary' key missing from greet.script.yaml. Contents: {data}"
    )
    assert data["summary"] == "Greet a user", (
        f"Expected summary 'Greet a user' but got: {repr(data['summary'])}"
    )
