import os
import re

PROJECT_DIR = "/home/user/windmill-project"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "f", "workflows", "report_generator.ts")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _read_workflow() -> str:
    with open(WORKFLOW_FILE, "r", encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_workflow_file_exists():
    """report_generator.ts must exist at the expected path."""
    assert os.path.isfile(WORKFLOW_FILE), (
        f"Workflow file not found at '{WORKFLOW_FILE}'. "
        "Create 'f/workflows/report_generator.ts' inside the project directory."
    )


# ---------------------------------------------------------------------------
# Import checks
# ---------------------------------------------------------------------------

def test_imports_task_and_workflow_from_windmill_client():
    """The file must import both `task` and `workflow` from `windmill-client`."""
    content = _read_workflow()
    assert re.search(r'import\s+.*\btask\b.*from\s+["\']windmill-client["\']', content), (
        "Expected `task` to be imported from 'windmill-client'. "
        "Add: import { task, workflow } from 'windmill-client';"
    )
    assert re.search(r'import\s+.*\bworkflow\b.*from\s+["\']windmill-client["\']', content), (
        "Expected `workflow` to be imported from 'windmill-client'. "
        "Add: import { task, workflow } from 'windmill-client';"
    )


# ---------------------------------------------------------------------------
# Export: main = workflow(...)
# ---------------------------------------------------------------------------

def test_exports_main_as_workflow():
    """The file must export `main` assigned to a `workflow(...)` call."""
    content = _read_workflow()
    assert re.search(r'export\s+const\s+main\s*=\s*workflow\s*\(', content), (
        "Expected 'export const main = workflow(' in report_generator.ts. "
        "The entry point must be a workflow() wrapper."
    )


# ---------------------------------------------------------------------------
# Fan-out: Promise.all presence
# ---------------------------------------------------------------------------

def test_uses_promise_all_for_fan_out():
    """The workflow must use Promise.all() to dispatch parallel tasks (fan-out)."""
    content = _read_workflow()
    assert "Promise.all(" in content, (
        "Expected 'Promise.all(' in report_generator.ts. "
        "Use Promise.all([task(fetchSectionData)('summary'), ...]) for the fan-out pattern."
    )


# ---------------------------------------------------------------------------
# Fan-out: fetchSectionData dispatched for all three sections
# ---------------------------------------------------------------------------

def test_dispatches_fetch_section_data_for_summary():
    """task(fetchSectionData) must be called with 'summary'."""
    content = _read_workflow()
    assert re.search(r'task\s*\(\s*fetchSectionData\s*\)\s*\(\s*["\']summary["\']', content), (
        "Expected task(fetchSectionData)('summary') in the workflow body. "
        "Fan-out must dispatch fetchSectionData for the 'summary' section."
    )


def test_dispatches_fetch_section_data_for_details():
    """task(fetchSectionData) must be called with 'details'."""
    content = _read_workflow()
    assert re.search(r'task\s*\(\s*fetchSectionData\s*\)\s*\(\s*["\']details["\']', content), (
        "Expected task(fetchSectionData)('details') in the workflow body. "
        "Fan-out must dispatch fetchSectionData for the 'details' section."
    )


def test_dispatches_fetch_section_data_for_metrics():
    """task(fetchSectionData) must be called with 'metrics'."""
    content = _read_workflow()
    assert re.search(r'task\s*\(\s*fetchSectionData\s*\)\s*\(\s*["\']metrics["\']', content), (
        "Expected task(fetchSectionData)('metrics') in the workflow body. "
        "Fan-out must dispatch fetchSectionData for the 'metrics' section."
    )


# ---------------------------------------------------------------------------
# Fan-in: compileReport called after Promise.all
# ---------------------------------------------------------------------------

def test_calls_task_compile_report_for_fan_in():
    """task(compileReport) must be present — the fan-in aggregation step."""
    content = _read_workflow()
    assert re.search(r'task\s*\(\s*compileReport\s*\)', content), (
        "Expected 'task(compileReport)' in report_generator.ts. "
        "The fan-in step must call compileReport via task() after Promise.all completes."
    )


def test_compile_report_called_after_promise_all():
    """task(compileReport) must appear after Promise.all in the source."""
    content = _read_workflow()
    idx_promise_all = content.find("Promise.all(")
    idx_compile = content.find("task(compileReport)")
    # Handle whitespace variants
    if idx_compile == -1:
        m = re.search(r'task\s*\(\s*compileReport\s*\)', content)
        idx_compile = m.start() if m else -1
    assert idx_promise_all != -1, "Promise.all( not found."
    assert idx_compile != -1, "task(compileReport) not found."
    assert idx_promise_all < idx_compile, (
        "task(compileReport) must appear AFTER the Promise.all() fan-out in the workflow body. "
        "Fan-in (compile) happens only once all parallel tasks have resolved."
    )


# ---------------------------------------------------------------------------
# Function definitions
# ---------------------------------------------------------------------------

def test_defines_fetch_section_data_function():
    """fetchSectionData must be defined as a function in the file."""
    content = _read_workflow()
    assert re.search(r'\bfetchSectionData\b', content), (
        "Expected function 'fetchSectionData' to be defined in report_generator.ts."
    )


def test_defines_compile_report_function():
    """compileReport must be defined as a function in the file."""
    content = _read_workflow()
    assert re.search(r'\bcompileReport\b', content), (
        "Expected function 'compileReport' to be defined in report_generator.ts."
    )


# ---------------------------------------------------------------------------
# Section strings present in file
# ---------------------------------------------------------------------------

def test_section_strings_present():
    """All three section identifiers must appear in the file."""
    content = _read_workflow()
    for section in ("summary", "details", "metrics"):
        assert section in content, (
            f"Expected the section string '{section}' to appear in report_generator.ts. "
            f"Ensure task(fetchSectionData)('{section}') is dispatched in the fan-out."
        )
