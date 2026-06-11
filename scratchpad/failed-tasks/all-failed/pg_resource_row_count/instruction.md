# Windmill: Count Public Tables via a Postgresql Resource (Bun)

## Background
Windmill is an open-source workflow engine and developer platform. Scripts in Windmill are typed functions whose parameters are turned into a JSON Schema and exposed via the CLI and API. Resources are JSON-Schema-typed configuration objects (for example database connections) referenced from scripts via the `$res:<path>` syntax.

You will author a small TypeScript (Bun) script that connects to a PostgreSQL database described by a Windmill `Postgresql` resource and returns the number of tables present in the `public` schema. The Windmill cloud workspace at `https://app.windmill.dev` is already configured locally (see the project's `wmill.yaml`), the workspace name is exported as `WINDMILL_WORKSPACE`, and a Bearer token is exported as `WINDMILL_TOKEN`. A `Postgresql` resource has already been seeded at `f/eval/pg_resource` and points to a publicly accessible read-only PostgreSQL mirror. **DO NOT** create, modify or delete that resource.

## Requirements
- Author a Bun (TypeScript) Windmill script at `f/eval/pg_row_count.ts` whose `main` function accepts a single argument named `pg` typed as the canonical Windmill `Postgresql` resource type, connects to that PostgreSQL instance, executes
  `SELECT COUNT(*) AS n FROM information_schema.tables WHERE table_schema = 'public'`
  and returns the result as a JSON object of shape `{ "count": <integer> }` where `count` is a non-negative integer.
- Provide the matching script-metadata file `f/eval/pg_row_count.script.yaml` declaring the script schema and the Bun runtime so that `wmill script push` can deploy the script.
- Push the script to the cloud workspace and execute it once with the seeded resource to confirm it works.

## Implementation Hints
- The project already contains a configured `wmill.yaml` and a workspace entry pointing at `https://app.windmill.dev`; you can run `wmill` commands directly from the project root without re-authenticating.
- The canonical `Postgresql` resource type has the fields `host`, `port`, `user`, `dbname`, `sslmode`, `password` (and optionally `root_certificate_pem`). Declare the full TypeScript type literal in the script so that the inferred schema is rich enough.
- Import the Windmill client as `import * as wmill from "windmill-client"`. Use any standard Bun-compatible Postgres client (for example `pg` from npm) to execute the query.
- The `.script.yaml` file should mirror the function signature: its top-level keys typically include `summary`, `description`, `lock`, `kind: script`, and a JSON-Schema 2020-12 `schema` block whose `properties.pg` references `format: resource-postgresql` (the convention Windmill uses to bind a Postgresql resource).
- Push the script with `wmill script push f/eval/pg_row_count.ts`. Trigger it with:
  `wmill script run f/eval/pg_row_count -d '{"pg": "$res:f/eval/pg_resource"}'`
  The command should exit with status 0 and print a JSON document containing a `count` field.
- The seeded database may contain zero tables in the `public` schema; that is acceptable. The verifier only requires `count` to be a non-negative integer.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Command: `wmill script run f/eval/pg_row_count -d '{"pg": "$res:f/eval/pg_resource"}'`
- The file `f/eval/pg_row_count.ts` must exist under the project path and:
  - Import `windmill-client` (for example `import * as wmill from "windmill-client"`).
  - Export an async `main` function whose signature is exactly `export async function main(pg: Postgresql)` (the parameter must be literally named `pg` and typed as `Postgresql`).
- A companion metadata file `f/eval/pg_row_count.script.yaml` must exist alongside the script, declare `kind: script`, and target the Bun runtime (for example via `language: bun` or by relying on Windmill's default Bun runtime for `.ts` files configured in `wmill.yaml`).
- The script must be pushed to the cloud workspace so that running it remotely succeeds.
- The command above must exit with status code 0 and emit, on stdout, a JSON object that contains a `count` field whose value is an integer `>= 0`.
- Do not modify or delete the pre-seeded resource `f/eval/pg_resource`.

