"""
Final state verification for the event_driven_etl_orchestrator task.

Verifies that the agent produced a correct Windmill WAC TypeScript workflow at
/home/user/windmill-project/f/workflows/etl_orchestrator.ts that implements:

1.  File existence
2.  WAC imports: step, parallel, waitForApproval, getResumeUrls
3.  Deduplication via processed_events.json
4.  parallel() with concurrency limit
5.  getResumeUrls() called inside a step()
6.  waitForApproval() with timeout
7.  enrichEvent function defined
8.  writeToWarehouse function defined
9.  workflow() wrapping main
10. Rejection branch (approved condition check)
11. State update after approval (writeFile / JSON.stringify + write)
"""

import re
import sys
import os

WORKFLOW_FILE = "/home/user/windmill-project/f/workflows/etl_orchestrator.ts"


# ── helpers ────────────────────────────────────────────────────────────────────

def _read_file() -> str:
    assert os.path.isfile(WORKFLOW_FILE), (
        f"Workflow file '{WORKFLOW_FILE}' does not exist. "
        "The agent must create this file."
    )
    with open(WORKFLOW_FILE, "r") as f:
        return f.read()


def _assert_pattern(source: str, pattern: str, flags: int = 0, msg: str = "") -> None:
    assert re.search(pattern, source, flags), (
        msg or f"Expected pattern not found in {WORKFLOW_FILE}:\n  pattern: {pattern!r}"
    )


# ── individual checks ──────────────────────────────────────────────────────────

def test_file_exists():
    """Check 1 – workflow file exists."""
    assert os.path.isfile(WORKFLOW_FILE), (
        f"'{WORKFLOW_FILE}' does not exist."
    )


def test_wac_imports():
    """Check 2 – imports step, parallel, waitForApproval, getResumeUrls from windmill-client."""
    source = _read_file()
    for symbol in ("step", "parallel", "waitForApproval", "getResumeUrls"):
        _assert_pattern(
            source,
            rf"\b{re.escape(symbol)}\b",
            msg=(
                f"WAC primitive '{symbol}' not found in {WORKFLOW_FILE}. "
                "It must be imported (or used) from 'windmill-client'."
            ),
        )
    # At least one import from windmill-client
    _assert_pattern(
        source,
        r"""from\s+['"]windmill-client['"]""",
        msg=(
            f"Expected an import from 'windmill-client' in {WORKFLOW_FILE}."
        ),
    )


def test_deduplication_state_file():
    """Check 3 – processed_events.json referenced for deduplication."""
    source = _read_file()
    _assert_pattern(
        source,
        r"processed_events\.json",
        msg=(
            f"'processed_events.json' not referenced in {WORKFLOW_FILE}. "
            "The workflow must read this file to deduplicate events."
        ),
    )


def test_parallel_with_concurrency():
    """Check 4 – parallel() call with concurrency limit present."""
    source = _read_file()
    _assert_pattern(
        source,
        r"parallel\s*\(",
        msg=f"'parallel(' not found in {WORKFLOW_FILE}.",
    )
    _assert_pattern(
        source,
        r"concurrency",
        msg=(
            f"'concurrency' option not found in {WORKFLOW_FILE}. "
            "parallel() must be called with a concurrency limit (e.g. concurrency: 5)."
        ),
    )


def test_get_resume_urls_in_step():
    """Check 5 – getResumeUrls() is called (inside a step)."""
    source = _read_file()
    _assert_pattern(
        source,
        r"getResumeUrls\s*\(\s*\)",
        msg=(
            f"'getResumeUrls()' call not found in {WORKFLOW_FILE}. "
            "The workflow must obtain approval/resume URLs before waiting."
        ),
    )
    # getResumeUrls should appear inside (or near) a step() call
    _assert_pattern(
        source,
        r"step\s*\(",
        msg=f"'step(' not found in {WORKFLOW_FILE}. getResumeUrls should be called within a step.",
    )


def test_wait_for_approval_with_timeout():
    """Check 6 – waitForApproval() with a timeout is present."""
    source = _read_file()
    _assert_pattern(
        source,
        r"waitForApproval\s*\(",
        msg=f"'waitForApproval(' not found in {WORKFLOW_FILE}.",
    )
    _assert_pattern(
        source,
        r"timeout",
        msg=(
            f"'timeout' not found near waitForApproval in {WORKFLOW_FILE}. "
            "waitForApproval must be called with a timeout option."
        ),
    )


def test_enrich_event_function():
    """Check 7 – enrichEvent function is defined."""
    source = _read_file()
    _assert_pattern(
        source,
        r"\benrichEvent\b",
        msg=(
            f"'enrichEvent' not found in {WORKFLOW_FILE}. "
            "The workflow must define or reference an enrichEvent task/function."
        ),
    )


def test_write_to_warehouse_function():
    """Check 8 – writeToWarehouse function is defined."""
    source = _read_file()
    _assert_pattern(
        source,
        r"\bwriteToWarehouse\b",
        msg=(
            f"'writeToWarehouse' not found in {WORKFLOW_FILE}. "
            "The workflow must define or reference a writeToWarehouse task/function."
        ),
    )


def test_workflow_main():
    """Check 9 – workflow() wrapping the main export is present."""
    source = _read_file()
    _assert_pattern(
        source,
        r"\bworkflow\s*\(",
        msg=(
            f"'workflow(' not found in {WORKFLOW_FILE}. "
            "The main function must be wrapped with workflow()."
        ),
    )


def test_rejection_branch():
    """Check 10 – a rejection branch checking the approval result is present."""
    source = _read_file()
    _assert_pattern(
        source,
        r"\bapproved\b",
        msg=(
            f"No 'approved' condition check found in {WORKFLOW_FILE}. "
            "The workflow must branch on the approval result and handle rejection."
        ),
    )


def test_state_update_after_approval():
    """Check 11 – processed_events.json is updated after approval."""
    source = _read_file()
    # Accept either writeFile (fs/promises) or a synchronous write pattern
    has_write_file = bool(re.search(r"\bwriteFile\b", source))
    has_stringify_write = bool(
        re.search(r"JSON\.stringify", source)
        and re.search(r"(writeFile|writeFileSync|fs\.write)", source)
    )
    assert has_write_file or has_stringify_write, (
        f"State update pattern not found in {WORKFLOW_FILE}. "
        "After approval, the workflow must write updated IDs back to processed_events.json "
        "using writeFile or a JSON.stringify + write pattern."
    )


# ── runner ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    checks = [
        test_file_exists,
        test_wac_imports,
        test_deduplication_state_file,
        test_parallel_with_concurrency,
        test_get_resume_urls_in_step,
        test_wait_for_approval_with_timeout,
        test_enrich_event_function,
        test_write_to_warehouse_function,
        test_workflow_main,
        test_rejection_branch,
        test_state_update_after_approval,
    ]

    failed = 0
    for check in checks:
        try:
            check()
            print(f"  PASS  {check.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {check.__name__}: {e}")
            failed += 1

    print()
    if failed:
        print(f"{failed}/{len(checks)} final-state check(s) failed.")
        sys.exit(1)
    else:
        print(f"All {len(checks)} final-state checks passed.")
        sys.exit(0)
