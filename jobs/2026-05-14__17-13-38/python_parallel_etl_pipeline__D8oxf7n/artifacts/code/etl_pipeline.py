import json
import urllib.request
from wmill import workflow, task, parallel

@task
async def extract(endpoint: str) -> dict:
    try:
        req = urllib.request.Request(endpoint)
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {'endpoint': endpoint, 'error': str(e), 'data': []}

@task
async def transform(record: dict) -> dict:
    return {**record, 'transformed': True, 'source': record.get('endpoint', 'unknown')}

@task
async def load(records: list) -> dict:
    return {'loaded': len(records), 'status': 'success'}

@workflow
async def main(endpoints: list) -> dict:
    raw_data = await parallel(endpoints, lambda ep: extract(ep), concurrency=4)
    transformed = await parallel(raw_data, lambda r: transform(r), concurrency=10)
    return await load(transformed)
