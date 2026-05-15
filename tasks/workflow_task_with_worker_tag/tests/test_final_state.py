import pathlib
import re
import pytest


WORKFLOW_FILE = pathlib.Path("/home/user/windmill-project/f/workflows/ml_pipeline.ts")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_workflow_file_exists():
    """The ml_pipeline.ts file must exist after the fix."""
    assert WORKFLOW_FILE.is_file(), (
        f"Workflow file {WORKFLOW_FILE} does not exist."
    )


# ---------------------------------------------------------------------------
# GPU tag presence
# ---------------------------------------------------------------------------


def test_gpu_tag_present_in_file():
    """
    The file must contain `tag: 'gpu'` or `tag: "gpu"` after the fix.
    """
    content = WORKFLOW_FILE.read_text()
    assert re.search(r"tag\s*:\s*['\"]gpu['\"]", content), (
        "Expected `tag: 'gpu'` (or double-quoted variant) to be present in ml_pipeline.ts. "
        "Add `{ tag: 'gpu' }` as the second argument to `task(trainModel, { tag: 'gpu' })`."
    )


def test_gpu_tag_associated_with_train_model():
    """
    The `tag: 'gpu'` option must appear in the same task invocation as `trainModel`.
    Checks that `task(trainModel` and `tag: 'gpu'` are within 120 characters of each other.
    """
    content = WORKFLOW_FILE.read_text()
    # Find the position of task(trainModel
    match_task = re.search(r"task\s*\(\s*trainModel", content)
    assert match_task is not None, (
        "`task(trainModel` not found in ml_pipeline.ts."
    )
    # Find the nearest tag: 'gpu' after task(trainModel
    search_region = content[match_task.start():match_task.start() + 120]
    assert re.search(r"tag\s*:\s*['\"]gpu['\"]", search_region), (
        "Expected `tag: 'gpu'` to appear within the `task(trainModel, { tag: 'gpu' })` call. "
        "Make sure the options object `{ tag: 'gpu' }` is passed as the second argument to `task(trainModel, ...)`."
    )


# ---------------------------------------------------------------------------
# preprocessData must NOT have a tag
# ---------------------------------------------------------------------------


def test_preprocess_data_task_has_no_tag():
    """
    `task(preprocessData)` must remain without any tag option.
    Verifies that `tag` does not appear within 120 chars after `task(preprocessData`.
    """
    content = WORKFLOW_FILE.read_text()
    match_preprocess = re.search(r"task\s*\(\s*preprocessData", content)
    assert match_preprocess is not None, (
        "`task(preprocessData` not found in ml_pipeline.ts. "
        "The preprocessData task call must remain in the workflow."
    )
    # Inspect the region immediately following task(preprocessData to check for tag
    search_region = content[match_preprocess.start():match_preprocess.start() + 80]
    assert not re.search(r"tag\s*:\s*['\"]", search_region), (
        "Found a `tag:` option near `task(preprocessData`. "
        "`preprocessData` must run on any worker without a tag — do not add a tag to it."
    )


def test_preprocess_data_call_present():
    """The `task(preprocessData)` call must still be present in the file."""
    content = WORKFLOW_FILE.read_text()
    assert "task(preprocessData)" in content, (
        "`task(preprocessData)` call was removed or modified. "
        "Keep `await task(preprocessData)(rawData)` unchanged."
    )


# ---------------------------------------------------------------------------
# Workflow structure integrity
# ---------------------------------------------------------------------------


def test_workflow_wrapper_intact():
    """The `workflow(` wrapper must still be present in the file."""
    content = WORKFLOW_FILE.read_text()
    assert "workflow(" in content, (
        "`workflow(` wrapper was removed from ml_pipeline.ts. Keep the workflow() wrapper intact."
    )


def test_train_model_task_still_referenced():
    """The `task(trainModel` call must still be present in the file."""
    content = WORKFLOW_FILE.read_text()
    assert "task(trainModel" in content, (
        "`task(trainModel` was removed from ml_pipeline.ts. "
        "The trainModel task call must remain; only add the `{ tag: 'gpu' }` options argument."
    )


def test_main_export_signature_intact():
    """The `export const main` signature must remain unchanged."""
    content = WORKFLOW_FILE.read_text()
    assert "export const main" in content, (
        "`export const main` signature was removed or modified. Keep the main export intact."
    )


def test_windmill_client_import_intact():
    """The import from `windmill-client` must still be present."""
    content = WORKFLOW_FILE.read_text()
    assert "windmill-client" in content, (
        "Import from `windmill-client` was removed from ml_pipeline.ts. Keep the import intact."
    )


# ---------------------------------------------------------------------------
# Correct task(trainModel, { tag: 'gpu' }) invocation form
# ---------------------------------------------------------------------------


def test_train_model_uses_options_object_form():
    """
    The fixed call must use `task(trainModel, { tag: 'gpu' })` — i.e. the options
    object is the second positional argument to `task()`, not appended elsewhere.
    Accepts single or double quotes for the tag value.
    """
    content = WORKFLOW_FILE.read_text()
    assert re.search(
        r"task\s*\(\s*trainModel\s*,\s*\{[^}]*tag\s*:\s*['\"]gpu['\"][^}]*\}\s*\)",
        content,
    ), (
        "Expected `task(trainModel, { tag: 'gpu' })` form not found. "
        "The options object `{ tag: 'gpu' }` must be the second argument to `task()`: "
        "`await task(trainModel, { tag: 'gpu' })(processedData)`."
    )
