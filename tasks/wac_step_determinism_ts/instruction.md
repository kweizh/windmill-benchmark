# Windmill Workflows-as-Code: Deterministic Timestamp Step (TypeScript)

## Background
Windmill's Workflows-as-Code (WAC) runtime uses a checkpoint/replay execution model. Any non-deterministic call placed directly inside the workflow body (such as `new Date().toISOString()`, `Date.now()`, `Math.random()`, or `fetch()`) is unsafe because it will return different values whenever the workflow replays from a checkpoint. The official mitigation is to wrap such calls inside `await step("<key>", () => ...)` so the result is persisted on the first execution and reused on subsequent replays.

Your task is to author, deploy, and run a TypeScript WAC flow on the cloud Windmill instance (https://app.windmill.dev) that captures a timestamp via a `step("init_time", ...)` checkpoint and returns both the captured timestamp and a downstream value derived from it.

## Requirements
- Author a Workflows-as-Code TypeScript script that:
  - Exports a `main` workflow created with `workflow(...)` from `windmill-client`.
  - Calls `step("init_time", () => new Date().toISOString())` to capture the current ISO-8601 timestamp.
  - Computes a downstream value that **depends on the captured timestamp** (for example, the `YYYY-MM-DD` date portion of the captured timestamp).
  - Returns a JSON object containing the captured timestamp and the downstream derived value.
  - **Does NOT** contain any unwrapped `Date.now()`, `new Date(...)`, `Math.random()`, or `fetch(...)` calls directly inside the workflow body; any non-deterministic operation must be wrapped inside a `step(...)` callback.
- Deploy the script to the cloud Windmill workspace using the `wmill` CLI.
- Run the deployed flow once via the Windmill HTTP API (or `wmill` CLI) and capture both the resulting job UUID and the JSON result.
- Save the run information to a log file for verification.

## Implementation Hints
- The `wmill` CLI is preinstalled and a workspace named `evaluation-ws` is already configured against https://app.windmill.dev with the API token from `WMILL_TOKEN`.
- Read the current `run-id` from the `ZEALT_RUN_ID` environment variable and append it to any folder/path you create so concurrent runs do not collide. Build the script path as `f/zealt_${run-id}/wac_step_determinism`.
- A WAC TypeScript script is just a `.ts` file accompanied by a `<name>.script.yaml` metadata file. After writing both files locally, deploy them with `wmill script push <path>` or `wmill sync push --yes`.
- To trigger an execution, use the synchronous run endpoint (e.g. `POST /api/w/<workspace>/jobs/run_wait_result/p/<path>`) or `wmill script run <path>`. Authenticate using the bearer token in `WMILL_TOKEN`.
- Persist non-deterministic calls inside `await step("<key>", () => ...)` blocks; the orchestration body itself must stay deterministic.

## Acceptance Criteria
- Project path: /home/user/myproject
- Ensure the script is actually deployed to the cloud Windmill instance and executed; the artifacts below must exist.
- Log file: /home/user/myproject/output.log
- WAC TypeScript source file: /home/user/myproject/f/zealt_${ZEALT_RUN_ID}/wac_step_determinism.ts
- Script metadata file: /home/user/myproject/f/zealt_${ZEALT_RUN_ID}/wac_step_determinism.script.yaml
- The deployed script path on Windmill must be: `f/zealt_${ZEALT_RUN_ID}/wac_step_determinism`.
- The TypeScript source must import `step` and `workflow` from `windmill-client`, declare a single workflow via `workflow(...)`, and use a literal `step("init_time", ...)` checkpoint to acquire the timestamp.
- The workflow body must NOT contain any unwrapped non-deterministic call (`Date.now`, `new Date`, `Math.random`, `fetch`) outside of a `step(...)` callback.
- Running the deployed flow must return a JSON object with:
  - A field whose value is the captured ISO-8601 timestamp returned by the `init_time` step.
  - A second field whose value is a string of length 10 in `YYYY-MM-DD` format, equal to the first 10 characters of that captured timestamp (the downstream derived value).
- The log file must contain two lines:
  - `Job UUID: <job_uuid>`
  - `Result: <json>` where `<json>` is the JSON result returned by the run.

