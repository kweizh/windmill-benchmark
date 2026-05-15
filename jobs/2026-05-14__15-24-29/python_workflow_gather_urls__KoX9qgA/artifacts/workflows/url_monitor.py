from wmill import workflow, task
import asyncio
import urllib.request

@task
async def check_url(url: str) -> dict:
    """
    Checks the status of a URL using urllib.request.
    Returns a dict with url, status code, and ok boolean.
    """
    try:
        # Using a context manager for urlopen to ensure connection is closed
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            return {
                'url': url,
                'status': status,
                'ok': 200 <= status < 400
            }
    except Exception:
        # Return status 0 and ok False on any exception as per requirements
        return {
            'url': url,
            'status': 0,
            'ok': False
        }

@task
async def aggregate(results: list) -> dict:
    """
    Aggregates the results of multiple URL checks.
    """
    successful = sum(1 for r in results if r.get('ok'))
    failed = sum(1 for r in results if not r.get('ok'))
    return {
        'total': len(results),
        'successful': successful,
        'failed': failed
    }

@workflow
async def main(urls: list) -> dict:
    """
    Main workflow to monitor URLs in parallel.
    """
    # Execute check_url tasks in parallel using asyncio.gather
    results = await asyncio.gather(*[check_url(u) for u in urls])
    
    # Pass results to the aggregate task
    summary = await aggregate(results)
    
    return summary
