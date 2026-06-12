# Windmill Webhook with HMAC-SHA256 Signature Verification (Python)

## Background
Many external systems (Stripe, GitHub, Slack, Discord, etc.) sign webhook payloads with HMAC-SHA256 and put the signature in a custom HTTP header. Receivers must verify the signature against the **raw, unparsed** request body before trusting the payload. Windmill exposes auto-generated webhooks for every script, and supports both forwarding custom headers and delivering the raw body verbatim to the script. Your job is to build the receiving end on the Windmill cloud instance (https://app.windmill.dev) using a Python script.

## Requirements
- Author a Python Windmill script that:
  - Reads its signing secret from a Windmill **Variable** (not hard-coded).
  - Computes HMAC-SHA256 of the raw request body using `hmac` and `hashlib.sha256` from the Python standard library.
  - Compares the computed digest to a signature delivered through a custom HTTP request header in a timing-safe manner.
  - Returns `{"valid": true}` for a correctly-signed request and rejects incorrectly-signed requests (either return `{"valid": false}` or surface an HTTP error — either path is acceptable as long as a valid signature is required).
- Deploy the script and its Variable to the Windmill cloud workspace using the `wmill` CLI.
- The script's webhook must be callable so that an HTTP client can submit `(raw_body, signature_header)` and get back the verification result via the synchronous `run_wait_result` endpoint.

## Implementation Hints
- Read the Windmill docs on webhooks, especially the sections on **Raw payload / body**, **Headers**, and the **synchronous (Result/Sync)** endpoint format.
- The Windmill webhook system can forward both the raw request body and selected HTTP headers into your script's function arguments via query-string options.
- Use the `wmill` Python client to read the Variable inside the script. Store the secret as a Windmill **secret variable** (so it is encrypted at rest and masked in logs).
- Authenticate the `wmill` CLI against the cloud instance using the API token in `WM_TOKEN` and the workspace id in `WM_WORKSPACE`. Use `wmill workspace add ... --token "$WM_TOKEN"` (non-interactive) followed by `wmill sync push --yes`, or use the raw HTTP API directly — whichever you prefer.
- The script and the Variable must live under a `run-id`-scoped path so concurrent evaluation runs do not collide.

## Acceptance Criteria
- Project path: `/home/user/wmtask`
- Read `run-id` from the `ZEALT_RUN_ID` environment variable and substitute it for `${run-id}` everywhere below.
- Deploy to the Windmill cloud workspace identified by `WM_WORKSPACE` (default `https://app.windmill.dev`) using the API token in `WM_TOKEN`.
- A Python script is deployed at path `f/zealt_${run-id}/sig_verify`.
  - Script content must import the standard-library modules `hmac` and `hashlib` and use `hashlib.sha256` for the digest.
  - Script content must obtain the signing secret by calling `wmill.get_variable` (the `wmill` Python client).
- A Windmill Variable is deployed at path `f/zealt_${run-id}/webhook_secret`.
  - It must be marked as a secret variable.
  - Its value is the signing secret used by the script.
- The script's auto-generated synchronous webhook (`POST /api/w/<workspace>/jobs/run_wait_result/p/f/zealt_${run-id}/sig_verify`) is callable with a Bearer token and:
  - Returns `{"valid": true}` when the request carries a correct HMAC-SHA256 hex digest of the raw request body in a custom HTTP header.
  - Rejects requests with an incorrect signature — either by returning `{"valid": false}` or by returning a non-success HTTP status / error result. The verifier accepts either rejection style.
- The webhook invocation must use Windmill's documented `raw=true` query-arg convention so the script receives the raw request body verbatim, and must use Windmill's documented header-forwarding query-arg convention so the signature header reaches the script as a function argument.
- Log file: `/home/user/wmtask/output.log` containing two lines in the exact format:
  - `Script path: f/zealt_${run-id}/sig_verify`
  - `Signature header name: <header-name-you-chose>` (any custom header name you use, e.g. `X-Signature`).

