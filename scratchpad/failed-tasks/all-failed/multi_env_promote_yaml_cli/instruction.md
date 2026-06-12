# Promote a Windmill Script from Staging to Production via `wmill sync`

## Background
Your team manages two Windmill workspaces on the cloud-hosted instance `https://app.windmill.dev`: a `staging` workspace and a `production` workspace. A small TypeScript (Bun) script has already been deployed and tested in `staging`, and you must now promote that exact script to `production` by means of the `wmill` CLI in a locally version-controlled folder. You must NOT log in to the Windmill UI; the entire promotion must be reproducible from the CLI and a single declarative `wmill.yaml`.

A cloud Windmill workspace contains many unrelated assets (other scripts, flows, apps, variables, schedules). A naive `wmill sync push` is a destructive, stateless reconcile that will delete anything on the target that is not present locally. You must therefore scope the sync narrowly so that only the script being promoted is affected.

## Requirements
- Initialise a Windmill project folder at `/home/user/promote-project` that contains a `wmill.yaml` file.
- The `wmill.yaml` MUST declare BOTH workspaces under the unified `workspaces:` key documented at https://www.windmill.dev/docs/advanced/cli/sync — one entry named `staging` and one entry named `production`. Each entry must point at the cloud instance via `baseUrl: https://app.windmill.dev` and an explicit `workspaceId` matching the cloud workspace ids supplied via environment variables.
- The `wmill.yaml` MUST scope the sync narrowly (via `includes:`) so that running `wmill sync push --workspace production` will only create/update the script being promoted and will NOT delete or modify any other asset that already lives in the `production` workspace.
- Register the two cloud workspaces locally with `wmill workspace add` using the same names (`staging` and `production`) so the CLI can resolve them.
- Pull the script from the staging workspace into the local folder.
- Use a SINGLE invocation of `wmill sync push --workspace production --yes` to promote the script. Do NOT call the Windmill HTTP API directly to create the script in `production`, and do NOT manually `wmill workspace switch` then `wmill sync push` without `--workspace`.
- Append a log line of the form `Promoted: f/promote_${run-id}/hello -> ${production_workspace_id}` to `/home/user/promote-project/output.log` after the push completes successfully.

## Implementation Hints
- Read `run-id` from the `ZEALT_RUN_ID` environment variable. The script you must promote already exists in the `staging` workspace at `f/promote_${run-id}/hello`.
- The cloud base URL, API token, and the two workspace IDs are provided via the environment variables `WMILL_BASE_URL`, `WMILL_TOKEN`, `WMILL_STAGING_WORKSPACE_ID`, and `WMILL_PROD_WORKSPACE_ID`.
- The `wmill` CLI is preinstalled. Use `wmill workspace add <name> <workspace_id> <base_url>` (passing `--token` as needed) to register both workspaces locally before syncing.
- Read the official documentation at https://www.windmill.dev/docs/advanced/cli/sync to determine the exact shape of the multi-workspace `wmill.yaml` (the `workspaces:` key, the per-entry `workspaceId` and `baseUrl` fields) and the correct flag for targeting a workspace on push (`--workspace`).
- To make the push non-destructive, narrow what `wmill sync push` sees by configuring `includes:` so the pattern matches ONLY the folder `f/promote_${run-id}/**`. The default `skipVariables`, `skipResources`, `skipSecrets`, and `skipResourceTypes` flags should remain at their safe defaults so unrelated production assets are untouched.
- `wmill sync pull --workspace staging --yes` will populate the local folder from staging without needing to switch the active profile manually.

## Acceptance Criteria
- Project path: `/home/user/promote-project`
- Ensure the real promotion action is executed against the cloud `production` workspace; the script must actually exist in production after the task completes.
- The folder MUST contain a `wmill.yaml` whose `workspaces:` mapping declares exactly two entries with the keys `staging` and `production`, each with `baseUrl: https://app.windmill.dev` and a `workspaceId` matching the corresponding environment variable.
- The folder MUST contain a script at the local path `f/promote_${run-id}/hello.ts` (or `.bun.ts`) plus its sibling metadata file (`hello.script.yaml`), matching what was deployed in staging.
- The script `f/promote_${run-id}/hello` MUST exist in the cloud `production` workspace and MUST be callable via the Windmill HTTP API (`POST /api/w/${WMILL_PROD_WORKSPACE_ID}/jobs/run_wait_result/p/f/promote_${run-id}/hello`).
- The pre-existing canary script `f/canary_${run-id}/keep_me` in the `production` workspace MUST still exist after promotion (i.e., the sync must NOT have deleted it).
- Log file: `/home/user/promote-project/output.log` MUST contain a line in the format: `Promoted: f/promote_${run-id}/hello -> <production_workspace_id>`.
- All resource paths MUST use `run-id` from the `ZEALT_RUN_ID` environment variable as shown.

