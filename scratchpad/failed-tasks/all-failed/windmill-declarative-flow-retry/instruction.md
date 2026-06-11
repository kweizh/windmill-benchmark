# Windmill Declarative Flow with Exponential Retry

## Background
Windmill is an open-source workflow engine that lets you author scripts and flows as declarative, version-controlled assets on disk and synchronize them to a Windmill workspace using the `wmill` CLI. Beyond scripts, Windmill exposes the **OpenFlow** spec, where a flow is described in `flow.yaml` as a sequence of modules with `input_transforms`, optional `retry` policies, and other control-flow features.

Your goal is to author a two-step OpenFlow pipeline that exercises Windmill's per-module **exponential retry** policy against the cloud Windmill instance at `https://app.windmill.dev`.

## Requirements
- Project path: `/home/user/windmill-project`
- Read `ZEALT_RUN_ID` from the environment and derive a workspace-safe folder name:
  - `SAFE_ID` = `ZEALT_RUN_ID` with every `-` character replaced by `_` (e.g. `zr-abc123` becomes `zr_abc123`).
  - Use the Windmill folder path `f/eval_${SAFE_ID}` for ALL assets created by this task. This prevents collisions across concurrent runs.
- Author a Python script at `f/eval_${SAFE_ID}/flaky_step` that:
  - Accepts a single string parameter `attempt_marker_path` (the Windmill variable path that stores the attempt counter).
  - Reads the current integer value from that Windmill variable, increments it by 1, and writes it back using `wmill.get_variable` / `wmill.set_variable`.
  - Raises a `RuntimeError` on every invocation where the new counter value is less than 3.
  - On the third invocation (when the counter reaches 3), returns the dict `{"ok": True, "attempt": 3}`.
- Author a Python script at `f/eval_${SAFE_ID}/finalize` that:
  - Accepts a single dict parameter `previous`.
  - Returns the dict `{"final": True, "previous_attempt": previous["attempt"]}`.
- Author a declarative Windmill flow at `f/eval_${SAFE_ID}/retry_pipeline` using the OpenFlow YAML schema with TWO `PathScript` modules:
  1. Module id `flaky` references the `f/eval_${SAFE_ID}/flaky_step` script. Its `input_transforms` must pass the literal string `f/eval_${SAFE_ID}/flaky_counter` as `attempt_marker_path`. The module must declare an **exponential** retry policy with EXACTLY `attempts: 4`, `multiplier: 2`, and `seconds: 1`.
  2. Module id `finalize` references the `f/eval_${SAFE_ID}/finalize` script. Its `input_transforms.previous` must be a JavaScript transform that references the output of the `flaky` module (so that the flow result reflects the value returned after the successful attempt).
- Pre-create the Windmill variable `f/eval_${SAFE_ID}/flaky_counter` with the string value `"0"` so the very first run starts from a known state.
- Deploy all assets (folder, scripts, flow, and variable) to the cloud workspace using `wmill sync push --yes` (configure `wmill.yaml` so that variables are included in the push).
- Trigger the flow once via the `wmill flow run` CLI and write the JSON result to a log file.

## Implementation Hints
- Authenticate against the cloud with `wmill workspace add` (or set `--token` / `--workspace` / `--base-url` per command) before running `wmill sync push`. The credentials live in the `WINDMILL_TOKEN` and `WINDMILL_WORKSPACE` environment variables; the base URL is `https://app.windmill.dev`.
- For Python scripts on disk, Windmill expects a `<name>.py` file paired with a `<name>.script.yaml` metadata file inside the script's folder.
- For declarative flows, place the `flow.yaml` file inside a folder named after the flow (the CLI supports both `<name>.flow/flow.yaml` and `<name>__flow/flow.yaml` layouts — choose one and make sure it is picked up by `wmill sync push`). Reference `https://www.windmill.dev/docs/openflow` and `https://www.windmill.dev/docs/advanced/cli/flow` for the exact schema.
- The OpenFlow `Retry` object supports an `exponential` block with `attempts`, `multiplier`, and `seconds` fields (delay formula: `multiplier * seconds ^ attempt`).
- Input transforms reference previous module outputs through the restricted JavaScript context: previous step results are exposed under `results.<module_id>` (e.g. `results.flaky`).
- The variable can be pre-created either with `wmill variable push` or by including a `flaky_counter.variable.yaml` file in the synced folder (set `skipVariables: false` in `wmill.yaml`).
- Trigger the flow via `wmill flow run f/eval_${SAFE_ID}/retry_pipeline -d '{}' --silent` and tee the JSON output into the log file.

## Acceptance Criteria
- Project path: `/home/user/windmill-project`
- Ensure the real deployment and flow execution are performed against `https://app.windmill.dev`; do not mock any Windmill API.
- Log file: `/home/user/windmill-project/output.log`
- The Python scripts and the declarative flow YAML must exist on disk under `/home/user/windmill-project` at the documented Windmill paths derived from `ZEALT_RUN_ID`.
- The flow YAML must declare, for the first module, an `exponential` retry policy with the exact fields `attempts: 4`, `multiplier: 2`, `seconds: 1`.
- The flow YAML must reference the output of the first module from the second module's `input_transforms.previous` using a JavaScript transform whose expression contains `results.flaky`.
- `wmill sync push --yes` must succeed and deploy the scripts, flow, and variable to the cloud workspace.
- After triggering the flow, the log file must contain the literal line:
  `Flow result: {"final": true, "previous_attempt": 3}`
- After execution, the Windmill variable `f/eval_${SAFE_ID}/flaky_counter` (as returned by the `wmill variable get` CLI) must equal the string `"3"`, confirming exactly three attempts ran.

