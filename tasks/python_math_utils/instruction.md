# Python Windmill Script — Statistical Math Utilities

## Background

Windmill scripts are frequently embedded in data pipelines to perform numerical analysis on values produced by upstream steps (e.g., sensor readings, financial metrics). This task creates a Python script that computes common statistical descriptors.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/describe.py`.
- The `main` function must have this signature:
  ```python
  def main(values: list[float]) -> dict:
  ```
- If `values` is empty, raise `ValueError("Cannot describe an empty list")`.
- Otherwise return:
  ```python
  {
    "count": int,
    "min": float,
    "max": float,
    "mean": float,            # sum / count
    "median": float,          # middle value (or average of two middles)
    "range": float            # max - min
  }
  ```
  Compute `median` without using `statistics` module — sort the list and compute manually.
- Create the metadata file at `/home/user/windmill-project/f/scripts/describe.script.yaml` with:
  - `summary: "Compute descriptive statistics for a list of numbers"`
  - `language: python3`

## Implementation Guide

```python
def main(values: list[float]) -> dict:
    if not values:
        raise ValueError("Cannot describe an empty list")
    sorted_v = sorted(values)
    n = len(sorted_v)
    mid = n // 2
    median = sorted_v[mid] if n % 2 else (sorted_v[mid - 1] + sorted_v[mid]) / 2
    return {
        "count": n,
        "min": sorted_v[0],
        "max": sorted_v[-1],
        "mean": sum(sorted_v) / n,
        "median": median,
        "range": sorted_v[-1] - sorted_v[0],
    }
```

## Constraints

- Project path: `/home/user/windmill-project`
- No `import statistics` — compute manually
- Return keys must be: `count`, `min`, `max`, `mean`, `median`, `range`

## Integrations

None.
