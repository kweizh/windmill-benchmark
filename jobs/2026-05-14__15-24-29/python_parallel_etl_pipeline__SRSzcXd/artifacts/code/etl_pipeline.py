import urllib.request
import json
from wmill import workflow, task, parallel

@task
async def extract(endpoint: str) -> dict:
    """
    Fetches JSON from a URL using urllib.request.urlopen with a 5-second timeout.
    """
    try:
        with urllib.request.urlopen(endpoint, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        return {'endpoint': endpoint, 'error': str(e), 'data': []}

@task
async def transform(record: dict) -> dict:
    """
    Transforms a record by adding metadata.
    """
    return {**record, 'transformed': True, 'source': record.get('endpoint', 'unknown')}

@task
async def load(records: list) -> dict:
    """
    Simulates loading records and returns status.
    """
    return {'loaded': len(records), 'status': 'success'}

@workflow
async def main(endpoints: list) -> dict:
    """
    Entry point for the ETL workflow.
    """
    # Step 1: Extract in parallel with concurrency 4
    raw_data = await parallel(endpoints, lambda ep: extract(ep), concurrency=4)
    
    # Step 2: Transform in parallel with concurrency 10
    transformed = await parallel(raw_data, lambda r: transform(r), concurrency=10)
    
    # Step 3: Load the final transformed data
    load_result = await load(transformed)
    
    return load_result
