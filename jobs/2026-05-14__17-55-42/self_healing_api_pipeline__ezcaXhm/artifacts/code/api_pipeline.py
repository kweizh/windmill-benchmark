import asyncio
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any


async def fetch_endpoint(endpoint: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Fetch data from a single API endpoint with exponential backoff retry.

    Args:
        endpoint: The URL to fetch data from
        max_retries: Maximum number of retry attempts

    Returns:
        Dict with endpoint URL, status, and data (or None if failed)
    """
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(endpoint, timeout=30) as response:
                data = response.read().decode('utf-8')
                return {
                    'endpoint': endpoint,
                    'status': 'success',
                    'data': data
                }
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, Exception) as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt seconds
                delay = 2 ** attempt
                await asyncio.sleep(delay)
            else:
                # All retries exhausted
                return {
                    'endpoint': endpoint,
                    'status': 'failed',
                    'data': None
                }


async def main(endpoints: List[str], max_retries: int = 3) -> Dict[str, Any]:
    """
    Main workflow that fetches data from multiple API endpoints in parallel.

    Args:
        endpoints: List of API endpoint URLs
        max_retries: Maximum number of retry attempts per endpoint

    Returns:
        Health report dictionary with statistics
    """
    from wmill import parallel

    # Create tasks for all endpoints
    tasks = []
    for endpoint in endpoints:
        task = fetch_endpoint(endpoint, max_retries)
        tasks.append(task)

    # Execute tasks in parallel with concurrency=3
    results = await parallel(*tasks, concurrency=3)

    # Count successful and failed endpoints
    successful = sum(1 for result in results if result['status'] == 'success')
    failed = len(results) - successful
    total = len(endpoints)

    # Compute health report
    health_report = {
        'total': total,
        'successful': successful,
        'failed': failed,
        'success_rate': successful / total if total > 0 else 0.0
    }

    # Write health report to JSON file
    report_path = '/home/user/windmill-project/pipeline_report.json'
    with open(report_path, 'w') as f:
        json.dump(health_report, f, indent=2)

    return health_report