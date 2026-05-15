import asyncio
import urllib.request

from wmill import task, workflow


@task
async def check_url(url: str) -> dict:
    """Fetch a URL and return its HTTP status code.

    Returns a dict with keys:
      - url: the original URL
      - status: HTTP status code, or 0 on error
      - ok: True when the request succeeded (status > 0)
    """
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return {"url": url, "status": response.status, "ok": True}
    except Exception:
        return {"url": url, "status": 0, "ok": False}


@task
async def aggregate(results: list) -> dict:
    """Summarise a list of check_url results.

    Returns a dict with keys:
      - total: total number of URLs checked
      - successful: number of URLs where ok == True
      - failed: number of URLs where ok == False
    """
    successful = sum(1 for r in results if r.get("ok") is True)
    failed = sum(1 for r in results if r.get("ok") is False)
    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
    }


@workflow
async def main(urls: list) -> dict:
    """Monitor a list of URLs in parallel and return a summary.

    Args:
        urls: List of URL strings to check.

    Returns:
        A summary dict produced by :func:`aggregate`.
    """
    results = await asyncio.gather(*[check_url(u) for u in urls])
    summary = await aggregate(list(results))
    return summary
