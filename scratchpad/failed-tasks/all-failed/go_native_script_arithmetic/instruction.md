# Go Native Windmill Script: Arithmetic + Echo

## Background
Windmill supports Go as a first-class scripting language. You will author a Go-native script, generate its metadata, deploy it to the Windmill cloud workspace using the `wmill` CLI, and execute it remotely. The script performs a tiny arithmetic computation and echoes a string argument back to the caller as a structured JSON object.

## Requirements
- Author a Go script that exposes a `main` function accepting two arguments:
  - `threshold` (Go `int`)
  - `name` (Go `string`)
- The function must return a value that serializes to a JSON object containing exactly two keys: `computed` (equal to `threshold * 2`) and `target` (equal to `name`).
- The script return type must follow Windmill's Go contract: `(<JSON-serializable type>, error)`.
- The script package must follow Windmill's required Go package naming.
- Generate the corresponding `.script.yaml` metadata file for the script.
- Deploy the script to the Windmill cloud workspace at the path described in Acceptance Criteria using the `wmill` CLI.
- Execute the deployed script remotely against the cloud workspace with `threshold = 5` and `name = "x"` and record the resulting JSON output in the log file.

## Implementation Hints
- Read the `ZEALT_RUN_ID` environment variable and use it to disambiguate the deployed script path so concurrent trials never clash.
- The Windmill CLI (`wmill`) is preinstalled and a workspace named `evaluation-ws` is preconfigured against `https://app.windmill.dev` using the provided API token.
- Use `wmill init` (if needed) to bootstrap a workspace folder and `wmill script generate-metadata` to derive the `.script.yaml` from your Go source.
- Use `wmill sync push --yes` to deploy local assets to the cloud workspace.
- Use `wmill script run <path> --data '<json>'` to execute the deployed script remotely. Pipe or redirect the output into the log file.
- A Go struct with `json:"computed"` and `json:"target"` tags is the most direct way to produce the required serialized shape.
- NEVER attempt to start a local Windmill instance. Always use the cloud workspace.

## Acceptance Criteria
- Project path: /home/user/myproject
- The current `run-id` MUST be read from the `ZEALT_RUN_ID` environment variable.
- The Go script source file MUST exist at: `/home/user/myproject/f/zealt/go_arith_${run-id}.go`
- The script metadata file MUST exist at: `/home/user/myproject/f/zealt/go_arith_${run-id}.script.yaml`
- The script MUST be deployed to the cloud workspace `evaluation-ws` (`https://app.windmill.dev`) at remote path `f/zealt/go_arith_${run-id}`.
- When the deployed script is invoked with `{"threshold": 5, "name": "x"}`, the returned JSON value MUST equal `{"computed": 10, "target": "x"}` (key order is irrelevant; no extra keys are allowed).
- The Go function signature MUST accept arguments named `threshold` (integer) and `name` (string), in that order, so that `wmill script run --data '{"threshold": 5, "name": "x"}'` resolves them correctly.
- Ensure the deployment and remote execution actions are actually performed.
- Log file: /home/user/myproject/output.log
- The log file MUST contain a line in the format: `Script path: f/zealt/go_arith_<run-id>` (with the literal resolved value of `run-id`).
- The log file MUST contain a line in the format: `Output: {"computed": 10, "target": "x"}` (key order is irrelevant; whitespace is irrelevant).

