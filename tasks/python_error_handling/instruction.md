# Python Windmill Script with Input Validation

## Background

In Windmill, when a script raises a Python exception, the step fails and the error is surfaced in the UI or routed to an error handler in a flow. Writing scripts that validate inputs and raise informative exceptions makes debugging and flow error-handling much easier.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/parse_age.py`.
- The `main` function must have this signature:
  ```python
  def main(age_str: str) -> dict:
  ```
- Behaviour:
  - Convert `age_str` to an integer.
  - If the value is not a valid integer, raise `ValueError(f"Invalid age: '{age_str}' is not an integer")`
  - If the integer is less than 0 or greater than 150, raise `ValueError(f"Age {age} is out of valid range (0–150)")`
  - Otherwise return `{"age": age, "category": category}` where category is:
    - `"minor"` if age < 18
    - `"adult"` if 18 <= age < 65
    - `"senior"` if age >= 65
- Create the metadata file at `/home/user/windmill-project/f/scripts/parse_age.script.yaml` with:
  - `summary: "Parse and categorize an age string"`
  - `language: python3`

## Constraints

- Project path: `/home/user/windmill-project`
- Raise `ValueError` (not a generic Exception) for invalid inputs
- Category strings must be exactly: `"minor"`, `"adult"`, `"senior"`

## Integrations

None.
