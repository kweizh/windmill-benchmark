# Python Windmill Script — JSON Log Processor

## Background

A common Windmill pattern is receiving a JSON string payload from a webhook or HTTP trigger and transforming it into a structured dict for downstream steps. This task involves parsing a JSON string, extracting fields, and returning a clean summary object.

## Requirements

- Create a Python script at `/home/user/windmill-project/f/scripts/parse_event.py`.
- The `main` function must have this signature:
  ```python
  def main(event_json: str) -> dict:
  ```
- `event_json` is a JSON string with this shape:
  ```json
  {"event": "user.signup", "user_id": 42, "metadata": {"plan": "pro", "source": "web"}}
  ```
- The function must:
  1. Parse the JSON string.
  2. Return a dict:
     ```python
     {
       "event": event,
       "user_id": user_id,
       "plan": metadata.get("plan", "free"),
       "source": metadata.get("source", "unknown"),
       "summary": f"{event} by user #{user_id} via {source} on {plan} plan"
     }
     ```
  3. If the JSON is invalid, raise `ValueError("Invalid JSON payload")`.
- Create the metadata file at `/home/user/windmill-project/f/scripts/parse_event.script.yaml` with:
  - `summary: "Parse and summarize a JSON event payload"`
  - `language: python3`

## Constraints

- Project path: `/home/user/windmill-project`
- Use `json.loads` (stdlib only — no third-party dependencies)
- Return keys must be: `event`, `user_id`, `plan`, `source`, `summary`

## Integrations

None.
