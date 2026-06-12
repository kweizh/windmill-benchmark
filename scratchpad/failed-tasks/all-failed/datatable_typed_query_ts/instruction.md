# Windmill Data Table Typed Query (TypeScript)

## Background
Windmill provides workspace-scoped Built-in Data Tables backed by a managed PostgreSQL database. You can interact with them imperatively from any script via the `windmill-client` SDK. In this task, you will use the cloud-hosted Windmill instance to (1) provision a small relational table inside the default Data Table, (2) seed it with a few rows, and (3) author a Bun TypeScript script that runs a parameterized query and returns aggregated information.

You will work entirely against the cloud Windmill instance at https://app.windmill.dev. The `wmill` CLI and a Bearer token are already configured in the environment — DO NOT attempt to start a local Windmill server.

## Requirements
- Read the run scope id from the `ZEALT_RUN_ID` environment variable. Use it to compute a per-run schema name `zr_${ZEALT_RUN_ID}` so concurrent task attempts do not collide.
- Inside the workspace's default (`main`) Data Table, create the schema `zr_${ZEALT_RUN_ID}` if it does not already exist, then (re)create a table `events` with this exact schema:
  - `id`  INTEGER PRIMARY KEY
  - `kind` TEXT NOT NULL
- Seed the `events` table with exactly these rows (any insertion order is fine):
  - `(1, 'login')`
  - `(2, 'logout')`
  - `(3, 'login')`
  - `(4, 'signup')`
  - `(5, 'login')`
- Author a TypeScript (Bun) Windmill script that uses the `windmill-client` Data Table client. The script must:
  - Accept a single argument `kind: string`.
  - Run a parameterized query against `zr_${ZEALT_RUN_ID}.events` selecting rows where `kind = $1`.
  - Return a JSON object with the shape `{ count: number, rows: { id: number, kind: string }[] }` where `count` is the number of matching rows and `rows` contains the matching rows.
- Save the script source as `/home/user/myproject/script.ts` so the verifier can execute it.
- Deploy the script to the cloud workspace at path `f/zr_${ZEALT_RUN_ID}/query_events` so it can be invoked via `wmill script run`.

## Implementation Hints
- The Windmill CLI is pre-installed and a workspace named `evaluation-ws` is pre-authenticated. Inspect `wmill --help` and `wmill script --help` to discover how to run a script with arguments and capture its JSON result.
- The Data Table client in TypeScript is exposed by the `windmill-client` SDK as a tagged-template SQL builder. Refer to the official docs at https://www.windmill.dev/docs/core_concepts/persistent_storage/data_tables for the exact API and its `fetch` / `fetchOne` execution methods.
- The default Data Table is named `main`. You may pass a search-path suffix (e.g. `:zr_<id>`) when instantiating the client to scope queries to your per-run schema, or fully-qualify table names with `schema.table`.
- Use a SQL admin script (Python or TypeScript, your choice) to set up the schema + seed data, or use the Database Studio endpoints in the API — either is acceptable as long as the resulting database state matches the requirements.
- A working example to run your script after deployment is `wmill script run f/zr_${ZEALT_RUN_ID}/query_events -d '{"kind":"login"}'`.

## Acceptance Criteria
- Project path: /home/user/myproject
- The cloud workspace's default Data Table (`main`) contains a schema `zr_${ZEALT_RUN_ID}` with a table `events(id INTEGER PRIMARY KEY, kind TEXT NOT NULL)` seeded with the exact 5 rows listed in the Requirements (order does not matter).
- A TypeScript Bun script exists at `/home/user/myproject/script.ts` that uses `wmill.datatable()` from `windmill-client` to perform a parameterized `SELECT` on the per-run `events` table.
- The script is deployed under the cloud workspace path `f/zr_${ZEALT_RUN_ID}/query_events`.
- Command: `wmill script run f/zr_${ZEALT_RUN_ID}/query_events -d '{"kind":"<kind>"}'`
  - Input argument format: `{"kind": string}`
  - Output: JSON object of shape `{"count": number, "rows": [{"id": number, "kind": string}, ...]}` where `count` equals `rows.length` and `rows` contains exactly the rows in the seeded table whose `kind` column equals the provided argument. Row ordering is not asserted.

