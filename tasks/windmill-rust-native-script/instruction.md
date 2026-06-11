# Windmill Rust Native Script

## Background
Windmill (https://app.windmill.dev) is an open-source developer platform that runs scripts authored in many languages (TypeScript, Python, Go, **Rust**, ...). Each Rust script is stored on disk as a pair of files: a `.rs` source containing a `main` function and a `.script.yaml` metadata companion. Cargo dependencies are declared inline through a partial `Cargo.toml` annotation embedded at the top of the Rust source so the worker can resolve them on first run.

In this task you will author a tiny Rust-on-Windmill script, deploy it to the cloud workspace via the `wmill` CLI, and verify that it executes against the cloud workers.

## Requirements
- Author a Rust script at the path `f/eval/rust_doubler` inside the project workspace folder.
- Declare an inline Cargo dependency on `serde_json = "1.0"` using Windmill's documented partial `Cargo.toml` annotation block (the `//! ` doc-comment block containing a ` ```cargo` fence).
- The script's `main` function must accept two owned parameters, a `String` named `name` and an `i32` named `threshold`, and return a `serde_json::Value` (either directly or wrapped in `anyhow::Result<_>`).
- The returned JSON payload must always have the shape `{ "status": "ok", "computed": <threshold * 2>, "target": <name> }`.
- Provide a `.script.yaml` companion that declares `language: rust` so Windmill recognises the script as a Rust script when it is synchronised.
- Synchronise the script to the cloud Windmill workspace using the `wmill` CLI so that `wmill script run f/eval/rust_doubler` succeeds against the real cloud workers.

## Implementation Hints
- The cloud Windmill instance URL is `https://app.windmill.dev`. The agent's `wmill` CLI has already been authenticated to a workspace whose ID is provided in the `WINDMILL_WORKSPACE` environment variable, using the token in `WINDMILL_TOKEN`.
- Use the `wmill` CLI to bootstrap and/or push the script (`wmill script bootstrap`, `wmill sync push`, etc.). Consult `wmill --help` and the Windmill docs (https://www.windmill.dev/docs and https://www.windmill.dev/llms.txt) for exact subcommand usage.
- Inline Cargo dependencies must use the doc-comment `//! ` prefix wrapping a ` ```cargo` ... ` ``` ` fenced block, e.g.:
  ```
  //! ```cargo
  //! [dependencies]
  //! serde_json = "1.0"
  //! ```
  ```
- Rust scripts can return either `serde_json::Value` directly or `anyhow::Result<serde_json::Value>`; both forms are acceptable as long as the payload shape matches.
- The first Rust execution on a fresh worker may need to compile dependencies, so allow generous time when invoking `wmill script run`.

## Acceptance Criteria
- Project path: /home/user/myproject
- The Rust source file must exist at `/home/user/myproject/f/eval/rust_doubler.rs` and contain a `main` function whose signature takes a `String` parameter named `name` and an `i32` parameter named `threshold`.
- A YAML companion must exist at `/home/user/myproject/f/eval/rust_doubler.script.yaml` and explicitly declare `language: rust`.
- The Rust source must contain an inline partial Cargo manifest (the `//!` block with a ` ```cargo` fence) that lists `serde_json` as a dependency.
- Command: `wmill script run f/eval/rust_doubler -d '{"name":"<name>","threshold":<threshold>}' -s` executed from `/home/user/myproject` must, within 180 seconds, exit with status 0 and print to stdout a single JSON object equal (by structural equality) to `{"status":"ok","computed":<threshold * 2>,"target":"<name>"}`.
- The script must be deployed to the cloud workspace identified by the `WINDMILL_WORKSPACE` environment variable on `https://app.windmill.dev`, not merely created locally.

