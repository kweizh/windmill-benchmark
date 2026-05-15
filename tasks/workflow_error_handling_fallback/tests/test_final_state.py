import re


WORKFLOW_FILE = "/home/user/windmill-project/f/workflows/data_pipeline.ts"


def _read_file() -> str:
    with open(WORKFLOW_FILE, "r") as f:
        return f.read()


def test_file_exists():
    """The workflow file must still exist after agent edits."""
    import os
    assert os.path.isfile(WORKFLOW_FILE), (
        f"{WORKFLOW_FILE} does not exist"
    )


def test_has_try_block():
    """The workflow must contain a try block wrapping task(fetchData)."""
    content = _read_file()
    assert re.search(r"\btry\s*\{", content), (
        "data_pipeline.ts does not contain a 'try {' block"
    )


def test_has_catch_block():
    """The workflow must contain a catch block."""
    content = _read_file()
    assert re.search(r"\bcatch\s*\(", content), (
        "data_pipeline.ts does not contain a 'catch (' block"
    )


def test_catch_invokes_fallback_data():
    """The catch block must call task(fallbackData)(source)."""
    content = _read_file()
    # task(fallbackData) must appear in the file
    assert "task(fallbackData)" in content, (
        "data_pipeline.ts does not call task(fallbackData) in the catch block"
    )
    # Verify fallbackData call is paired with (source)
    assert re.search(r"task\(fallbackData\)\s*\(\s*source\s*\)", content), (
        "task(fallbackData) is not called with 'source' argument"
    )


def test_catch_logs_fetch_data_failed():
    """The catch block must contain a console.log mentioning 'fetchData failed'."""
    content = _read_file()
    assert "fetchData failed" in content, (
        "data_pipeline.ts catch block does not log 'fetchData failed'"
    )
    assert re.search(r"console\.log\(", content), (
        "data_pipeline.ts does not contain a console.log() call"
    )


def test_transform_task_still_present():
    """The task(transform) call must still exist after the try/catch."""
    content = _read_file()
    assert "task(transform)" in content, (
        "data_pipeline.ts no longer contains task(transform) — it may have been accidentally removed"
    )


def test_main_export_unchanged():
    """The exported main workflow signature must still be present."""
    content = _read_file()
    assert "export const main" in content, (
        "data_pipeline.ts no longer exports 'main'"
    )


def test_fetch_data_task_call_inside_try():
    """task(fetchData) must appear inside the try block (before catch)."""
    content = _read_file()
    # The try block must come before the catch block, and fetchData must
    # appear between them. We check ordering via character index.
    try_match = re.search(r"\btry\s*\{", content)
    catch_match = re.search(r"\bcatch\s*\(", content)
    fetch_match = re.search(r"task\(fetchData\)", content)

    assert try_match, "No try block found"
    assert catch_match, "No catch block found"
    assert fetch_match, "No task(fetchData) call found"

    assert try_match.start() < fetch_match.start() < catch_match.start(), (
        "task(fetchData) does not appear to be inside the try block "
        "(expected: try ... task(fetchData) ... catch)"
    )


def test_fallback_data_function_definition_present():
    """The fallbackData function definition must not have been removed."""
    content = _read_file()
    assert "async function fallbackData" in content, (
        "The fallbackData function definition was removed from data_pipeline.ts"
    )


def test_fetch_data_function_definition_present():
    """The fetchData function definition must not have been removed."""
    content = _read_file()
    assert "async function fetchData" in content, (
        "The fetchData function definition was removed from data_pipeline.ts"
    )


def test_transform_function_definition_present():
    """The transform function definition must not have been removed."""
    content = _read_file()
    assert "async function transform" in content, (
        "The transform function definition was removed from data_pipeline.ts"
    )
