import pathlib
import re
import pytest


WORKFLOW_FILE = pathlib.Path("/home/user/windmill-project/f/workflows/order_processor.ts")


# ---------------------------------------------------------------------------
# Priority 3: File checks
# ---------------------------------------------------------------------------


def test_workflow_file_exists():
    """The order_processor.ts file must exist after the fix."""
    assert WORKFLOW_FILE.is_file(), (
        f"Workflow file {WORKFLOW_FILE} does not exist."
    )


def test_step_imported_from_windmill_client():
    """
    `step` must be imported from `windmill-client`.
    Accepts both named and combined import forms, e.g.:
      import { task, workflow, step } from 'windmill-client';
    """
    content = WORKFLOW_FILE.read_text()
    # Look for an import statement from windmill-client that includes `step`
    assert re.search(
        r"import\s*\{[^}]*\bstep\b[^}]*\}\s*from\s*['\"]windmill-client['\"]",
        content,
    ), (
        "`step` is not imported from `windmill-client`. "
        "Add `step` to the import statement, e.g.: "
        "import { task, workflow, step } from 'windmill-client';"
    )


def test_timestamp_wrapped_in_step():
    """
    `Date.now()` must be wrapped in a `step()` call with key 'timestamp'.
    Expected pattern: await step('timestamp', () => Date.now())
    """
    content = WORKFLOW_FILE.read_text()
    assert re.search(
        r"await\s+step\s*\(\s*['\"]timestamp['\"]",
        content,
    ), (
        "Expected `await step('timestamp', ...)` wrapping `Date.now()`. "
        "Replace `const timestamp = Date.now();` with "
        "`const timestamp = await step('timestamp', () => Date.now());`"
    )


def test_order_id_wrapped_in_step():
    """
    `Math.random()` must be wrapped in a `step()` call with key 'order_id'.
    Expected pattern: await step('order_id', () => Math.random()...)
    """
    content = WORKFLOW_FILE.read_text()
    assert re.search(
        r"await\s+step\s*\(\s*['\"]order_id['\"]",
        content,
    ), (
        "Expected `await step('order_id', ...)` wrapping `Math.random()`. "
        "Replace `const orderId = Math.random().toString(36).slice(2);` with "
        "`const orderId = await step('order_id', () => Math.random().toString(36).slice(2));`"
    )


def test_no_bare_date_now_in_workflow_body():
    """
    Bare `Date.now()` (i.e., not inside a step() arrow-function callback)
    must NOT appear in the workflow body as a direct assignment.
    The pattern `const timestamp = Date.now()` must be gone.
    """
    content = WORKFLOW_FILE.read_text()
    # Match the broken pattern: direct assignment without step()
    assert not re.search(
        r"const\s+timestamp\s*=\s*Date\.now\(\)",
        content,
    ), (
        "Found bare `const timestamp = Date.now()` in workflow body. "
        "`Date.now()` must be wrapped in `step('timestamp', () => Date.now())`."
    )


def test_no_bare_math_random_in_workflow_body():
    """
    Bare `Math.random()` (i.e., not inside a step() arrow-function callback)
    must NOT appear in the workflow body as a direct assignment.
    The pattern `const orderId = Math.random()` must be gone.
    """
    content = WORKFLOW_FILE.read_text()
    # Match the broken pattern: direct assignment without step()
    assert not re.search(
        r"const\s+orderId\s*=\s*Math\.random\(\)",
        content,
    ), (
        "Found bare `const orderId = Math.random()` in workflow body. "
        "`Math.random()` must be wrapped in `step('order_id', () => Math.random()...)`."
    )


def test_task_process_order_call_intact():
    """The `task(processOrder)` call must remain unchanged."""
    content = WORKFLOW_FILE.read_text()
    assert "task(processOrder)" in content, (
        "`task(processOrder)` call was removed or renamed. Keep all task() calls intact."
    )


def test_task_notify_shipping_call_intact():
    """The `task(notifyShipping)` call must remain unchanged."""
    content = WORKFLOW_FILE.read_text()
    assert "task(notifyShipping)" in content, (
        "`task(notifyShipping)` call was removed or renamed. Keep all task() calls intact."
    )


def test_main_export_signature_intact():
    """The `export const main` signature must remain unchanged."""
    content = WORKFLOW_FILE.read_text()
    assert "export const main" in content, (
        "`export const main` signature was removed or modified."
    )


def test_date_now_only_inside_step_callback():
    """
    If `Date.now()` appears in the file at all, it must only appear inside
    a step() arrow-function callback, never as a standalone expression in
    the workflow body.
    """
    content = WORKFLOW_FILE.read_text()
    # Find all occurrences of Date.now() and check each one is preceded by
    # an arrow function inside step()
    for match in re.finditer(r"Date\.now\(\)", content):
        start = match.start()
        # Look backwards for the step( pattern within a reasonable window
        window = content[max(0, start - 60):start]
        assert re.search(r"step\s*\([^)]*,\s*\(\s*\)\s*=>", window), (
            f"Found `Date.now()` at position {start} that does not appear to be "
            "inside a step() arrow-function callback. All Date.now() calls must be "
            "wrapped: step('timestamp', () => Date.now())"
        )


def test_math_random_only_inside_step_callback():
    """
    If `Math.random()` appears in the file at all, it must only appear inside
    a step() arrow-function callback, never as a standalone expression in
    the workflow body.
    """
    content = WORKFLOW_FILE.read_text()
    for match in re.finditer(r"Math\.random\(\)", content):
        start = match.start()
        window = content[max(0, start - 60):start]
        assert re.search(r"step\s*\([^)]*,\s*\(\s*\)\s*=>", window), (
            f"Found `Math.random()` at position {start} that does not appear to be "
            "inside a step() arrow-function callback. All Math.random() calls must be "
            "wrapped: step('order_id', () => Math.random()...)"
        )
