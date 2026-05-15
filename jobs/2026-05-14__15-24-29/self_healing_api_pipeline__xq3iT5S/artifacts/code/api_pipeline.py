import asyncio
import json
import urllib.request
import urllib.error
from wmill import task, parallel

@task
async def fetch_endpoint(url: str, max_retries: int):
    """
    Fetches data from a single endpoint with exponential backoff retry.
    """
    for attempt in range(max_retries):
        try:
            # Using urllib.request as per constraints
            # We use a timeout to avoid hanging indefinitely
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read().decode('utf-8')
                return {'endpoint': url, 'status': 'success', 'data': data}
        except Exception:
            if attempt < max_retries - 1:
                # Delays of 2^attempt seconds: 2^0=1s, 2^1=2s, 2^2=4s...
                delay = 2 ** attempt
                await asyncio.sleep(delay)
            else:
                # All retries failed, record it as failed
                return {'endpoint': url, 'status': 'failed', 'data': None}

async def main(endpoints: list, max_retries: int = 3):
    """
    Main workflow entry point.
    """
    # Process all endpoints in parallel with concurrency=3
    # fetch_endpoint is decorated with @task, so it returns a task object when called
    results = await parallel(
        [fetch_endpoint(url, max_retries) for url in endpoints],
        concurrency=3
    )
    
    # Compute health report
    total = len(endpoints)
    successful = sum(1 for r in results if r and r.get('status') == 'success')
    failed = total - successful
    success_rate = successful / total if total > 0 else 0.0
    
    report = {
        'total': total,
        'successful': successful,
        'failed': failed,
        'success_rate': success_rate
    }
    
    # Write health report to JSON file
    report_path = '/home/user/windmill-project/pipeline_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=4)
        
    return report
