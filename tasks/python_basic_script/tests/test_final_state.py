import os
import subprocess
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
HELLO_PY = os.path.join(SCRIPTS_DIR, "hello.py")
HELLO_YAML = os.path.join(SCRIPTS_DIR, "hello.script.yaml")


def test_hello_py_exists():
    assert os.path.isfile(HELLO_PY), f"Expected Python script at '{HELLO_PY}' but it was not found."


def test_hello_script_yaml_exists():
    assert os.path.isfile(HELLO_YAML), f"Expected metadata file at '{HELLO_YAML}' but it was not found."


def _run_main(name: str) -> str:
    """Execute main() from hello.py via python3 -c and return its output."""
    script = (
        f"import importlib.util, sys\n"
        f"spec = importlib.util.spec_from_file_location('hello', '{HELLO_PY}')\n"
        f"mod = importlib.util.module_from_spec(spec)\n"
        f"spec.loader.exec_module(mod)\n"
        f"print(mod.main({repr(name)}))\n"
    )
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, (
        f"python3 execution failed (exit {result.returncode}):\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return result.stdout.strip()


def test_main_hello_world():
    """Priority 1: main('World') must return 'Hello, World!'"""
    assert _run_main("World") == "Hello, World!", (
        f"Expected 'Hello, World!' but got: {repr(_run_main('World'))}"
    )


def test_main_hello_alice():
    """Priority 1: main('Alice') must return 'Hello, Alice!'"""
    assert _run_main("Alice") == "Hello, Alice!", (
        f"Expected 'Hello, Alice!' but got: {repr(_run_main('Alice'))}"
    )


def test_main_hello_bob():
    """Priority 1: main('Bob') must return 'Hello, Bob!'"""
    assert _run_main("Bob") == "Hello, Bob!", (
        f"Expected 'Hello, Bob!' but got: {repr(_run_main('Bob'))}"
    )


def _parse_simple_yaml(path: str) -> dict:
    result = {}
    with open(path) as fh:
        for line in fh:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def test_yaml_language_is_python3():
    data = _parse_simple_yaml(HELLO_YAML)
    assert "language" in data, f"'language' key missing from hello.script.yaml. Contents: {data}"
    assert data["language"] == "python3", f"Expected language 'python3' but got: {repr(data['language'])}"


def test_yaml_summary_correct():
    data = _parse_simple_yaml(HELLO_YAML)
    assert "summary" in data, f"'summary' key missing from hello.script.yaml. Contents: {data}"
    assert data["summary"] == "Say hello to a user", (
        f"Expected summary 'Say hello to a user' but got: {repr(data['summary'])}"
    )
