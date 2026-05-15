import os
import re


TARGET_FILE = "/home/user/windmill-project/f/workflows/batch_processor.ts"


def _read_file():
    with open(TARGET_FILE, "r", encoding="utf-8") as fh:
        return fh.read()


def test_batch_processor_file_exists():
    """The batch_processor.ts file must exist at the expected path."""
    assert os.path.isfile(TARGET_FILE), (
        f"File '{TARGET_FILE}' does not exist. "
        "Create it as instructed in the task description."
    )


def test_imports_parallel_from_windmill_client():
    """The file must import `parallel` from `windmill-client`."""
    content = _read_file()
    # Accept any import style: named import or namespace import
    assert re.search(r'import\s+.*\bparallel\b.*from\s+["\']windmill-client["\']', content), (
        "Expected `parallel` to be imported from 'windmill-client'. "
        "Add: import { task, workflow, parallel } from 'windmill-client';"
    )


def test_defines_checkurl_function():
    """The file must define a `checkUrl` function."""
    content = _read_file()
    assert re.search(r'\bcheckUrl\b', content), (
        "Expected a `checkUrl` function definition in the file."
    )


def test_defines_summarize_function():
    """The file must define a `summarize` function."""
    content = _read_file()
    assert re.search(r'\bsummarize\b', content), (
        "Expected a `summarize` function definition in the file."
    )


def test_uses_concurrency_3():
    """The parallel() call must specify `concurrency: 3`."""
    content = _read_file()
    assert re.search(r'concurrency\s*:\s*3', content), (
        "Expected `concurrency: 3` in the parallel() options argument. "
        "Use: parallel(urls, (url) => task(checkUrl)(url), { concurrency: 3 })"
    )


def test_exports_main_with_workflow():
    """The file must export `main` using the `workflow()` wrapper."""
    content = _read_file()
    assert re.search(r'\bworkflow\s*\(', content), (
        "Expected `workflow(` call to define the exported main function. "
        "Use: export const main = workflow(async (urls: string[]) => { ... });"
    )


def test_wraps_checkurl_with_task():
    """The file must wrap `checkUrl` with `task()`."""
    content = _read_file()
    assert re.search(r'\btask\s*\(\s*checkUrl\s*\)', content), (
        "Expected `task(checkUrl)` in the workflow body. "
        "Use: parallel(urls, (url) => task(checkUrl)(url), { concurrency: 3 })"
    )


def test_wraps_summarize_with_task():
    """The file must wrap `summarize` with `task()`."""
    content = _read_file()
    assert re.search(r'\btask\s*\(\s*summarize\s*\)', content), (
        "Expected `task(summarize)` in the workflow body to invoke the summarize step."
    )
