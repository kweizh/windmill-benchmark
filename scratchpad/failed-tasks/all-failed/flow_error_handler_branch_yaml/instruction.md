# Windmill Flow Error Handler in YAML

## Background
Windmill flows are declarative DAGs that can be authored as `.flow.yaml` files and deployed to a Windmill instance. A flow can declare a documented error handler that runs when one of its modules fails.

## Requirements
Author a Windmill flow as YAML on disk and deploy it to the cloud workspace. The flow must contain a script step that throws when its input demands it, and an error handler that intercepts the failure and returns a custom JSON payload.

## Implementation Hints
- Read the current `run-id` from the `ZEALT_RUN_ID` environment variable and append it to the flow path so concurrent trials do not collide.
- The Windmill CLI (`wmill`) is preconfigured to talk to the cloud workspace; environment variables for the base URL, workspace, and token are already provided.
- A flow's error handler is documented in the OpenFlow specification.

## Acceptance Criteria
- Project path: /home/user/myproject
- Ensure the flow is actually deployed to the cloud workspace; the verifier will fetch and run the deployed flow remotely.
- The flow must be deployed at the remote path `f/zealt/err_handler_${run-id}` where `run-id` is read from `ZEALT_RUN_ID`.
- The local YAML file `/home/user/myproject/f/zealt/err_handler_${run-id}.flow/flow.yaml` must use the documented error-handler keyword from the OpenFlow spec.
- The flow accepts a single input field `should_fail` (boolean). When `should_fail` is `true`, the inner script must raise/throw an error.
- When the inner script fails, the flow's overall result (i.e. the value returned by the error handler) must be a JSON object of the form `{ "handled": true, "reason": "<non-empty string>" }`. The `reason` value should be derived from the upstream error message.

