import os
import re
from pathlib import Path

TARGET_FILE = Path("/home/user/windmill-project/f/workflows/cached_enricher.ts")


def _read_file() -> str:
    return TARGET_FILE.read_text(encoding="utf-8")


def test_cached_enricher_file_exists():
    """The cached_enricher.ts file must exist at the expected path."""
    assert TARGET_FILE.is_file(), (
        f"File '{TARGET_FILE}' does not exist. "
        "Ensure the workflow file was not accidentally deleted."
    )


def test_file_contains_cache_ttl_3600():
    """The file must contain `cache_ttl: 3600` to enable result caching."""
    content = _read_file()
    assert re.search(r"cache_ttl\s*:\s*3600", content), (
        "Expected `cache_ttl: 3600` in the file. "
        "Add it as the second argument to task(): task(enrichRecord, { cache_ttl: 3600 })(record)"
    )


def test_task_enrich_record_still_present():
    """The `task(enrichRecord` call must still be present — the function must not be removed."""
    content = _read_file()
    assert re.search(r"\btask\s*\(\s*enrichRecord", content), (
        "Expected `task(enrichRecord` to remain in the file. "
        "Do not remove or rename the enrichRecord task call."
    )


def test_task_save_results_still_present():
    """The `task(saveResults)` call must still be present and unchanged."""
    content = _read_file()
    assert re.search(r"\btask\s*\(\s*saveResults\s*\)", content), (
        "Expected `task(saveResults)` to remain in the file. "
        "Do not modify or remove the saveResults task call."
    )


def test_parallel_still_present():
    """The `parallel(` call must still be present — the parallel structure must be preserved."""
    content = _read_file()
    assert re.search(r"\bparallel\s*\(", content), (
        "Expected `parallel(` to remain in the file. "
        "Do not remove the parallel() structure when adding cache_ttl."
    )


def test_workflow_export_still_present():
    """The `workflow(` export must still be present — the main function wrapper must be preserved."""
    content = _read_file()
    assert re.search(r"\bworkflow\s*\(", content), (
        "Expected `workflow(` to remain in the file. "
        "Do not remove the workflow() export wrapper."
    )
