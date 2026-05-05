# Python Windmill Script — Nested Dictionary Transformer

## Background

Windmill Python scripts that process webhook payloads or API responses often receive deeply nested JSON structures. Flattening or restructuring these nested dicts is a common pre-processing step before passing data to downstream scripts.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/flatten_config.py`.
- The `main` function must have this signature:
  ```python
  def main(config: dict, prefix: str = "") -> dict:
  ```
- The function must flatten a nested dict into a single-level dict with dot-notation keys.
  - e.g., `{"a": {"b": 1, "c": {"d": 2}}}` → `{"a.b": 1, "a.c.d": 2}`
  - If `prefix` is provided, prepend it: `{"x": 1}` with `prefix="ns"` → `{"ns.x": 1}`
- Non-dict values are written as-is (string, int, float, bool, list).
- Create the metadata file at `/home/user/windmill-project/f/scripts/flatten_config.script.yaml` with:
  - `summary: "Flatten a nested dictionary into dot-notation keys"`
  - `language: python3`

## Constraints

- Project path: `/home/user/windmill-project`
- Key separator is `.` (dot)
- Lists are NOT recursed into — kept as-is

## Integrations

None.
