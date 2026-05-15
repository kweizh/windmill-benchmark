from __future__ import annotations

import json
import urllib.request
from typing import Any

from wmill import parallel, task, workflow


@task
async def extract(endpoint: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(endpoint, timeout=5) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)
    except Exception as exc:
        return {"endpoint": endpoint, "error": str(exc), "data": []}


@task
async def transform(record: dict[str, Any]) -> dict[str, Any]:
    return {
        **record,
        "transformed": True,
        "source": record.get("endpoint", "unknown"),
    }


@task
async def load(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {"loaded": len(records), "status": "success"}


@workflow
async def main(endpoints: list[str]) -> dict[str, Any]:
    raw_data = await parallel(endpoints, lambda ep: extract(ep), concurrency=4)
    transformed = await parallel(raw_data, lambda record: transform(record), concurrency=10)
    return await load(transformed)
