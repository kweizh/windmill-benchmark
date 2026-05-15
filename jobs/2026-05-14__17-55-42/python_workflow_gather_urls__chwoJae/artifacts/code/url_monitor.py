from wmill import workflow, task
import asyncio
import urllib.request


@task
async def check_url(url: str) -> dict:
    """
    Check a single URL and return its status.
    
    Args:
        url: The URL to check
        
    Returns:
        dict: {'url': url, 'status': int, 'ok': bool}
    """
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.status
            return {'url': url, 'status': status, 'ok': status < 400}
    except Exception:
        return {'url': url, 'status': 0, 'ok': False}


@task
async def aggregate(results: list) -> dict:
    """
    Aggregate the results from URL checks.
    
    Args:
        results: List of check_url results
        
    Returns:
        dict: {'total': int, 'successful': int, 'failed': int}
    """
    successful = sum(1 for r in results if r.get('ok', False))
    failed = len(results) - successful
    return {'total': len(results), 'successful': successful, 'failed': failed}


@workflow
async def main(urls: list) -> dict:
    """
    Main workflow to check multiple URLs in parallel.
    
    Args:
        urls: List of URLs to check
        
    Returns:
        dict: Summary of URL check results
    """
    results = await asyncio.gather(*[check_url(u) for u in urls])
    summary = await aggregate(results)
    return summary