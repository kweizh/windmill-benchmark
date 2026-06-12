# Invoke a Pre-deployed Windmill Script with the `wmill` CLI

## Background
You are working with a Windmill Cloud workspace that already has a deployed script for adding two integers. Your job is to invoke this script from the command line using the `wmill` CLI, pass the inputs inline as JSON, and capture the JSON result into a file so a downstream evaluator can consume it.

The target Windmill instance is the public cloud (`https://app.windmill.dev`). A workspace has already been registered locally with the `wmill` CLI inside this environment, and an API token is configured. The deployed script is named `add_numbers` and lives at the Windmill path `f/zealt_eval/add_numbers`. Given inputs `a` and `b`, the script returns the integer `a + b` as its JSON result.

## Requirements
- Use the `wmill` CLI (already installed in the environment, and already authenticated against the cloud workspace) to execute the pre-deployed script `f/zealt_eval/add_numbers`.
- Pass the inputs inline as a JSON string with `a = 17` and `b = 25`.
- Capture the script's JSON result and write it to `/home/user/result.json`.
- The file must contain ONLY the parsed JSON result returned by the script (no Windmill log lines, no ANSI color codes, no trailing prompts).

## Implementation Hints
- The relevant subcommand is `wmill script run`, which accepts the script path and inline inputs via a `-d` / `--data` flag.
- The `wmill script run` command supports a flag that suppresses streaming logs and emits only the final result as JSON on stdout — that is the recommended way to capture clean JSON output for redirection into a file.
- The workspace and token are already configured; you should not need to run `wmill workspace add` or set any extra environment variables. A simple verification with `wmill workspace whoami` should confirm authentication.
- You only need to issue ONE command (with shell redirection) to satisfy this task — there is no need to write any local script files or push anything to Windmill.

## Acceptance Criteria
- Project path: /home/user
- Command: a single `wmill script run` invocation that targets `f/zealt_eval/add_numbers`, passes the inputs as inline JSON via the `-d`/`--data` flag, and writes its JSON result to `/home/user/result.json`.
- Inputs used: `{"a": 17, "b": 25}`.
- Output file: `/home/user/result.json` must exist and contain valid JSON that equals the result returned by the script for those inputs.
- The contents of `/home/user/result.json` must be parseable as JSON. The evaluator parses the file and compares the parsed value against the expected JSON result; it does NOT compare raw text formatting, color codes, or surrounding log output.

