# Windmill Workflow: Self-Healing API Data Pipeline
#
# Parameters:
#   endpoints  : list  – list of URL strings to fetch
#   max_retries: int   – maximum number of retry attempts per endpoint (default 3)
#
# The workflow fetches all endpoints in parallel (concurrency=3) with exponential
# backoff retry, computes a health report, writes it to pipeline_report.json,
# and returns the report dict.

import asyncio
import json
import urllib.request
import urllib.error
from typing import Any

import wmill
from wmill import task, parallel


# ---------------------------------------------------------------------------
# Helper: fetch a single URL with exponential-backoff retries
# ---------------------------------------------------------------------------

@task
async def fetch_with_retry(url: str, max_retries: int) -> dict[str, Any]:
    """
    Attempt to GET *url* up to *max_retries* times.

    Delay schedule (asyncio.sleep, NOT wmill sleep primitive):
      attempt 0 → no prior sleep
      attempt 1 → sleep 2^0 = 1 s  after first failure
      attempt 2 → sleep 2^1 = 2 s  after second failure
      attempt 3 → sleep 2^2 = 4 s  after third failure
      …

    Returns:
        {
            'endpoint': str,
            'status':   'success' | 'failed',
            'data':     <parsed JSON / raw text> | None,
        }
    """
    last_error: str = ""

    for attempt in range(max_retries):
        # Exponential backoff: wait before every retry (not before the first try)
        if attempt > 0:
            delay = 2 ** (attempt - 1)   # 1 s, 2 s, 4 s, …
            wmill.log(f"[{url}] attempt {attempt + 1}/{max_retries} – sleeping {delay}s after previous failure")
            await asyncio.sleep(delay)

        try:
            wmill.log(f"[{url}] attempt {attempt + 1}/{max_retries} – fetching …")
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "windmill-api-pipeline/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                raw = response.read().decode("utf-8")

            # Try to parse as JSON; fall back to raw text
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = raw

            wmill.log(f"[{url}] ✓ success on attempt {attempt + 1}")
            return {"endpoint": url, "status": "success", "data": data}

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last_error = str(exc)
            wmill.log(f"[{url}] ✗ attempt {attempt + 1} failed: {last_error}")

    # All retries exhausted
    wmill.log(f"[{url}] ✗ all {max_retries} attempts failed – marking as failed")
    return {"endpoint": url, "status": "failed", "data": None}


# ---------------------------------------------------------------------------
# Main workflow entry-point
# ---------------------------------------------------------------------------

async def main(endpoints: list, max_retries: int = 3) -> dict[str, Any]:
    """
    Fetch all *endpoints* in parallel (concurrency=3) with retry/self-healing,
    build a health report, persist it as JSON, and return it.
    """
    if not endpoints:
        report: dict[str, Any] = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
        }
        _write_report(report)
        return report

    wmill.log(
        f"Starting pipeline: {len(endpoints)} endpoint(s), "
        f"max_retries={max_retries}, concurrency=3"
    )

    # ------------------------------------------------------------------
    # Dispatch all fetch tasks in parallel, capped at concurrency=3
    # ------------------------------------------------------------------
    tasks = [fetch_with_retry(url, max_retries) for url in endpoints]
    results: list[dict[str, Any]] = await parallel(tasks, concurrency=3)

    # ------------------------------------------------------------------
    # Compute health report
    # ------------------------------------------------------------------
    total      = len(endpoints)
    successful = sum(1 for r in results if r.get("status") == "success")
    failed     = total - successful
    success_rate = successful / total if total > 0 else 0.0

    report = {
        "total":        total,
        "successful":   successful,
        "failed":       failed,
        "success_rate": success_rate,
    }

    wmill.log(
        f"Pipeline complete – total={total}, successful={successful}, "
        f"failed={failed}, success_rate={success_rate:.2%}"
    )

    # ------------------------------------------------------------------
    # Persist the report
    # ------------------------------------------------------------------
    _write_report(report)

    return report


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _write_report(report: dict[str, Any]) -> None:
    """Write *report* as pretty-printed JSON to the configured path."""
    report_path = "/home/user/windmill-project/pipeline_report.json"
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    wmill.log(f"Health report written to {report_path}")
