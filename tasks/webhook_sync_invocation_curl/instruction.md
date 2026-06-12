# Windmill Synchronous Webhook Invocation with curl

## Background
Windmill autogenerates a synchronous webhook endpoint for every deployed script. That endpoint blocks until the underlying job finishes and returns the script's JSON result as the HTTP response body. In this task you will deploy a tiny Python script to the cloud Windmill instance at `https://app.windmill.dev` and exercise its synchronous webhook using `curl`, capturing the raw HTTP response (status line + body) to disk for verification.

## Requirements
- Read the `run-id` from the `ZEALT_RUN_ID` environment variable. All names below depend on it.
- Authenticate the `wmill` CLI against the cloud instance using the workspace id in `WINDMILL_WORKSPACE` and the bearer token in `WINDMILL_TOKEN`.
- Author a Python script that accepts a single string argument `message` and returns the JSON object `{"echoed": message}`.
- Deploy the script to the workspace at the path `u/${WINDMILL_USERNAME}/echo_message_${run_id_safe}` where `run_id_safe` is the value of `ZEALT_RUN_ID` with every `-` replaced by `_` (so for `zr-abc123` the path is `u/${WINDMILL_USERNAME}/echo_message_zr_abc123`).
- Invoke the synchronous webhook for the deployed script with `curl` (POST, `Content-Type: application/json`, `Authorization: Bearer ${WINDMILL_TOKEN}`) and JSON body `{"message": "harbor-${ZEALT_RUN_ID}"}`.
- Capture the full HTTP response to disk: the status line and response headers to `/home/user/windmill-webhook/response.headers` and the response body to `/home/user/windmill-webhook/response.body.json`. Both files MUST be produced from the same single `curl` invocation against the synchronous endpoint.

## Implementation Hints
- The cloud sync webhook URL pattern is documented at <https://www.windmill.dev/docs/core_concepts/webhooks>. It targets the `run_wait_result` route under `/api/w/<workspace>/jobs/`.
- The `wmill` CLI (`npm install -g windmill-cli`) can deploy a script using `wmill script push` or `wmill sync push` after `wmill workspace add`.
- Use `curl -D <headers_file> -o <body_file> -s -w '%{http_code}\n'` (or `curl -i ... | tee`) to persist both the HTTP status/headers and the parsed JSON body in one shot.
- The script can be written as plain Python; the `main(message: str)` signature is enough for Windmill to derive the JSON schema.

## Acceptance Criteria
- Project path: /home/user/windmill-webhook
- Ensure the script is actually deployed to the cloud Windmill workspace and the synchronous webhook is actually invoked.
- The deployed script path MUST be `u/${WINDMILL_USERNAME}/echo_message_${run_id_safe}` where `run_id_safe` is `ZEALT_RUN_ID` with hyphens replaced by underscores.
- Response headers file: /home/user/windmill-webhook/response.headers
  - The first line MUST start with `HTTP/` and contain the status code `200`.
  - A `Content-Type` header MUST be present and MUST contain `application/json` (additional parameters such as `charset` are allowed).
- Response body file: /home/user/windmill-webhook/response.body.json
  - MUST be valid JSON.
  - MUST equal exactly `{"echoed": "harbor-<ZEALT_RUN_ID>"}` (the same `run-id` value, with the leading `harbor-` prefix and no extra keys).

