import os
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
SCRIPT_FILE = os.path.join(SCRIPTS_DIR, "db_row_count.ts")
YAML_FILE = os.path.join(SCRIPTS_DIR, "db_row_count.script.yaml")


# ---------------------------------------------------------------------------
# Priority 3: File / content checks (no Windmill server available)
# ---------------------------------------------------------------------------

def test_script_file_exists():
    """db_row_count.ts must exist at the required path."""
    assert os.path.isfile(SCRIPT_FILE), (
        f"Script file not found at {SCRIPT_FILE!r}. "
        "Create the TypeScript script at the specified path."
    )


def test_postgresql_type_defined():
    """db_row_count.ts must define a Postgresql type with the required fields."""
    with open(SCRIPT_FILE) as f:
        content = f.read()

    assert "Postgresql" in content, (
        "Expected a 'Postgresql' type definition in db_row_count.ts, but none was found."
    )

    required_fields = ["host", "port", "user", "dbname", "sslmode", "password"]
    for field in required_fields:
        assert field in content, (
            f"Expected field '{field}' to be present in the Postgresql type definition "
            f"in {SCRIPT_FILE!r}, but it was not found."
        )


def test_main_function_exported():
    """db_row_count.ts must export an async main function."""
    with open(SCRIPT_FILE) as f:
        content = f.read()

    assert "export" in content and "function main" in content, (
        "Expected an exported 'main' function in db_row_count.ts. "
        "Make sure the function is declared as 'export async function main(...)' or 'export function main(...)'."
    )


def test_main_accepts_db_parameter():
    """main() must accept a db parameter typed as Postgresql."""
    with open(SCRIPT_FILE) as f:
        content = f.read()

    assert "db" in content and "Postgresql" in content, (
        "Expected the main function to accept a 'db: Postgresql' parameter in db_row_count.ts."
    )

    # Heuristic: the parameter list should contain both 'db' and 'table_name'
    assert "table_name" in content, (
        "Expected the main function to accept a 'table_name' parameter in db_row_count.ts."
    )


def test_return_value_contains_required_keys():
    """main() must return an object with host, dbname, table, query, and note keys."""
    with open(SCRIPT_FILE) as f:
        content = f.read()

    for key in ["host", "dbname", "table", "query", "note"]:
        assert key in content, (
            f"Expected return object key '{key}' to appear in db_row_count.ts, but it was missing."
        )


def test_return_note_value():
    """The note field in the return value must equal 'Resource received successfully'."""
    with open(SCRIPT_FILE) as f:
        content = f.read()

    assert "Resource received successfully" in content, (
        "Expected the return object's 'note' field to equal "
        "'Resource received successfully' in db_row_count.ts."
    )


def test_companion_yaml_exists():
    """db_row_count.script.yaml must exist alongside the TypeScript script."""
    assert os.path.isfile(YAML_FILE), (
        f"Companion YAML file not found at {YAML_FILE!r}. "
        "Create the script metadata YAML at the specified path."
    )


def test_yaml_contains_db_property_with_resource_format():
    """The companion YAML must declare a 'db' property with format 'resource-postgresql'."""
    with open(YAML_FILE) as f:
        content = f.read()

    assert "db" in content, (
        f"Expected a 'db' property in the schema section of {YAML_FILE!r}, but it was not found."
    )

    assert "resource-postgresql" in content, (
        f"Expected 'resource-postgresql' format for the 'db' property in {YAML_FILE!r}."
    )


def test_yaml_contains_table_name_property():
    """The companion YAML must declare a 'table_name' string property."""
    with open(YAML_FILE) as f:
        content = f.read()

    assert "table_name" in content, (
        f"Expected a 'table_name' property in the schema section of {YAML_FILE!r}, "
        "but it was not found."
    )
