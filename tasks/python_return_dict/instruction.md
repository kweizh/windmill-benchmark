# Python Windmill Script Returning a Dictionary

## Background

Windmill scripts can return Python dictionaries which are serialized to JSON and passed to downstream flow steps. This pattern is common for scripts that compute and return multiple related values together.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/stats.py`.
- The `main` function must accept one parameter: `numbers` of type `list[float]`.
- The function must return a dict with exactly these keys:
  - `count`: the number of elements in `numbers` (int)
  - `total`: the sum of all elements (float)
  - `average`: `total / count`, or `0.0` if `numbers` is empty (float)
- Create the metadata file at `/home/user/windmill-project/f/scripts/stats.script.yaml` with:
  - `summary: "Compute basic statistics for a list of numbers"`
  - `language: python3`

## Implementation Guide

1. Create `f/scripts/stats.py`:
   ```python
   def main(numbers: list[float]) -> dict:
       count = len(numbers)
       total = sum(numbers)
       average = total / count if count > 0 else 0.0
       return {"count": count, "total": total, "average": average}
   ```
2. Create `f/scripts/stats.script.yaml`:
   ```yaml
   summary: "Compute basic statistics for a list of numbers"
   language: python3
   ```

## Constraints

- Project path: `/home/user/windmill-project`
- Script path: `/home/user/windmill-project/f/scripts/stats.py`
- Metadata path: `/home/user/windmill-project/f/scripts/stats.script.yaml`
- Return key names must be exactly `count`, `total`, `average`
- Handle empty list by returning `average: 0.0`

## Integrations

None.
