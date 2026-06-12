# Declarative Windmill Flow with Input Transforms

## Background
Windmill supports defining flows declaratively in YAML following the OpenFlow schema. Each module's parameters are populated via an `input_transforms` map that can wire a static value, a flow input, or a JavaScript expression referencing a previous step's result (e.g. `results.<step_id>`). In this task you will author a two-step linear flow whose second step consumes the first step's output, deploy it to the cloud-hosted Windmill instance, and execute it.

## Requirements
- Author a flow YAML file describing a linear pipeline with TWO sequential `rawscript` modules.
- The first module must double its numeric input (return `x * 2`).
- The second module must increment its numeric input by 1 (return `value + 1`).
- The second module must receive its numeric parameter from the first module's result through an `input_transforms` entry of type `javascript` whose `expr` references the first step by its module id (i.e. `results.<step_1_id>`).
- The flow's top-level input schema must declare a single numeric field `x`.
- Deploy the flow to the cloud-hosted Windmill workspace using the `wmill` CLI.
- Execute the deployed flow with input `{"x": 4}` and capture the final result.

## Implementation Hints
- The Windmill cloud instance is reachable at `https://app.windmill.dev`. Authentication uses the bearer token in the `WMILL_TOKEN` environment variable; the workspace id is in `WMILL_WORKSPACE`. **Never start a local Windmill instance.**
- Configure the `wmill` CLI workspace before pushing. The `wmill workspace add` command accepts `--token` and a base URL.
- The OpenFlow YAML structure has a top-level `summary`, a `value.modules` list, and a top-level JSON Schema in `schema`. Each module has an `id`, a `value` block (`type: rawscript`) containing `content`, `language`, and `input_transforms`.
- For inline scripts, valid `language` values include `bun` (TypeScript) and `python3`. Pick whichever you are comfortable with; the verifier only checks the final numeric result.
- Use `wmill flow push <local_file> <remote_path>` to deploy and `wmill flow run <remote_path> -d '<json>'` to execute. The CLI prints the final job result to stdout.
- Read `run-id` from the `ZEALT_RUN_ID` environment variable and append it to the remote flow path so concurrent runs do not collide.

## Acceptance Criteria
- Project path: `/home/user/wmill-project`
- Ensure the deployment and run actions are actually executed against `https://app.windmill.dev` and that the listed artifacts exist on disk afterwards.
- Local flow file: `/home/user/wmill-project/two_step_flow.flow/flow.yaml`
  - Contains a top-level `summary` string and `value.modules` list with exactly two modules.
  - Each module has a unique `id` and a `value` block of `type: rawscript`.
  - The second module's `input_transforms` contains an entry whose `type` is `javascript` and whose `expr` references the first module's id via the `results.<first_module_id>` pattern.
  - The flow's top-level `schema` declares a property named `x`.
- The flow must be deployed to the remote path `f/zealt/two_step_flow_${run-id}` on the workspace identified by `WMILL_WORKSPACE`, where `run-id` is read from `ZEALT_RUN_ID`.
- Log file: `/home/user/wmill-project/output.log`. It must contain the following two lines:
  - `Flow path: f/zealt/two_step_flow_<run-id>`
  - `Final result: 9`

