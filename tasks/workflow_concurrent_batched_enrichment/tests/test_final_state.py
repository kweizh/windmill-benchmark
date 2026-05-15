"""
Final state verification for workflow_concurrent_batched_enrichment.

Priority 3 checks — verifies all truth conditions using re.search patterns
against the content of /home/user/windmill-project/f/workflows/batch_enricher.ts.

Truth conditions:
  1.  File exists at the expected path
  2.  step( is present — used for run ID generation
  3.  parallel( is present — within-batch concurrency
  4.  concurrency_limit: 10 is present
  5.  concurrency_key: 'user-enrichment' or "user-enrichment" is present
  6.  enrichUser function is defined
  7.  aggregateResults function is defined
  8.  Loop pattern present (for...of / for / while)
  9.  task(aggregateResults) is called after the loop
  10. workflow( is present — main export uses Windmill workflow wrapper
"""

import os
import re

TARGET_FILE = "/home/user/windmill-project/f/workflows/batch_enricher.ts"


def _read_file():
    """Return the contents of the target file, or raise a clear assertion error."""
    assert os.path.isfile(TARGET_FILE), (
        f"Expected file '{TARGET_FILE}' to exist, but it was not found. "
        "The agent must create this file."
    )
    with open(TARGET_FILE, "r", encoding="utf-8") as fh:
        return fh.read()


# --------------------------------------------------------------------------- #
# Test 1 — File existence                                                       #
# --------------------------------------------------------------------------- #

def test_file_exists():
    """The batch_enricher.ts file must exist at the specified path."""
    assert os.path.isfile(TARGET_FILE), (
        f"'{TARGET_FILE}' does not exist. "
        "Create this file as part of the task."
    )


# --------------------------------------------------------------------------- #
# Test 2 — step( usage for run ID                                               #
# --------------------------------------------------------------------------- #

def test_step_used_for_run_id():
    """step() must be called to generate the run ID."""
    content = _read_file()
    assert re.search(r"\bstep\s*\(", content), (
        "Expected 'step(' to appear in the file for run ID generation, "
        "but it was not found. Use Windmill's step() primitive."
    )


# --------------------------------------------------------------------------- #
# Test 3 — parallel( usage                                                      #
# --------------------------------------------------------------------------- #

def test_parallel_used():
    """parallel() must be used for within-batch concurrency."""
    content = _read_file()
    assert re.search(r"\bparallel\s*\(", content), (
        "Expected 'parallel(' to appear in the file for concurrent batch "
        "processing, but it was not found."
    )


# --------------------------------------------------------------------------- #
# Test 4 — concurrency_limit: 10                                                #
# --------------------------------------------------------------------------- #

def test_concurrency_limit_10():
    """concurrency_limit must be set to exactly 10."""
    content = _read_file()
    assert re.search(r"concurrency_limit\s*:\s*10\b", content), (
        "Expected 'concurrency_limit: 10' in the task() options for enrichUser, "
        "but it was not found. The limit must be exactly 10."
    )


# --------------------------------------------------------------------------- #
# Test 5 — concurrency_key: 'user-enrichment'                                   #
# --------------------------------------------------------------------------- #

def test_concurrency_key_user_enrichment():
    """concurrency_key must be set to 'user-enrichment' (single or double quotes)."""
    content = _read_file()
    assert re.search(r'concurrency_key\s*:\s*["\']user-enrichment["\']', content), (
        "Expected `concurrency_key: 'user-enrichment'` (or double-quoted) in the "
        "task() options, but it was not found."
    )


# --------------------------------------------------------------------------- #
# Test 6 — enrichUser function defined                                           #
# --------------------------------------------------------------------------- #

def test_enrich_user_function_defined():
    """enrichUser must be defined as a named function."""
    content = _read_file()
    assert re.search(r"\benrichUser\b", content), (
        "Expected 'enrichUser' to be defined in the file, but it was not found."
    )
    # Must look like a function definition (function keyword or arrow function assigned)
    assert re.search(
        r"(function\s+enrichUser|enrichUser\s*[=:]\s*(async\s*)?\(|async\s+function\s+enrichUser)",
        content,
    ), (
        "Found 'enrichUser' in the file but it does not appear to be defined as a function. "
        "Define it as a named async function or arrow function."
    )


# --------------------------------------------------------------------------- #
# Test 7 — aggregateResults function defined                                     #
# --------------------------------------------------------------------------- #

def test_aggregate_results_function_defined():
    """aggregateResults must be defined as a named function."""
    content = _read_file()
    assert re.search(r"\baggregateResults\b", content), (
        "Expected 'aggregateResults' to be defined in the file, but it was not found."
    )
    assert re.search(
        r"(function\s+aggregateResults|aggregateResults\s*[=:]\s*(async\s*)?\(|async\s+function\s+aggregateResults)",
        content,
    ), (
        "Found 'aggregateResults' in the file but it does not appear to be defined as a function. "
        "Define it as a named async function or arrow function."
    )


# --------------------------------------------------------------------------- #
# Test 8 — Loop pattern for sequential batch processing                         #
# --------------------------------------------------------------------------- #

def test_loop_pattern_present():
    """A loop (for...of, for, or while) must be present for sequential batch processing."""
    content = _read_file()
    assert re.search(r"\b(for\s*\(|for\s+\w+\s+of\s+|while\s*\()", content), (
        "Expected a loop construct (for, for...of, or while) for sequential batch "
        "processing, but none was found."
    )


# --------------------------------------------------------------------------- #
# Test 9 — task(aggregateResults) called after the loop                         #
# --------------------------------------------------------------------------- #

def test_task_aggregate_results_called():
    """task(aggregateResults) must be called to perform the final aggregation."""
    content = _read_file()
    assert re.search(r"\btask\s*\(\s*aggregateResults\s*\)", content), (
        "Expected 'task(aggregateResults)' to be called after the batch loop, "
        "but it was not found."
    )


# --------------------------------------------------------------------------- #
# Test 10 — workflow( present — main export uses Windmill workflow wrapper       #
# --------------------------------------------------------------------------- #

def test_workflow_wrapper_used():
    """The main exported function must be declared with workflow()."""
    content = _read_file()
    assert re.search(r"\bworkflow\s*\(", content), (
        "Expected 'workflow(' to appear in the file — the main function must be "
        "wrapped with Windmill's workflow() primitive, but it was not found."
    )
