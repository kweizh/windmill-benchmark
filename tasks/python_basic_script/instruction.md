# Create a Python Windmill Script

## Background

Windmill supports Python scripts alongside TypeScript. A Python Windmill script is a `.py` file containing a `main` function — the entry point Windmill calls when running the script. Like TypeScript scripts, each Python script is paired with a `.script.yaml` metadata file.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/hello.py`.
- The `main` function must accept one parameter: `name` of type `str`.
- The function must return the string `f"Hello, {name}!"`.
- Create the metadata file at `/home/user/windmill-project/f/scripts/hello.script.yaml` with:
  - `summary: "Say hello to a user"`
  - `language: python3`

## Implementation Guide

1. Navigate to the project directory:
   ```bash
   cd /home/user/windmill-project
   ```

2. Create the Python script `f/scripts/hello.py`:
   ```python
   def main(name: str) -> str:
       return f"Hello, {name}!"
   ```

3. Create the metadata file `f/scripts/hello.script.yaml`:
   ```yaml
   summary: "Say hello to a user"
   language: python3
   ```

## Constraints

- Project path: `/home/user/windmill-project`
- Script path: `/home/user/windmill-project/f/scripts/hello.py`
- Metadata path: `/home/user/windmill-project/f/scripts/hello.script.yaml`
- The function signature must be exactly: `main(name: str) -> str`
- The return value must be a formatted string: `f"Hello, {name}!"`

## Integrations

None.
