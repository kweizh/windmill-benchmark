import os
import re
import pytest

PROJECT_DIR = "/home/user/windmill-project"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "f", "scripts", "greet.ts")
METADATA_PATH = os.path.join(PROJECT_DIR, "f", "scripts", "greet.script.yaml")


def test_greet_ts_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Script file '{SCRIPT_PATH}' does not exist. "
        "Create f/scripts/greet.ts inside the project directory."
    )


def test_greet_ts_exports_main():
    with open(SCRIPT_PATH) as f:
        content = f.read()
    assert "export" in content, (
        f"'{SCRIPT_PATH}' does not contain an 'export' statement. "
        "The main function must be exported."
    )
    assert "main" in content, (
        f"'{SCRIPT_PATH}' does not define a function named 'main'. "
        "Windmill scripts must export a function called 'main'."
    )


def test_greet_ts_has_name_string_param():
    with open(SCRIPT_PATH) as f:
        content = f.read()
    # Accept 'name: string' or 'name:string' patterns
    assert re.search(r"name\s*:\s*string", content) is not None, (
        f"'{SCRIPT_PATH}' does not declare a 'name: string' parameter in the main function. "
        "The signature must include 'name: string'."
    )


def test_greet_ts_has_age_number_param():
    with open(SCRIPT_PATH) as f:
        content = f.read()
    # Accept 'age: number' or 'age:number' patterns
    assert re.search(r"age\s*:\s*number", content) is not None, (
        f"'{SCRIPT_PATH}' does not declare an 'age: number' parameter in the main function. "
        "The signature must include 'age: number'."
    )


def test_greet_script_yaml_exists():
    assert os.path.isfile(METADATA_PATH), (
        f"Metadata file '{METADATA_PATH}' does not exist. "
        "Create f/scripts/greet.script.yaml alongside the TypeScript file."
    )


def test_greet_script_yaml_has_summary():
    with open(METADATA_PATH) as f:
        content = f.read()
    assert "summary" in content, (
        f"'{METADATA_PATH}' does not contain a 'summary' field. "
        "The companion YAML must include a 'summary' key."
    )


def test_greet_script_yaml_has_name_in_schema():
    with open(METADATA_PATH) as f:
        content = f.read()
    assert "name" in content, (
        f"'{METADATA_PATH}' schema does not reference the 'name' parameter. "
        "The schema section must list 'name' as an input property."
    )


def test_greet_script_yaml_has_age_in_schema():
    with open(METADATA_PATH) as f:
        content = f.read()
    assert "age" in content, (
        f"'{METADATA_PATH}' schema does not reference the 'age' parameter. "
        "The schema section must list 'age' as an input property."
    )
