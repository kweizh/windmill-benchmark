from wmill import workflow, task, parallel
import urllib.request
import json


@task
async def extract(endpoint: str) -> dict:
    """
    Extract JSON data from a given endpoint URL.
    Uses urllib.request.urlopen with a 5-second timeout.
    Returns parsed JSON dict or error dict on exception.
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
    Transform a record by adding metadata fields.
    Returns the record with 'transformed': True and 'source' field.
    """
    return {**record, 'transformed': True, 'source': record.get('endpoint', 'unknown')}


@task
async def load(records: list) -> dict:
    """
    Load the transformed records.
    Returns a dict with count of loaded records and success status.
    """
    return {'loaded': len(records), 'status': 'success'}


@workflow
async def main(endpoints: list) -> dict:
    """
    Main ETL workflow that runs extract, transform, and load in parallel.
    - Extract: concurrency=4
    - Transform: concurrency=10
    - Load: sequential
    """
    # Extract phase - fetch data from all endpoints concurrently
    raw_data = await parallel(endpoints, lambda ep: extract(ep), concurrency=4)
    
    # Transform phase - transform all records concurrently
    transformed = await parallel(raw_data, lambda r: transform(r), concurrency=10)
    
    # Load phase - load all transformed records
    load_result = await load(transformed)
    
    return load_result