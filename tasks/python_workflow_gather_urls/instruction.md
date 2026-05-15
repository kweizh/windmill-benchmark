# Build a Python Windmill Workflow to Monitor URLs in Parallel

## Background

Windmill supports Python for Workflows-as-Code (WAC). Use the `@workflow` decorator on your entry function and `@task` on functions that should run as separate child jobs. Multiple tasks can be dispatched in parallel using `asyncio.gather()`.

```python
from wmill import workflow, task
import asyncio

@task
async def check_url(url: str) -> dict:
    # runs as a separate child job
    ...

@workflow
async def main(urls: list) -> dict:
    results = await asyncio.gather(*[check_url(u) for u in urls])
    ...
```

## Requirements

Create a workflow at `/home/user/windmill-project/f/workflows/url_monitor.py` that:

1. Defines a `check_url` task (decorated with `@task`) that accepts `url: str` and returns `{'url': url, 'status': int, 'ok': bool}`. Use `urllib.request.urlopen` with a 5-second timeout to get the status code. On any exception, return `{'url': url, 'status': 0, 'ok': False}`.
2. Defines an `aggregate` task (decorated with `@task`) that accepts a `results: list` and returns `{'total': len(results), 'successful': count of ok==True, 'failed': count of ok==False}`.
3. Exports a `main` function (decorated with `@workflow`) that:
   - Accepts `urls: list` as input.
   - Uses `asyncio.gather(*[check_url(u) for u in urls])` to fetch all URLs in parallel.
   - Passes the results list to `aggregate(results)` (awaited).
   - Returns the summary dict.

## Implementation Guide

1. Create `/home/user/windmill-project/f/workflows/url_monitor.py`.
2. Import `workflow`, `task` from `wmill`; import `asyncio` and `urllib.request`.
3. Implement `check_url` with `@task` decorator.
4. Implement `aggregate` with `@task` decorator.
5. Implement `main` with `@workflow` decorator.

## Constraints

- Project path: `/home/user/windmill-project`
- Output file: `/home/user/windmill-project/f/workflows/url_monitor.py`
- Use `urllib.request.urlopen` (stdlib only, no `requests` or `httpx`).
- The `check_url` function MUST handle all exceptions with try/except and return `{'url': url, 'status': 0, 'ok': False}` on error.
- No live Windmill server is required.
