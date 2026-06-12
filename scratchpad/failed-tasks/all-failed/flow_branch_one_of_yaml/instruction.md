# Windmill Declarative Flow: Branch One Router (YAML)

## Background
Windmill flows are stored as declarative OpenFlow YAML and can be deployed with the `wmill` CLI to the cloud-hosted instance at https://app.windmill.dev. Among the flow primitives, `branchone` runs **exactly one** branch out of many based on the first predicate that evaluates to `true`. Your goal is to author a small router flow whose YAML uses the documented `branchone` primitive to dispatch to one of two constant-returning branches based on the `route` input.

## Requirements
- Read the current `run-id` from the `ZEALT_RUN_ID` environment variable.
- Author an OpenFlow YAML file at `/home/user/myproject/flow.yaml` whose `value.modules` contains a single module whose `value.type` is `branchone`.
- The `branchone` module must define **two** branches with explicit predicate expressions:
  - The first branch runs when the flow input `route` equals the string `"a"`. Its inline script must return the exact string `"branch_a_route"`.
  - The second branch runs when the flow input `route` equals the string `"b"`. Its inline script must return the exact string `"branch_b_route"`.
- The flow must expose a JSON schema that accepts a required string input named `route`.
- Deploy the flow to the cloud workspace under the path `f/zealt/branch_one_${run-id}` (substituting the value of `run-id`).
- Append the deployed flow remote path to `/home/user/myproject/output.log` in the format `Flow path: f/zealt/branch_one_<run-id>` so the verifier can confirm deployment was attempted.

## Implementation Hints
- The Windmill CLI is preinstalled and pre-authenticated against the cloud instance — the workspace `evaluation-ws` is already bound, and the `WM_TOKEN`, `WM_WORKSPACE`, and `WM_BASE_URL` environment variables are available for API verification.
- Refer to the Windmill OpenFlow specification (`https://www.windmill.dev/docs/openflow`) and the Branches docs (`https://www.windmill.dev/docs/flows/flow_branches`) for the exact YAML shape of a `branchone` module, including the `branches` array (each with `expr`, optional `summary`, and `modules`) and the required `default` array.
- Inline scripts inside a flow module are expressed with `type: rawscript`, an empty `input_transforms` map (when no inputs are needed), a `language` field, and a `content` field containing the source code.
- Predicate expressions are evaluated as restricted JavaScript and have access to `flow_input.<field>`.
- Deploy using `wmill flow push <local_path> <remote_path>` and run with `wmill flow run <remote_path> -d '{"route":"a"}'`. The cloud API also exposes synchronous run endpoints under `/api/w/<workspace>/jobs/run_wait_result/f/<flow_path>` for end-to-end verification.
- Do **not** start a local Windmill instance; the task targets the cloud instance only.

## Acceptance Criteria
- Project path: /home/user/myproject
- Ensure the real flow deployment action is executed and the log artifact exists.
- Log file: /home/user/myproject/output.log
- The local file `/home/user/myproject/flow.yaml` must exist and be parseable as YAML.
- The flow YAML must contain a module whose `value.type` field equals the literal string `branchone` and whose `value.branches` array has length 2.
- The flow must be deployed to the cloud workspace `evaluation-ws` at the remote path `f/zealt/branch_one_${run-id}` where `run-id` is read from `ZEALT_RUN_ID`.
- Running the deployed flow with input `{"route": "a"}` must produce the exact string result `branch_a_route`.
- Running the deployed flow with input `{"route": "b"}` must produce the exact string result `branch_b_route`.
- The log file must contain a line matching `Flow path: f/zealt/branch_one_<run-id>`.

