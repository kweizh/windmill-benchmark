# Windmill Python Execution Counter via `wmill.get_state` / `wmill.set_state`

## Background
Windmill is a self-hostable workflow engine that runs scripts authored in many languages on a managed worker pool. Scripts can persist values across distinct executions of the same script using the workspace-level **State** primitive, which is exposed through the Python SDK (`wmill`) as `wmill.get_state()` and `wmill.set_state(value)`.

In this task, you will author a Python Windmill script that uses State to count how many times it has been executed against the **cloud-hosted Windmill instance** at `https://app.windmill.dev`, then deploy it to the configured workspace using the `wmill` CLI. The verifier will exercise the deployed script three times and assert that the persisted counter reaches `3`.

## Requirements
- The project root is `/home/user/myproject`. Treat that directory as a Windmill local workspace folder.
- Author the script as a file pair on disk:
  - `f/eval/exec_counter.py` — Python script entrypoint.
  - `f/eval/exec_counter.script.yaml` — Windmill script metadata declaring the `python3` runtime (no input arguments).
- The Python script MUST:
  1. `import wmill`.
  2. Define `def main():` (no arguments).
  3. On each invocation, read the current state via `wmill.get_state()`; if it is `None`, treat it as `{"runs": 0}`.
  4. Compute a new state by incrementing the `runs` field by one.
  5. Persist the new state via `wmill.set_state(new_state)`.
  6. Return the new state dict as the script result.
- Deploy the script to the cloud workspace (the credentials are provided through environment variables) so that `wmill script run f/eval/exec_counter` works against it.

## Implementation Hints
- Install the CLI with `npm install -g windmill-cli` (Node >= 20 is preinstalled in the environment).
- Authenticate non-interactively against `https://app.windmill.dev` using the `WINDMILL_TOKEN` and `WINDMILL_WORKSPACE` environment variables. The CLI accepts `wmill workspace add <name> <workspace_id> <remote> --token <token>` for headless setup.
- Use `wmill script push <file>` or `wmill sync push --yes` from inside `/home/user/myproject` to deploy the script. The Windmill folder `f/eval/` must exist on the workspace; create it if necessary (a minimal `f/eval/folder.meta.yaml` or pushing via `sync push` will do).
- The `.script.yaml` schema should declare `language: python3` plus an empty `schema.properties` since `main()` takes no arguments.
- Reference the Python SDK State docs: https://www.windmill.dev/docs/core_concepts/resources_and_types#states .
- Do **not** spin up any local Windmill instance — only the cloud version at `https://app.windmill.dev` is used.

## Acceptance Criteria
- Project path: /home/user/myproject
- File `/home/user/myproject/f/eval/exec_counter.py` exists, imports `wmill`, and contains the literal substrings `get_state(` and `set_state(` in its body.
- File `/home/user/myproject/f/eval/exec_counter.script.yaml` exists and declares `python3` as the script runtime.
- The script must NOT hard-code the value `3` anywhere in its source. The counter value must be produced through `wmill.get_state` / `wmill.set_state` rather than literally written.
- The script is deployed to the cloud workspace identified by the `WINDMILL_WORKSPACE` env var on `https://app.windmill.dev` at path `f/eval/exec_counter`.
- After three sequential invocations of `wmill script run f/eval/exec_counter` (each exiting with code `0`), the JSON result printed by the third invocation must include `"runs": 3`.

