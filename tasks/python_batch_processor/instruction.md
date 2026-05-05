# Python Windmill Script — Batch Processor with Progress Tracking

## Background

Windmill is often used to orchestrate bulk data processing. A common pattern is a script that receives a large list of items, processes them in fixed-size batches, and returns both the results and a processing summary. This makes it easy to detect partial failures in a flow.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/batch_process.py`.
- The `main` function must have this signature:
  ```python
  def main(items: list[str], batch_size: int = 10, transform: str = "upper") -> dict:
  ```
- `transform` options:
  - `"upper"`: convert each string to uppercase
  - `"lower"`: convert to lowercase
  - `"reverse"`: reverse each string
  - Any other value: raise `ValueError(f"Unknown transform: '{transform}'. Choose 'upper', 'lower', or 'reverse'")`
- Process `items` in batches of `batch_size`.
- Return:
  ```python
  {
    "total": len(items),
    "batch_count": math.ceil(len(items) / batch_size) if items else 0,
    "batch_size": batch_size,
    "transform": transform,
    "results": [transformed_item, ...],  # all items transformed, in order
    "batches": [{"batch_index": i, "items": batch_results}, ...]
  }
  ```
- Create the metadata file at `/home/user/windmill-project/f/scripts/batch_process.script.yaml` with:
  - `summary: "Process a list of strings in configurable batches"`
  - `language: python3`

## Constraints

- Project path: `/home/user/windmill-project`
- Use `import math` for `math.ceil`
- `batches` list must reflect actual batching (each batch dict has `batch_index` and `items`)
- `results` is a flat list of all transformed items

## Integrations

None.
