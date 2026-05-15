from wmill import workflow, task
import asyncio
import urllib.request


@task
async def check_url(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
        return {"url": url, "status": status, "ok": True}
    except Exception:
        return {"url": url, "status": 0, "ok": False}


@task
async def aggregate(results: list) -> dict:
    successful = sum(1 for result in results if result.get("ok"))
    failed = len(results) - successful
    return {"total": len(results), "successful": successful, "failed": failed}


@workflow
async def main(urls: list) -> dict:
    results = await asyncio.gather(*[check_url(url) for url in urls])
    summary = await aggregate(results)
    return summary
