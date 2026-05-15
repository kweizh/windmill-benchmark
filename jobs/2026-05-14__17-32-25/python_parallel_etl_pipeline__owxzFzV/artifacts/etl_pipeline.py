import json
import urllib.request

from wmill import parallel, task, workflow


@task
async def extract(endpoint: str) -> dict:
    """Fetch JSON from the given URL endpoint.

    Returns the parsed JSON dict on success, or an error dict on failure.
    """
    try:
        with urllib.request.urlopen(endpoint, timeout=5) as response:
            raw = response.read()
            data = json.loads(raw)
            return data
    except Exception as e:
        return {"endpoint": endpoint, "error": str(e), "data": []}


@task
async def transform(record: dict) -> dict:
    """Enrich a single record with transformation metadata."""
    return {
        **record,
        "transformed": True,
        "source": record.get("endpoint", "unknown"),
    }


@task
async def load(records: list) -> dict:
    """Load the transformed records and report how many were persisted."""
    return {"loaded": len(records), "status": "success"}


@workflow
async def main(endpoints: list) -> dict:
    """Orchestrate the full ETL pipeline across all provided endpoints.

    Steps:
        1. Extract: fan-out across all endpoints (concurrency=4).
        2. Transform: enrich every raw record (concurrency=10).
        3. Load: persist the transformed records as a single batch.
    """
    raw_data = await parallel(
        endpoints,
        lambda ep: extract(ep),
        concurrency=4,
    )

    transformed = await parallel(
        raw_data,
        lambda r: transform(r),
        concurrency=10,
    )

    result = await load(transformed)
    return result
