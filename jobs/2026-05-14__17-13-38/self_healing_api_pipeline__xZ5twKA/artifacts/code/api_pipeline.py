import wmill
import asyncio
import urllib.request
import json

@wmill.task
async def fetch_endpoint(item: dict):
    url = item.get("url")
    max_retries = item.get("max_retries", 3)
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode('utf-8')
            return {'endpoint': url, 'status': 'success', 'data': data}
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    return {'endpoint': url, 'status': 'failed', 'data': None}

async def main(endpoints: list, max_retries: int = 3):
    items = [{"url": url, "max_retries": max_retries} for url in endpoints]
    
    results = await wmill.parallel(items, fetch_endpoint, concurrency=3)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    total = len(endpoints)
    
    report = {
        'total': total,
        'successful': successful,
        'failed': failed,
        'success_rate': successful / total if total > 0 else 0
    }
    
    with open('/home/user/windmill-project/pipeline_report.json', 'w') as f:
        json.dump(report, f)
        
    return report
