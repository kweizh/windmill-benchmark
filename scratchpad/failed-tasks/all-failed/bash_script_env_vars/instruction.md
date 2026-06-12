# Windmill Bash Script with Runtime Env Vars

## Background
Windmill is a developer platform and workflow engine that supports authoring scripts in multiple languages, including Bash. At runtime, every job receives a set of injected environment variables prefixed with `WM_`, such as `WM_USERNAME` (the username of the caller). Your goal is to author and deploy a Bash script to the cloud-hosted Windmill workspace that consumes a positional argument and surfaces the caller's `WM_USERNAME` together with the input as a single structured JSON line.

## Requirements
- Use the `wmill` CLI to author and deploy a Bash script to the cloud-hosted Windmill workspace.
- The script must declare a single positional `string` argument (so that Windmill renders it as a typed parameter) and read the `WM_USERNAME` environment variable at runtime.
- The script must print a single JSON object as the LAST line of stdout containing exactly two keys: `"input"` (set to the argument value) and `"user"` (set to the value of `WM_USERNAME`).
- The script must be deployed to the cloud workspace under a `run-id`-scoped folder so concurrent trials do not collide.
- A log file must capture the JSON returned by Windmill when the script is executed with the input string `hello`.

## Implementation Hints
- The `wmill` CLI (`windmill-cli` npm package) is already installed and authenticated against the cloud workspace `app.windmill.dev`. Use `wmill workspace list` to confirm the active workspace before deploying.
- For Bash scripts, Windmill infers parameters from positional `$1`, `$2`, ... usage. Scripts live as a pair of files on disk: a `.sh` source file and a `.script.yaml` metadata file under an `f/<folder>/` path.
- The runtime injects `WM_USERNAME`, `WM_EMAIL`, `WM_WORKSPACE`, etc. into the script environment. Refer to the Windmill docs for the complete list.
- Deploy local changes to the cloud with `wmill sync push`. Execute the deployed script with `wmill script run` and capture stdout to the log file.
- Read the `run-id` from the `ZEALT_RUN_ID` environment variable and use it to build the script path (for example, `f/zealt_${run-id}/echo_user`).

## Acceptance Criteria
- Project path: /home/user/myproject
- Ensure the script is actually deployed to the cloud Windmill workspace and the artifacts below exist.
- Read the `run-id` from the `ZEALT_RUN_ID` environment variable.
- Bash script source file: /home/user/myproject/f/zealt_${run-id}/echo_user.sh
- Bash script metadata file: /home/user/myproject/f/zealt_${run-id}/echo_user.script.yaml
- Log file: /home/user/myproject/output.log
- The log file must contain a JSON object whose `input` field equals `"hello"` and whose `user` field is a non-empty string (the value of `WM_USERNAME` for the executing identity).
- The same JSON object must be the LAST line of stdout produced by the deployed Bash script when executed with the argument `hello`.

