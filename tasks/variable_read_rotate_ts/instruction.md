# Windmill: Read and Rotate a Secret Variable (TypeScript / Bun)

## Background
Windmill is an open-source, code-first workflow and serverless platform. Workspace variables (including encrypted secrets) are accessed from scripts through the `windmill-client` SDK and managed from the outside through the `wmill` CLI or REST API.

In this task you will author a TypeScript (Bun) Windmill script that performs a simple secret-rotation routine. The script must read a pre-existing workspace variable, write back an updated value, and return both values to the caller.

The target workspace is the public Windmill Cloud at https://app.windmill.dev. A workspace ID is exposed via the `WINDMILL_WORKSPACE` environment variable and an API token via the `WINDMILL_TOKEN` environment variable. The wmill CLI is already installed and the workspace `evaluation` is already configured against the cloud instance; you can run `wmill` commands directly from the project folder.

A secret variable at the path `f/eval/session_token` has already been created in the workspace with the initial value `INITIAL_SECRET` (`is_secret: true`).

## Requirements
- Author a Windmill TypeScript (Bun) script that:
  1. Imports the `windmill-client` SDK.
  2. Reads the current value of the workspace variable at the path `f/eval/session_token` using `wmill.getVariable`.
  3. Computes a rotated value by appending the literal suffix `_rotated` to the current value.
  4. Writes the rotated value back to the same variable path using `wmill.setVariable`.
  5. Returns a JSON object of the shape `{ "previous": <old value>, "next": <rotated value> }`.
- Place the script on disk in the local workspace folder so that it deploys to the Windmill script path `f/eval/var_rotate`.
- Deploy the script to the Windmill Cloud workspace so that it can be executed with `wmill script run f/eval/var_rotate`.

## Implementation Hints
- The project directory `/home/user/project` is already a Windmill workspace folder (already initialized with `wmill init` and the `evaluation` remote selected). You only need to add the script file and push it.
- A Windmill TypeScript script is a plain `.ts` file that exports an async `main` function. Companion metadata files (such as `*.script.yaml`) can be generated automatically when the script is pushed.
- The Windmill TypeScript client exposes `wmill.getVariable(path)` and `wmill.setVariable(path, value)` for variable I/O.
- Use `wmill sync push --yes` (or `wmill script push`) to upload the script to the remote workspace, and `wmill script run <path>` to trigger an execution from the CLI. `wmill script run` prints the JSON result of the script's `main` return value to stdout on success.
- The variable is a secret. The script still reads it with `wmill.getVariable` exactly like a non-secret variable; Windmill takes care of decryption and log masking.

## Acceptance Criteria
- Project path: /home/user/project
- The agent is responsible for actually creating, deploying, and executing the script against the Windmill Cloud workspace.
- A TypeScript script file is present at `/home/user/project/f/eval/var_rotate.ts` and:
  - Imports from `windmill-client`.
  - Contains at least one call to `getVariable(` and at least one call to `setVariable(`.
- After deployment, the command `wmill script run f/eval/var_rotate` (executed from `/home/user/project`) exits with status code 0 and prints a JSON object on stdout that, when parsed, satisfies:
  - `previous` equals the string `INITIAL_SECRET`.
  - `next` equals the string `INITIAL_SECRET_rotated`.
- After the script has been run, the workspace variable `f/eval/session_token` (queried via the Windmill CLI / API) has its value updated to `INITIAL_SECRET_rotated`.

