# Self-Healing API Data Pipeline

## Overview
This Windmill workflow fetches data from multiple API endpoints with automatic retry and self-healing behavior.

## Workflow File
- **Location**: `/home/user/windmill-project/f/workflows/api_pipeline.py`
- **Artifacts**: `/logs/artifacts/code/api_pipeline.py`

## Features

### 1. Parameters
- `endpoints: List[str]` - List of API endpoint URLs to fetch
- `max_retries: int = 3` - Maximum number of retry attempts per endpoint

### 2. Exponential Backoff Retry
- Attempts up to `max_retries` times for each endpoint
- Uses exponential backoff with delays: 2^attempt seconds (1s, 2s, 4s)
- Implements `await asyncio.sleep()` for delays within tasks

### 3. Parallel Processing
- Uses `wmill.parallel()` with `concurrency=3`
- Processes all endpoints concurrently with controlled parallelism

### 4. Error Handling
- Catches all HTTP and network errors
- Records failed endpoints with `{'endpoint': url, 'status': 'failed', 'data': None}`
- Continues processing other endpoints even if some fail

### 5. Health Report
Computes and returns a health report with:
- `total`: Total number of endpoints
- `successful`: Number of successful fetches
- `failed`: Number of failed fetches
- `success_rate`: Success rate as a float (0.0 to 1.0)

### 6. Output File
Writes health report to: `/home/user/windmill-project/pipeline_report.json`

## Implementation Details

### Dependencies
- `asyncio` - For async/await and sleep functionality
- `json` - For JSON serialization
- `urllib.request` - For HTTP requests (stdlib only)
- `urllib.error` - For error handling
- `typing` - For type hints
- `wmill` - Windmill SDK for parallel execution

### Key Functions

#### `fetch_endpoint(endpoint: str, max_retries: int = 3) -> Dict[str, Any]`
- Fetches data from a single API endpoint
- Implements exponential backoff retry logic
- Returns dict with endpoint URL, status, and data

#### `main(endpoints: List[str], max_retries: int = 3) -> Dict[str, Any]`
- Main workflow entry point
- Creates tasks for all endpoints
- Executes tasks in parallel with concurrency=3
- Computes and writes health report
- Returns health report dict

## Usage Example

```python
from f.workflows.api_pipeline import main

endpoints = [
    "https://api.example.com/data1",
    "https://api.example.com/data2",
    "https://api.example.com/data3"
]

result = await main(endpoints, max_retries=3)
# Returns: {'total': 3, 'successful': 3, 'failed': 0, 'success_rate': 1.0}
```

## Verification

All structure and logic checks have passed:
- ✓ Python syntax is valid
- ✓ All required imports present
- ✓ Function signatures correct
- ✓ Uses asyncio.sleep() for delays
- ✓ Uses parallel() with concurrency=3
- ✓ Uses urllib.request.urlopen()
- ✓ Writes JSON report to correct path
- ✓ Health report contains all required fields
- ✓ Implements exponential backoff (2 ** attempt)
- ✓ Has retry loop
- ✓ Returns success/failed status
- ✓ Counts successful results

## Testing
A verification script is available at `/logs/artifacts/verify_workflow.py` that validates the workflow structure and logic without executing network calls.