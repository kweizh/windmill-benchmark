# GitOps Sync with `excludes:` Glob Protection

## Background
You are inside a pre-initialised Windmill workspace at `/home/user/myproject` that is already authenticated against the cloud instance `https://app.windmill.dev`. `wmill init` has already run, so a `wmill.yaml` is present and a workspace profile (`evaluation-ws`) is registered.

The shared cloud workspace already contains a remote-only script at `f/gitops_${SAFE_ID}/legacy.ts` that was seeded before you started — it is **not** in your local folder and must remain untouched after deployment. Your job is to lay out three new scripts locally and deploy them with `wmill sync push --yes` **without destroying the pre-existing remote script**.

## Background: the destructive-sync trap
`wmill sync push --yes` is stateless and destructive: anything present on the remote workspace inside the configured `includes:` scope that is **not** present locally will be deleted on push. The verified way to preserve remote-only assets is **NOT** the `keepDeleted` key (it does not exist on the current `wmill.yaml` schema). The supported mechanism is the `excludes:` glob list on `wmill.yaml`, which removes matching paths from both `pull` and `push` scope so the destructive diff never touches them. See https://www.windmill.dev/docs/advanced/cli/sync#wmillyaml.

## Requirements
- Compute `SAFE_ID = ZEALT_RUN_ID.replace('-', '_')` (read `ZEALT_RUN_ID` from the environment). This is required because Windmill paths must use `[a-zA-Z0-9_]` segments and the cloud workspace is shared across concurrent runs.
- Lay out three new scripts under the run-id-scoped folder `f/gitops_${SAFE_ID}/`:
  - `f/gitops_${SAFE_ID}/alpha.ts` — TypeScript (Bun) script.
  - `f/gitops_${SAFE_ID}/beta.ts` — TypeScript (Bun) script.
  - `f/gitops_${SAFE_ID}/gamma.py` — Python 3 script.
  Each script must export/define a `main(message: string)` (or `def main(message: str)` for Python) entry point that returns the JSON object `{"script": "<alpha|beta|gamma>", "echo": message}`.
- Provide the matching script-metadata file for each script (`alpha.script.yaml`, `beta.script.yaml`, `gamma.script.yaml`) so that `wmill sync push` recognises each pair as a deployable script asset.
- Update `/home/user/myproject/wmill.yaml` so that:
  - `includes:` still covers `f/**` (the existing default).
  - `excludes:` is a YAML list containing a glob that matches the pre-existing remote script path `f/gitops_${SAFE_ID}/legacy.ts` (for example `f/gitops_${SAFE_ID}/legacy.*` or the exact path `f/gitops_${SAFE_ID}/legacy.ts`).
- Deploy by running `wmill sync push --yes` from `/home/user/myproject`. After the push completes, the remote workspace must contain all three new scripts AND still contain the pre-existing `f/gitops_${SAFE_ID}/legacy.ts`.

## Implementation Hints
- **The verified preservation mechanism is `excludes:`, not `keepDeleted`.** The `keepDeleted` key does NOT exist on the current `wmill.yaml` schema (verified against https://www.windmill.dev/docs/advanced/cli/sync#wmillyaml and `wmill config`). Use the `excludes:` glob list instead — paths matched by `excludes:` are removed from sync scope on both pull and push, so destructive `push` cannot delete them.
- `wmill init` already created a default `wmill.yaml` with `includes: ['f/**']` and `excludes: []`. You only need to append your `excludes:` glob, not regenerate the file.
- Each script file needs a sibling `<name>.script.yaml` metadata file. The minimum viable metadata is just `summary:` and `description:` strings (and `lock: ""` is acceptable). The `defaultTs: bun` setting in `wmill.yaml` is what tells the CLI that `.ts` files are Bun scripts; the language for `.py` is inferred from the extension.
- The three new scripts are simple echo scripts: take a `message` argument and return `{"script": "<name>", "echo": message}`. No Windmill SDK calls are required.
- The pre-seeded `legacy.ts` was uploaded directly to the cloud workspace via the Windmill REST API; it has no on-disk counterpart inside `/home/user/myproject`. That is exactly the situation the `excludes:` glob is designed to protect.
- The workspace profile `evaluation-ws` is already registered (pointing at `https://app.windmill.dev` with the correct `WINDMILL_WORKSPACE` and `WINDMILL_TOKEN`). You do not need to run `wmill workspace add` yourself; just `cd /home/user/myproject` and use `wmill` commands directly.
- After the agent finishes, also write the final deployed run-scoped folder path and the literal `excludes:` glob you used into `/home/user/myproject/output.log` so the verifier can correlate the run.

## Acceptance Criteria
- Project path: /home/user/myproject
- The agent must actually run `wmill sync push --yes` from `/home/user/myproject` (the verifier checks remote state via the REST API; no local-only fake will pass).
- Log file: /home/user/myproject/output.log
  - Must contain a line of the form: `Deployed folder: f/gitops_<SAFE_ID>`
  - Must contain a line of the form: `Excludes glob: <pattern>` where `<pattern>` is the literal value placed in `excludes:` that matches `f/gitops_<SAFE_ID>/legacy.ts`.
- Local files that must exist under `/home/user/myproject` (where `<SAFE_ID>` = `ZEALT_RUN_ID` with `-` replaced by `_`):
  - `f/gitops_<SAFE_ID>/alpha.ts` with its sibling `alpha.script.yaml`
  - `f/gitops_<SAFE_ID>/beta.ts` with its sibling `beta.script.yaml`
  - `f/gitops_<SAFE_ID>/gamma.py` with its sibling `gamma.script.yaml`
- Local `wmill.yaml` constraints (parsed as YAML, not regex on the raw bytes):
  - The top-level `excludes:` key MUST be a list.
  - At least one entry in the list MUST match the path `f/gitops_<SAFE_ID>/legacy.ts` when interpreted as a glob (e.g. `f/gitops_<SAFE_ID>/legacy.*` or the exact path `f/gitops_<SAFE_ID>/legacy.ts`).
- Remote (cloud) workspace state after `wmill sync push --yes`, verified through the documented REST endpoint `GET /api/w/{workspace}/scripts/get/p/{path}` against `https://app.windmill.dev`:
  - `f/gitops_<SAFE_ID>/alpha` → returns 200 (deployed by the agent).
  - `f/gitops_<SAFE_ID>/beta` → returns 200 (deployed by the agent).
  - `f/gitops_<SAFE_ID>/gamma` → returns 200 (deployed by the agent).
  - `f/gitops_<SAFE_ID>/legacy` → returns 200 (still present, proving `excludes:` protected it).
- Runtime invocation: `wmill script run f/gitops_<SAFE_ID>/alpha -d '{"message": "<probe>"}'` from `/home/user/myproject` MUST succeed (exit 0) and emit a JSON result of shape `{"script": "alpha", "echo": "<probe>"}`.

