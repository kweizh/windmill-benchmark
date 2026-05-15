import os
import re
import pytest

ETL_FILE = "/home/user/windmill-project/f/workflows/etl_pipeline.py"

def _read_file():
    with open(ETL_FILE) as f:
        return f.read()

def test_file_exists():
    assert os.path.isfile(ETL_FILE), \
        f"etl_pipeline.py not found at {ETL_FILE}."

def test_imports_workflow_task_parallel():
    content = _read_file()
    assert re.search(r'from\s+wmill\s+import\s+[^\n]*workflow', content), \
        "Expected 'workflow' imported from 'wmill'."
    assert re.search(r'from\s+wmill\s+import\s+[^\n]*task', content), \
        "Expected 'task' imported from 'wmill'."
    assert re.search(r'from\s+wmill\s+import\s+[^\n]*parallel', content), \
        "Expected 'parallel' imported from 'wmill'."

def test_task_decorator_used_at_least_three_times():
    content = _read_file()
    count = len(re.findall(r'@task', content))
    assert count >= 3, \
        f"Expected @task decorator at least 3 times, found {count}."

def test_workflow_decorator_used():
    content = _read_file()
    assert re.search(r'@workflow', content), \
        "Expected @workflow decorator on the main function."

def test_parallel_with_concurrency_4():
    content = _read_file()
    assert re.search(r'parallel\s*\(.*?concurrency\s*=\s*4', content, re.DOTALL), \
        "Expected parallel() call with concurrency=4 for extraction."

def test_parallel_with_concurrency_10():
    content = _read_file()
    assert re.search(r'parallel\s*\(.*?concurrency\s*=\s*10', content, re.DOTALL), \
        "Expected parallel() call with concurrency=10 for transformation."

def test_extract_function_defined():
    content = _read_file()
    assert re.search(r'async\s+def\s+extract\s*\(', content), \
        "Expected 'extract' async function defined."

def test_extract_has_try_except():
    content = _read_file()
    assert 'try:' in content or 'try :' in content, \
        "Expected try/except error handling in extract function."

def test_transform_function_defined():
    content = _read_file()
    assert re.search(r'async\s+def\s+transform\s*\(', content), \
        "Expected 'transform' async function defined."

def test_load_function_defined():
    content = _read_file()
    assert re.search(r'async\s+def\s+load\s*\(', content), \
        "Expected 'load' async function defined."
