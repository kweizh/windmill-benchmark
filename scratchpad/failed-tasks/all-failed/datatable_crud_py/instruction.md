# Windmill Built-In Data Tables CRUD (Python)

## Background
Windmill provides a workspace-scoped, zero-setup PostgreSQL store called **Built-In Data Tables**. Scripts read and write to it through the official `wmill.datatable()` Python SDK without ever handling raw database credentials. In this task you will author two Python scripts that together perform a tiny write/read CRUD round-trip against the default workspace data table on the public Windmill cloud (`https://app.windmill.dev`).

## Requirements
- Author two Python scripts inside a local workspace folder so they can be pushed to the configured Windmill cloud workspace with the `wmill` CLI.
  1. `f/eval/datatable_writer.py` — `main(records: list[dict])` creates the table if needed, inserts every record, and returns `{"inserted": <n>}` where `<n>` is the count of inserted rows.
  2. `f/eval/datatable_reader.py` — `main()` takes no arguments and returns `{"rows": [...]}` containing every row of the table, sorted by `id` ascending.
- Both scripts MUST use Windmill's official Built-In Data Tables SDK (`wmill.datatable()`).
- The scripts MUST NOT open a raw PostgreSQL connection (no `psycopg`, `psycopg2`, `asyncpg`, raw `psql`, or any other direct DB driver).
- The table that the two scripts share MUST be named `eval_orders_<RUN_ID>`, where `<RUN_ID>` is the literal value of the `ZEALT_RUN_ID` environment variable available in the shell at authoring time. Inline the resolved name into both scripts; do not read the env var at script runtime (Windmill workers do not have access to it).
- The table must have at least the columns `id INT` and `status TEXT`.
- Author each script as a Windmill script asset pair (a `.py` content file plus a matching `.script.yaml` metadata file) so that `wmill sync push --yes` will deploy both scripts to the remote workspace.
- After authoring, deploy the scripts to the configured Windmill cloud workspace with `wmill sync push --yes`.

## Implementation Hints
- Install the CLI with `npm install -g windmill-cli` (Node ≥ 20 is already available in the environment).
- Authenticate non-interactively against the cloud instance using the `WINDMILL_TOKEN` and `WINDMILL_WORKSPACE` environment variables. The cloud base URL is always `https://app.windmill.dev`.
- Bootstrap the local sync folder with `wmill init` (or hand-write a minimal `wmill.yaml` that includes the `f/**` path).
- A Windmill Python script's entrypoint is a top-level `def main(...)` function. Return values are JSON-serialized automatically.
- The Built-In Data Tables SDK exposes `db = wmill.datatable()` and uses positional `$1`, `$2`, ... parameters: `db.query("... $1 ...", value).execute()` for DDL/INSERT and `.fetch()` / `.fetch_one()` for SELECTs.
- The default data table (named `main`) is implicit — you do not need to pass any name to `wmill.datatable()`.
- Resolve `ZEALT_RUN_ID` from your shell before writing the scripts and substitute the literal value into the SQL strings.
- Verify everything works end-to-end with `wmill script run f/eval/datatable_writer -d '{"records": [...]}'` and `wmill script run f/eval/datatable_reader` from inside the project folder.

## Acceptance Criteria
- Project path: /home/user/wmill-project
- Both Windmill script assets must be deployed to the cloud workspace (`https://app.windmill.dev`, workspace = `$WINDMILL_WORKSPACE`).
- The two scripts MUST exist locally at exactly these paths and each MUST be paired with a sibling `*.script.yaml` metadata file:
  - `/home/user/wmill-project/f/eval/datatable_writer.py`
  - `/home/user/wmill-project/f/eval/datatable_writer.script.yaml`
  - `/home/user/wmill-project/f/eval/datatable_reader.py`
  - `/home/user/wmill-project/f/eval/datatable_reader.script.yaml`
- Neither `.py` file may import or invoke `psycopg`, `psycopg2`, `asyncpg`, `pg8000`, or any other raw Postgres driver, and may not shell out to `psql`. All database access must go through `wmill.datatable()`.
- The shared table name must be `eval_orders_<RUN_ID>` where `<RUN_ID>` is the literal value of the `ZEALT_RUN_ID` environment variable at authoring time.
- Writer behavior:
  - Command: `wmill script run f/eval/datatable_writer -d '{"records": <JSON_ARRAY>}' -s`
  - Each record is a JSON object `{"id": <int>, "status": <string>}`.
  - The command exits 0 and prints a JSON object of the shape `{"inserted": <int>}` where `<int>` equals the number of records that were inserted.
- Reader behavior:
  - Command: `wmill script run f/eval/datatable_reader -s`
  - The command exits 0 and prints a JSON object of the shape `{"rows": [{"id": <int>, "status": <string>}, ...]}`.
  - The `rows` array MUST be sorted by `id` ascending and MUST contain exactly the records that were most recently written by the writer in the same run.

