# Secret Variable Log Masking with Windmill (Python)

## Background
Windmill encrypts variables marked as secrets and automatically masks them in job logs so that sensitive values never land in `job_logs` even if a script intentionally prints them. The mask is documented in the [Secret masking in job logs changelog](https://www.windmill.dev/changelog/secret-masking-job-logs): the first 3 characters of the secret are kept and the rest is replaced by `*****`. Only values of 8 characters or more are masked.

Your job is to demonstrate this behaviour end-to-end against the **cloud-hosted** Windmill instance at `https://app.windmill.dev`. You will declaratively define a secret Windmill Variable, write a Python script that fetches and prints the secret value through the `wmill` Python SDK, deploy both assets to the cloud workspace, execute the script, and persist the resulting job UUID so the verifier can pull its logs through the Windmill API.

## Requirements
- Authenticate the `wmill` CLI against the cloud Windmill instance using the API token, workspace ID, and base URL provided in environment variables.
- Bootstrap a local Windmill workspace under `/home/user/myproject` containing a `wmill.yaml` file and the asset folders described below.
- Read `run-id` from the `ZEALT_RUN_ID` environment variable, sanitize it for Windmill identifiers (replace every `-` with `_`) and reuse the sanitized id as a unique suffix on every Windmill asset path created by this task. Refer to the sanitized id below as `${run_id_safe}`.
- Declaratively create an **encrypted** Windmill Variable at the path `f/secret_masking_${run_id_safe}/api_key` whose value is literally `secret_value_${run_id_safe}_padding` (this string is longer than 8 characters so Windmill will mask it). The variable must be defined via a `.variable.yaml` manifest on disk (not only via the imperative `wmill variable add` command).
- Declaratively create a Python script at `f/secret_masking_${run_id_safe}/print_secret` consisting of a `.py` file paired with a `.script.yaml` metadata file. The script must call `wmill.get_variable("f/secret_masking_${run_id_safe}/api_key")` and print the returned value to stdout (e.g., via `print(...)`).
- Push the variable, folder, and script to the cloud workspace using the declarative `wmill sync push` flow (you must pass `--include-secrets` so the secret variable is uploaded; otherwise the default settings skip secrets).
- Trigger one execution of the deployed script through the Windmill API or the `wmill` CLI, capture the resulting job UUID, and write the line `Job ID: <job_uuid>` to `/home/user/myproject/output.log` (a single line is enough).
- Do **not** print, log, or otherwise persist the plaintext secret value anywhere outside of the Windmill job's masked logs. The point of the task is to prove that Windmill masks it for you.

## Implementation Hints
- Install the CLI with `npm install -g windmill-cli` (Node.js ≥ 20 is already in the image).
- Use `wmill workspace add` (supplying `--remote`, the workspace id, and the token) followed by `wmill init` to bootstrap `wmill.yaml`.
- Variable manifests follow the schema documented in the [`wmill variable` reference](https://www.windmill.dev/docs/advanced/cli/variable): the YAML must contain `value`, `is_secret: true`, and the other standard fields. Pushing with `--plain-secrets` lets you keep the value in clear text inside the manifest while still marking it as a secret in the workspace.
- Script assets live as file pairs on disk; see the [Python quickstart](https://www.windmill.dev/docs/getting_started/scripts_quickstart/python) and the [`wmill.yaml` reference](https://www.windmill.dev/docs/advanced/cli/wmill-yaml-reference) for the exact `.script.yaml` shape and the `includeSecrets` toggle.
- The Windmill Python SDK exposes `wmill.get_variable(path: str)`; use it inside `main()` and print the result. Returning the value from `main()` will also be captured in the masked logs, so a plain `print` is sufficient.
- To execute the deployed script and obtain a job UUID you can either use `wmill script run` and capture the UUID it prints, or POST to `/api/w/<workspace>/jobs/run/p/<path>` with the bearer token and read the UUID from the response body.
- Logs are retrievable via `wmill job logs <uuid>` or via `GET /api/w/<workspace>/jobs_u/get_logs/<uuid>` if you want to confirm masking yourself.

## Acceptance Criteria
- Project path: /home/user/myproject
- Ensure the real Windmill deployment and execution actions are performed; the verifier will not redeploy anything.
- A `wmill.yaml` file exists at `/home/user/myproject/wmill.yaml`.
- A variable manifest exists at `/home/user/myproject/f/secret_masking_${run_id_safe}/api_key.variable.yaml` and is marked as a secret (`is_secret: true`).
- A Python script file pair exists at `/home/user/myproject/f/secret_masking_${run_id_safe}/print_secret.py` and `/home/user/myproject/f/secret_masking_${run_id_safe}/print_secret.script.yaml`, with the `.py` file invoking `wmill.get_variable("f/secret_masking_${run_id_safe}/api_key")`.
- Log file: `/home/user/myproject/output.log` contains exactly one line in the format `Job ID: <job_uuid>`, where `<job_uuid>` is the UUID of a completed run of the deployed script.
- Fetching the job logs through the Windmill API for that UUID must show that the secret value is masked: the logs must contain the prefix-and-stars form documented in the Windmill changelog (the first 3 characters of the secret followed by `*****`, i.e. `sec*****`) and must **not** contain the full plaintext value `secret_value_${run_id_safe}_padding`.
- The variable, folder, and script paths in the cloud workspace must all be suffixed with `${run_id_safe}` so concurrent runs do not collide.

