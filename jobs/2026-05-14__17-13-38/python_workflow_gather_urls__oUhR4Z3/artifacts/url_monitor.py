import asyncio
import urllib.request
from wmill import task, workflow

@task
async def check_url(url: str) -> dict:
    try:
        response = urllib.request.urlopen(url, timeout=5)
        return {'url': url, 'status': response.getcode(), 'ok': True}
    except Exception:
        return {'url': url, 'status': 0, 'ok': False}

@task
async def aggregate(results: list) -> dict:
    successful = sum(1 for r in results if r.get('ok'))
    failed = len(results) - successful
    return {'total': len(results), 'successful': successful, 'failed': failed}

@workflow
async def main(urls: list) -> dict:
    results = await asyncio.gather(*[check_url(u) for u in urls])
    summary = await aggregate(results)
    return summary
