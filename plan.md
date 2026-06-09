## 1. Library Overview

- **Description**: Windmill is an open-source, self-hostable workflow engine and developer platform for building internal tools, automations, data pipelines, and AI agents. It combines an efficient multi-language execution runtime (TypeScript, Python, Go, PHP, Bash, SQL, Rust, Ruby, R, C#, Java, and arbitrary Docker images) with a visual flow editor, a low-code app builder, and a "workflows-as-code" SDK. It positions itself as a unified alternative to Retool, n8n, Airflow, Prefect, Kestra, and Temporal.

- **Ecosystem Role**: Windmill sits as the orchestration and internal-tooling layer of a modern stack. It plugs into databases (Postgres, MySQL, BigQuery, Snowflake, DuckDB), object storage (S3/R2/MinIO/Azure Blob/GCS), messaging (Kafka, NATS, MQTT, SQS, GCP Pub/Sub, Azure Event Grid), chat (Slack, Teams, Discord), and AI providers (OpenAI, Anthropic, Mistral, Gemini, DeepSeek, Groq, etc.). Code is authored either in the web IDE or locally via the `wmill` CLI / VS Code extension and version-controlled in Git.

- **Project Setup**:
  1. **Install the CLI** (requires Node ≥ 20):
     ```bash
     npm install -g windmill-cli
     ```
  2. **Authenticate against an instance** (cloud or self-hosted, in this case, only use the cloud version):
     ```bash
     wmill workspace add my-ws my-ws https://app.windmill.dev
     # follow the prompt to paste a Bearer token created in Account Settings
     ```
  3. **Bootstrap a local workspace folder** (generates a fully commented `wmill.yaml` and binds the active profile):
     ```bash
     wmill init
     ```
  4. **Pull existing scripts / flows / apps**:
     ```bash
     wmill sync pull --yes
     ```
  5. **Author code**. Each script lives in a pair of files, e.g.:
     - `f/my_folder/hello.ts` (or `.py`, `.go`, …) — the entry point with a `main` function.
     - `f/my_folder/hello.script.yaml` — metadata (summary, description, schema, runtime, triggers).
  6. **Run, preview, and deploy** from the CLI:
     ```bash
     wmill script run f/my_folder/hello -d '{"name":"Wei"}'
     wmill dev                 # live local preview against the workspace
     wmill sync push --yes     # deploy the local folder to the workspace
     ```

## 2. Core Primitives & APIs

### 2.1 Scripts

A Windmill script is a single function (`main` for Python / `export async function main` for TypeScript) whose typed signature is parsed into a JSON Schema, an auto-generated form, and a pair of webhooks (sync + async).

- Docs: [Scripts quickstart (TypeScript)](https://www.windmill.dev/docs/getting_started/scripts_quickstart/typescript), [Scripts quickstart (Python)](https://www.windmill.dev/docs/getting_started/scripts_quickstart/python), [JSON schema and parsing](https://www.windmill.dev/docs/core_concepts/json_schema_and_parsing).

TypeScript (Bun) script with typed args, a Resource, and a Windmill-specific type:
```typescript
// boilerplate adapted from the official TS quickstart
import * as wmill from "windmill-client"

type Postgresql = {
  host: string
  port: number
  user: string
  dbname: string
  sslmode: string
  password: string
}

export async function main(
  a: number,
  b: "my" | "enum",
  pg: Postgresql,
  email: wmill.Email,
  sql: wmill.Sql,
  e = "inferred type string from default arg",
  variant:
    | { label: "Variant 1"; foo: string }
    | { label: "Variant 2"; bar: number }
) {
  const token = await wmill.getVariable("u/user/foo")
  return { ok: true, a, b, host: pg.host, variant, token }
}
```
Each `main` argument becomes a form field; `wmill.Email` / `wmill.Sql` are type hints that give the field a rich editor; the union type renders as a discriminated `oneOf` selector.

Python script with Pydantic input, secret access, and persistent state (verbatim style of the Python quickstart):
```python
import os
import wmill
from pydantic import BaseModel
from typing import Optional, List

class Address(BaseModel):
    street: str
    city: str
    zip_code: Optional[str] = None

class User(BaseModel):
    name: str
    age: int
    addresses: List[Address] = []

def main(user: User, file_: bytes = bytes(0)):
    try:
        secret = wmill.get_variable("f/examples/secret")
    except Exception:
        secret = "No secret yet at f/examples/secret"

    last_state = wmill.get_state()
    new_state = {"calls": 1} if last_state is None else {**last_state, "calls": last_state["calls"] + 1}
    wmill.set_state(new_state)

    return {"name": user.name, "user": os.environ.get("WM_USERNAME"), "secret": secret, "state": new_state}
```
Pydantic / `@dataclass` types are inspected to build nested forms; `wmill.get_variable` and `wmill.get_state` use the implicit `WM_TOKEN` env var the worker injects.

Backend schema validation can be enforced with a top-of-file annotation:
```typescript
// schema_validation
export async function main(a: number, b: "my" | "enum") {
  return { a, b }
}
```
With `schema_validation`, the worker rejects calls whose payload does not match the inferred JSON Schema (types, enums, required, `oneOf` shape).

### 2.2 Resources & Resource Types

A **Resource Type** is a JSON-Schema describing a structured object (DB credentials, API keys, …). A **Resource** is an instance of that type. Resources can embed `$var:...` (secret variable) or `$res:...` (another resource) placeholders, resolved with the caller's permissions.

- Docs: [Resources and types](https://www.windmill.dev/docs/core_concepts/resources_and_types).

Pass a typed resource as a parameter (preferred):
```typescript
type Postgresql = {
  host: string
  port: number
  user: string
  dbname: string
  sslmode: string
  password: string
  root_certificate_pem: string
}

export async function main(postgres: Postgresql) {
  // Windmill UI will show a select of resources whose resource_type is "postgresql"
  return { db: postgres.dbname, host: postgres.host }
}
```
The parameter type name (CamelCase ⇒ snake_case) must match a `resource_type` registered in the workspace.

Fetch a resource imperatively:
```typescript
import * as wmill from "windmill-client"

export async function main() {
  const slack = await wmill.getResource("u/user/my_slack")
  return { token_prefix: slack.token.slice(0, 4) }
}
```
```python
import wmill
def main():
    cfg = wmill.get_resource("u/user/my_db")
    return cfg["host"]
```

Resource values can interpolate other resources / variables:
```yaml
# inside a resource value
host: db.internal
user: app
password: $var:f/devops/db_password
mirror: $res:f/devops/replica_db
job_id: $WM_JOB_ID
```
Only `$var:`, `$res:`, and `$WM_*` are interpolated inside resource values; arbitrary `$FOO` strings are returned as-is.

### 2.3 Variables & Secrets

User-defined variables are encrypted at rest with a workspace key; "secret" variables are masked in job logs and auditable via `variables.decrypt_secret` events.

- Docs: [Variables and secrets](https://www.windmill.dev/docs/core_concepts/variables_and_secrets).

```python
import wmill
def main():
    token = wmill.get_variable("u/user/foo")
    wmill.set_variable("u/user/foo", token + "-rotated")
    return "ok"
```
```typescript
import * as wmill from "windmill-client"
export async function main() {
  const v = await wmill.getVariable("u/user/foo")
  await wmill.setVariable("u/user/foo", `${v}-rotated`)
  return v
}
```
Passing a variable via the UI uses an indirect reference `$var:u/user/foo` that the worker resolves at execution time using the caller's permissions; the same mechanism works for arrays / nested objects up to depth 2.

Contextual variables are injected as env vars on every job: `WM_TOKEN`, `WM_WORKSPACE`, `WM_JOB_ID`, `WM_USERNAME`, `WM_EMAIL`, `BASE_INTERNAL_URL`, etc.

### 2.4 States & Flow User States

`state` is a per-`(script, user, schedule)` resource that survives across executions; `flow user state` is scoped to one flow run.

- Docs: [States](https://www.windmill.dev/docs/core_concepts/resources_and_types#states).

Persistent state across runs (classic "watch the temperature" example):
```python
import requests
from wmill import get_state, set_state

def main():
    last = get_state()
    new = requests.get("http://wttr.in/Paris?format=%t").text.strip("°F")
    set_state(new)
    if last is None:
        return "first run"
    return "increase" if new > last else "decrease" if new < last else "stable"
```

In-flow user state (lives only for the duration of the flow):
```typescript
import * as wmill from "windmill-client"
export async function main(x: string) {
  await wmill.setFlowUserState("FOO", 42)
  return await wmill.getFlowUserState("FOO")
}
```

### 2.5 Flows (visual editor)

Flows are DAGs of modules (raw scripts, workspace scripts, branches, loops, approval steps, …). They are stored as YAML and editable both in the web IDE and on disk.

- Docs: [Flow editor](https://www.windmill.dev/docs/flows/flow_editor), [Flow approval](https://www.windmill.dev/docs/flows/flow_approval), [Retries](https://www.windmill.dev/docs/flows/retries).

Real flow YAML (excerpt from the dynamic-enum approval tutorial in the docs):
```yaml
summary: ""
value:
  modules:
    - id: a
      summary: Approval step with dynamic enum
      value:
        type: rawscript
        language: bun
        content: |
          import * as wmillClient from "windmill-client"
          export async function main() {
            const customers = ["New York","Los Angeles","Chicago"]
            const resumeUrls = await wmillClient.getResumeUrls("approver1")
            return {
              resume: resumeUrls["resume"],
              enums: { "Customers to send to": customers },
              default_args: { "Customers to send to": customers },
            }
          }
        input_transforms: {}
        is_trigger: false
      continue_on_error: false
      suspend:
        required_events: 1
        timeout: 1800
        hide_cancel: false
        resume_form:
          schema:
            properties:
              Customers to send to:
                items: { type: string }
                type: array
            required: []
            order: ["Customers to send to"]
    - id: b
      summary: Use the selected arguments
      value:
        type: rawscript
        language: python3
        content: |
          def main(x):
              return x
        input_transforms:
          x:
            type: javascript
            expr: resume["Customers to send to"]
        is_trigger: false
  same_worker: false
schema:
  $schema: https://json-schema.org/draft/2020-12/schema
  properties: {}
  required: []
  type: object
```
Each module declares `value` (what to run), `input_transforms` (how to wire previous step outputs into args), and optional `suspend` / `retry` / `continue_on_error` / `sleep` / `cache_ttl` settings.

### 2.6 Workflows as Code (WAC)

WAC lets you write the orchestration in pure TS/Python; Windmill uses a checkpoint/replay model so the parent fully suspends between every primitive (zero worker waste during sleeps / approvals).

- Docs: [Workflows as code](https://www.windmill.dev/docs/core_concepts/workflows_as_code).

Quickstart (TypeScript) — every primitive in ~20 lines (verbatim from the docs):
```typescript
import { task, step, workflow, sleep, parallel } from "windmill-client"

async function fetchData(url: string) {
  const resp = await fetch(url)
  return resp.json()
}
async function transform(data: any) {
  return { count: data.length, summary: data.slice(0, 5) }
}
async function notify(message: string) {
  console.log(`Sending notification: ${message}`)
  return "sent"
}

export const main = workflow(async (url: string) => {
  const startedAt = await step("started_at", () => new Date().toISOString())
  const data = await task(fetchData)(url)
  const result = await task(transform)(data)
  await sleep(5)
  await task(notify)(`Processed ${result.count} items since ${startedAt}`)
  return result
})
```
`task()` runs each function as its own Windmill job; `step()` is an inline checkpoint for non-deterministic values (timestamps, UUIDs); `sleep()` suspends the workflow without holding a worker; `parallel()` fans out work with optional concurrency control.

Python equivalent with the decorator API:
```python
from wmill import workflow, task, step, sleep, parallel
import datetime, uuid

@task
async def fetch_data(url: str):
    import urllib.request, json
    return json.loads(urllib.request.urlopen(url).read())

@task(tag="gpu", timeout=600)
async def transform(data):
    return {"count": len(data), "summary": data[:5]}

@workflow
async def main(url: str):
    started_at = await step("started_at", lambda: datetime.datetime.utcnow().isoformat())
    run_id = await step("run_id", lambda: str(uuid.uuid4()))
    data = await fetch_data(url)
    result = await transform(data)
    await sleep(5)
    return {"run_id": run_id, "started_at": started_at, **result}
```

Parallelism via `Promise.all` or `parallel()` with concurrency:
```typescript
import { task, parallel, workflow } from "windmill-client"
async function processItem(item: number) { return item * 2 }
export const main = workflow(async () => {
  const items = [1,2,3,4,5,6,7,8,9,10]
  const all = await parallel(items, (i) => task(processItem)(i))
  const batched = await parallel(items, (i) => task(processItem)(i), { concurrency: 3 })
  return { all, batched }
})
```

Approval gate + `getResumeUrls()` + scheduled retry with exponential backoff (combined from the docs' deployment-with-approval and scheduled-retry examples):
```typescript
import {
  task, step, workflow, sleep, waitForApproval, getResumeUrls
} from "windmill-client"

async function runTests(branch: string) { return { passed: 42, failed: 0 } }
async function deployToProduction(branch: string) { return { url: "https://example.com" } }
async function callExternalApi(payload: any) {
  const r = await fetch("https://api.example.com/submit", { method: "POST", body: JSON.stringify(payload) })
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

export const main = workflow(async (branch: string, payload: any, maxRetries = 3) => {
  const tests = await task(runTests)(branch)
  if (tests.failed > 0) return { status: "failed", tests }

  const urls = await step("approval_urls", () => getResumeUrls())
  await step("notify", () => console.log(`Approve at ${urls.approvalPage}`))

  const approval = await waitForApproval({ timeout: 86_400, selfApproval: false })
  if (!approval.approved) return { status: "rejected", approver: approval.approver }

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await task(callExternalApi)(payload)
      break
    } catch (e) {
      if (attempt === maxRetries) throw e
      await sleep(30 * Math.pow(2, attempt - 1)) // 30s, 60s, 120s — zero worker usage
    }
  }
  return await task(deployToProduction)(branch)
})
```

Branches via standard `try/catch` (errors surface as `TaskError` in Python with `step_key`, `child_job_id`, `result`):
```typescript
import { task, workflow } from "windmill-client"
async function risky(d: string) { if (d === "bad") throw new Error("nope"); return d }
async function fallback(msg: string) { return `fallback: ${msg}` }
export const main = workflow(async (d: string) => {
  try { return await task(risky)(d) }
  catch (e: any) { return await task(fallback)(e.message) }
})
```

Dispatch to existing scripts and flows by path:
```typescript
import { taskScript, taskFlow, workflow } from "windmill-client"
export const main = workflow(async () => {
  const data = await taskScript("f/data_team/extract_users")({ limit: 100 })
  const r    = await taskFlow("f/data_team/etl_pipeline")({ data })
  const heavy = await taskScript("f/ml/train_model", { timeout: 3600, tag: "gpu" })({ dataset: data })
  return { r, heavy }
})
```

Per-task options accepted by `task()` / `taskScript()` / `taskFlow()`: `timeout`, `tag`, `cache_ttl`, `priority`, `concurrency_limit`, `concurrency_key`, `concurrency_time_window_s`.

### 2.7 Apps (low-code)

Low-code apps wire **components** (inputs, tables, buttons, charts) to **runnables** (background scripts, click handlers, frontend scripts). They expose four output namespaces — `ctx`, `state`, `<component_id>`, `bg_*` — that can be referenced in connection expressions.

- Docs: [App editor](https://www.windmill.dev/docs/apps/app_editor), [Resources in apps](https://www.windmill.dev/docs/core_concepts/resources_and_types#resources-in-apps).

A typical click handler runnable wired to a `text_input` and a `button` component:
```typescript
// click handler for the "send" button; reads from the text_input component
import * as wmill from "windmill-client"

type SlackRes = { token: string }

export async function main(slack: SlackRes, channel: string, message: string) {
  const { WebClient } = await import("@slack/web-api")
  const web = new WebClient(slack.token)
  await web.chat.postMessage({ channel, text: message })
  return { sent: true }
}
```
Connect the runnable's `message` input to `text_input.value` via the eval expression `text_input.value`, and connect `channel` to a static literal. The Slack resource is provided through a static **Resource select** component (whitelisted by the app's auto-generated policy).

App definitions are stored on disk under `<path>__app/` (or `<path>.app/` with `nonDottedPaths: false`); runnables can be inline scripts or workspace scripts.

### 2.8 Triggers

A trigger is any external mechanism that enqueues a job. Every script/flow exposes auto-generated webhook URLs; additionally, dedicated trigger objects can be created for schedules, HTTP routes, websockets, Postgres logical replication, Kafka, NATS, SQS, MQTT, GCP Pub/Sub, Azure Event Grid, email (SMTP), Nextcloud, and Google Drive/Calendar.

- Docs: [Triggers overview](https://www.windmill.dev/docs/getting_started/triggers), [Webhooks](https://www.windmill.dev/docs/core_concepts/webhooks), [Scheduling](https://www.windmill.dev/docs/core_concepts/scheduling).

**Schedules (cron)** use Hexagon's `croner` extension to Unix cron — first field is optional seconds; supports `L`, `W`, `#`, name ranges (`MON-FRI`), etc.

```text
0 0 12 * * MON-FRI   # every weekday at noon
0 0 12 ? * 5#3       # every third Friday of the month at noon
0 0 12 15W * ?       # closest weekday to the 15th of every month at noon
0 0 */3 ? * *        # every three hours
```
Each schedule can have its own error handler, recovery handler, and a "dynamic skip" validator:
```typescript
// dynamic-skip validator: skip weekends and holidays
export async function main(scheduled_for: string): Promise<boolean> {
  const d = new Date(scheduled_for)
  if (d.getUTCDay() === 0 || d.getUTCDay() === 6) return false
  const holiday = await fetch(`https://api.example.com/holidays?date=${scheduled_for}`).then(r => r.json())
  return !holiday.is_holiday
}
```

**Webhooks** are auto-generated per script/flow:
```bash
# async (returns the job uuid)
curl -X POST "$URL/api/w/demo/jobs/run/p/u/bot/hello_world" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  --data '{"name":"Wei"}'

# sync (waits for the result)
curl -X POST "$URL/api/w/demo/jobs/run_wait_result/p/u/bot/hello_world" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  --data '{"name":"Wei"}'
```
Non-object payloads are wrapped under `body`; `?wrap_body=true` forces the wrap; `?raw=true` adds a `raw_string` arg for signature verification; `?include_header=X-Sign,foo` and `?include_query=a,b` add request headers/query as args. The script can customize the response by returning `wm_status_code`, `wm_content_type`, and `wm_headers`.

**HTTP routes** let you mount a script at a custom path (`/api/r/payment/webhook`) with method and auth options. **WebSocket triggers** subscribe to an upstream WS server and dispatch each message as a job. **Postgres triggers** use logical replication to react to INSERT/UPDATE/DELETE on selected tables/schemas. **Kafka/NATS/SQS/MQTT/GCP/Azure** triggers all run as long-lived connectors that enqueue a job per message and can be transformed by a **preprocessor** script before reaching the main runnable.

Form-data webhook with file upload:
```typescript
import { S3Object } from "windmill-client"
export async function main(mytextfield: string, myfilefield: S3Object[]) {
  return { name: myfilefield[0].s3, text: mytextfield }
}
```

### 2.9 Error Handling, Approvals, Suspends, Retries

- Docs: [Error handling](https://www.windmill.dev/docs/core_concepts/error_handling), [Flow approval](https://www.windmill.dev/docs/flows/flow_approval), [Retries](https://www.windmill.dev/docs/flows/retries).

In-script `try/catch` is the simplest layer:
```typescript
export async function main() {
  try {
    const r = await fetch("https://api.example.com/data")
    return await r.json()
  } catch (error) {
    return { error: "fetch failed", details: String(error) }
  }
}
```

Throwing a Windmill-rendered error from a script:
```javascript
return { error: { name: "418", message: "I'm a teapot", stack: "Error: I'm a teapot" } }
```

Workspace-level / trigger-level custom error handlers receive a documented payload:
```typescript
// custom workspace error handler
export async function main(
  workspace_id: string, job_id: string, path: string,
  is_flow: boolean, started_at: string, email: string,
  schedule_path?: string
) {
  const kind = is_flow ? "flow" : "script"
  console.log(`Workspace error: ${kind} ${path} (${job_id}) by ${email}`)
  return { handled: true, workspace_id, job_id }
}
```
```typescript
// trigger-specific error handler (e.g. for an HTTP route)
export async function main(
  error: object, path: string, is_flow: boolean, trigger_path: string,
  workspace_id: string, email: string, job_id: string, started_at: string
) {
  return { trigger_path, error }
}
```

A flow approval step is a normal script with the **Suspend** option enabled. It uses `getResumeUrls` to produce per-recipient secret URLs:
```typescript
import * as wmill from "windmill-client"
export async function main(approver?: string) {
  const urls = await wmill.getResumeUrls(approver)
  return {
    resume: urls.resume,    // single-click approve URL
    cancel: urls.cancel,    // single-click reject URL
    default_args: {},
    enums: {},
    description: { render_all: [{ markdown: "**Approve to continue**" }] },
  }
}
```
Flow-level pre-approvals (`flowLevel: true` / `flow_level=True`) let one step grant resume permission that any later suspend step in the same flow can consume.

Retries (configured via the `Advanced > Retries` panel; reflected in the flow YAML):
```yaml
retry:
  constant:
    attempts: 5
    seconds: 30
  exponential:
    attempts: 4
    multiplier: 2
    seconds: 3   # delay = multiplier * seconds ^ attempt
```

### 2.10 AI agents

AI agents are a first-class flow step that calls an LLM with system + user prompts, optional tools (workspace scripts, hub scripts, inline scripts, MCP servers, web search, nested agents), and structured output via a JSON schema.

- Docs: [AI agents](https://www.windmill.dev/docs/core_concepts/ai_agents).

Manual-memory message format (OpenAI-compatible):
```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "search_docs", "arguments": "{\"q\":\"retry\"}"}}]
}
```

Streaming payloads emitted over SSE webhooks:
```json
{ "type": "token_delta", "content": "Hello" }
{ "type": "tool_call",        "call_id": "c1", "function_name": "search_docs", "function_arguments": "{...}" }
{ "type": "tool_execution",   "call_id": "c1", "function_name": "search_docs" }
{ "type": "tool_result",      "call_id": "c1", "function_name": "search_docs", "result": "...", "success": true }
```

### 2.11 CLI (`wmill`)

- Docs: [CLI overview](https://www.windmill.dev/docs/advanced/cli), [Sync](https://www.windmill.dev/docs/advanced/cli/sync), [wmill.yaml reference](https://www.windmill.dev/docs/advanced/cli/wmill-yaml-reference).

Common commands:
```bash
# workspace setup
wmill workspace add prod prod https://app.windmill.dev
wmill workspace switch prod

# bootstrap local repo
wmill init                        # writes a commented wmill.yaml + binds workspace
wmill sync pull --yes             # download workspace state
wmill sync push --yes --message "deploy: refactor"

# unified item subcommands (every type supports list/get/new)
wmill script list --json | jq '.[].path'
wmill resource get f/db/prod --json | jq .value.host
wmill trigger new f/http/webhook --kind http
wmill flow new f/etl/my_flow

# run / preview a script
wmill script run f/my_folder/hello -d '{"name":"Wei"}'
wmill script preview f/my_folder/hello
wmill dev                         # live local preview with hot reload
wmill docs "how do I create a flow?"   # EE only: doc search
```

Sample `wmill.yaml` (multi-workspace, env-aware):
```yaml
defaultTs: bun
includes: ["f/**"]
excludes: []
skipSecrets: true
includeSchedules: false
includeTriggers: false

workspaces:
  staging:
    baseUrl: https://staging.windmill.dev
    overrides:
      includeSchedules: true
  production:
    baseUrl: https://app.windmill.dev
    workspaceId: prod-ws
    gitBranch: main
    overrides:
      skipSecrets: false
    promotionOverrides:
      skipApps: true
      skipFlows: true
    specificItems:
      resources: ["u/alex/prod_*"]
      variables: ["u/alex/env_*"]
  commonSpecificItems:
    resources: ["u/alex/config/**"]
    folders:  ["f/env_*"]
    settings: true
```
`wmill sync` resolves the active workspace via `--workspace`, then the current git branch, then the active local profile.

## 3. Real-World Use Cases & Templates

- **Parallel ETL with retries and structured output** — fan out API extraction with `parallel()`, transform with bounded concurrency, load in a single batch ([ETL example](https://www.windmill.dev/docs/core_concepts/workflows_as_code#etl-pipeline-with-retry)).
- **Human-in-the-loop deploys** — test → deploy to staging → Slack-notify with `getResumeUrls()` → `waitForApproval({ timeout: 86400, selfApproval: false })` → deploy to prod ([Deployment with approval gate](https://www.windmill.dev/docs/core_concepts/workflows_as_code#deployment-with-approval-gate)).
- **Refund-request triage** — manual flow trigger, interactive Slack approval, predicate-based `branchone` to refund / refuse / investigate ([Slack-approval tutorial](https://www.windmill.dev/docs/flows/flow_approval#tutorial-a-slack-approval-step-conditioning-flow-branches)). Reference flow on the Hub: [hub.windmill.dev/flows/49](https://hub.windmill.dev/flows/49/).
- **Scheduled polls** — a "trigger script" + state + flow's "watch changes regularly" mode replaces external webhooks for sources without push (e.g. GitHub stars, HN top items).
- **AI Discord bot via WebSocket** — combined websocket trigger + Anthropic AI agent step ([Discord bot guide](https://www.windmill.dev/docs/misc/guides/discord_bot.md)).
- **Slack-driven internal tools** — wrap any script as a slash command via webhook + custom HTTP route ([Handler Slack commands blog](https://www.windmill.dev/blog/handler-slack-commands)).
- **Windmill Hub** — 200+ ready-made resource types, scripts, and flows at [hub.windmill.dev](https://hub.windmill.dev/) (Slack, OpenAI, GSheets, Postgres, Stripe, Linear, …).
- **Example git-sync repo** — [windmill-labs/windmill-sync-example](https://github.com/windmill-labs/windmill-sync-example) demonstrates a `wmill.yaml`-driven workflow.

## 4. Developer Friction Points

- **Determinism in WAC** — the workflow body replays from checkpoints, so any side-effectful or non-deterministic call (`Date.now()`, `Math.random()`, `os.getenv`, mutable globals, network reads that influence control flow) must be wrapped in `await step("key", fn)`. Re-deploying a workflow mid-run is detected via source-hash mismatch and forces a from-scratch replay ([Determinism requirement](https://www.windmill.dev/docs/core_concepts/workflows_as_code#determinism-requirement)).
- **Step IDs vs. task ordering** — both `step()` and `task()` are keyed by their call order; conditionally skipping a `step("foo")` in one branch but not another can shift keys and re-execute later steps. Stable, unique string keys per `step()` and a deterministic control-flow shape are required.
- **`get_state` vs `getFlowUserState`** — `get_state` / `set_state` persists across script runs at a path computed from `(script, flow, schedule, user)`; `getFlowUserState` is scoped to the current flow run only. Choosing the wrong one is a common source of "my counter resets every run" bugs ([States](https://www.windmill.dev/docs/core_concepts/resources_and_types#states)).
- **Resource scoping in low-code apps** — Apps run as the publisher, not the viewer. A runnable accepting a `Resource` argument that is sourced from anything other than a static **Resource select** component needs the "Resources from users allowed" toggle on the input's eval source, otherwise the worker returns permission-denied ([Resources in apps](https://www.windmill.dev/docs/core_concepts/resources_and_types#resources-in-apps)).
- **Webhook payload wrapping** — Non-JSON or non-object payloads are silently wrapped as `{ "body": <payload> }` unless the script expects `body: any`. Forgetting `?wrap_body=true` (or accepting the matching arg) leads to "missing required arg" errors ([Webhook body](https://www.windmill.dev/docs/core_concepts/webhooks#non-object-payload--body)).
- **CLI `sync` overwrite semantics** — `wmill sync push/pull` is **stateless and destructive**: items present in the target but not in the source are deleted on confirm. Secrets, schedules, and triggers are skipped by default (`skipSecrets`, `includeSchedules: false`, `includeTriggers: false`); users frequently lose schedules by re-running `sync push` after a fresh `init` without flipping these flags ([Sync](https://www.windmill.dev/docs/advanced/cli/sync)).
- **TypeScript runtime modes** — `//nobundling`, `//native`, `//nodejs`, `//npm` are top-of-file annotations that change runtime semantics. `//nodejs` and `//npm` are EE-only; `//native` skips bundling but disables many features ([TS modes](https://www.windmill.dev/docs/getting_started/scripts_quickstart/typescript#modes)).
- **Python version pinning** — Inferred from `# py: >=3.12` / `# py312` annotations; scripts deployed before any annotation default to Python 3.11 forever, even after `INSTANCE_PYTHON_VERSION` changes ([Python versions](https://www.windmill.dev/docs/getting_started/scripts_quickstart/python#select-python-version)).
- **Schema validation is opt-in** — Without the `// schema_validation` annotation, the worker accepts any payload shape and the script may crash at runtime instead of returning a clean 400 from the webhook.

## 5. Evaluation Ideas

**Simple**
1. Implement a TypeScript script with a typed `Postgresql` resource argument that returns the row count of a given table.
2. Build a Python script that uses `wmill.get_state` / `wmill.set_state` to track and return the number of times it has been executed.
3. Author a cron schedule using the new croner syntax (e.g. "every third Friday at 9 AM Europe/Paris") and attach it to an existing script.

**Medium**
4. Create a Workflow-as-Code that fans out HTTP GETs to a list of URLs with `parallel(..., { concurrency: 3 })` and aggregates `{ url, status }`.
5. Build a low-code app with a text input, a Resource-select for a Slack resource, and a button whose click runnable posts a message to a channel.
6. Add a `// schema_validation` script with a `oneOf` argument, a `wmill.Email` argument, and an enum, and verify rejection of malformed webhook payloads.
7. Implement a Postgres trigger that listens for `INSERT` events on `orders` and dispatches a notification flow with a preprocessor that drops events without `customer_id`.
8. Add an approval step with a dynamic-enum form to a flow and route the result through a `branchone` (refund vs. refuse vs. investigate).

**Complex**
9. Refactor a sequential visual Flow into a deterministic WAC script, correctly using `step()` for IDs/timestamps and `taskScript()` to call existing workspace scripts.
10. Implement a multi-stage deployment WAC with `runTests → deployStaging → waitForApproval(selfApproval=false) → exponential-backoff retry → deployProduction`, surfacing `getResumeUrls()` to Slack.
11. Build a `wmill.yaml` for a staging/production split with `promotionOverrides` and `specificItems`, then write a CI job that runs `wmill sync push --workspace production --promotion --yes`.
12. Compose an AI-agent flow that uses an MCP tool, a hub-script tool, and a nested AI agent, with `output_schema` enforcing a JSON contract and `streaming: true` exposed via the SSE webhook.

## 6. Sources

1. [Windmill — What is Windmill?](https://www.windmill.dev/docs/intro) — top-level overview of the platform's runtime, orchestrator, app builder, and CLI.
2. [Windmill `llms.txt`](https://www.windmill.dev/llms.txt) — single-file structured index of every docs page used to drive the rest of this research.
3. [TypeScript scripts quickstart](https://www.windmill.dev/docs/getting_started/scripts_quickstart/typescript) — Bun/Node/Deno modes, `main` signature, resource types, generated UI.
4. [Python scripts quickstart](https://www.windmill.dev/docs/getting_started/scripts_quickstart/python) — `wmill` client, Pydantic/dataclass inputs, Python version pinning.
5. [Workflows as code](https://www.windmill.dev/docs/core_concepts/workflows_as_code) — full API for `workflow()`, `task()`, `step()`, `sleep()`, `parallel()`, `waitForApproval()`, `taskScript()`, `taskFlow()`.
6. [Resources and types](https://www.windmill.dev/docs/core_concepts/resources_and_types) — resource types, `$var:` / `$res:` interpolation, States and Flow User States.
7. [Variables and secrets](https://www.windmill.dev/docs/core_concepts/variables_and_secrets) — encryption, secret masking, Vault/Azure/AWS backends, contextual env vars.
8. [JSON schema and parsing](https://www.windmill.dev/docs/core_concepts/json_schema_and_parsing) — Python/TS → JSON Schema mapping, `oneOf`, dynamic select, `schema_validation`.
9. [Flow editor](https://www.windmill.dev/docs/flows/flow_editor) — visual DAG, groups, node manipulation, subflows.
10. [Flow approval / suspend](https://www.windmill.dev/docs/flows/flow_approval) — suspend semantics, `getResumeUrls`, forms, default args, dynamic enums, Slack/Teams approvals.
11. [Retries](https://www.windmill.dev/docs/flows/retries) — constant vs. exponential, continue-on-error.
12. [Error handling](https://www.windmill.dev/docs/core_concepts/error_handling) — script `try/catch`, schedule/workspace/trigger error handlers, success handler, instance handler.
13. [Scheduling (cron)](https://www.windmill.dev/docs/core_concepts/scheduling) — croner syntax, primary vs. additional schedules, dynamic skip handler.
14. [Triggers overview](https://www.windmill.dev/docs/getting_started/triggers) — every trigger kind in one page (webhooks, HTTP, WS, Postgres, Kafka, NATS, SQS, MQTT, GCP, Azure, email, native).
15. [Webhooks](https://www.windmill.dev/docs/core_concepts/webhooks) — sync vs. async, body wrapping, `wm_status_code` / `wm_content_type`, SSE stream webhooks.
16. [App editor](https://www.windmill.dev/docs/apps/app_editor) — components, runnables panel, outputs (`ctx`/`state`/component/bg).
17. [AI agents](https://www.windmill.dev/docs/core_concepts/ai_agents) — providers, tools (script/hub/MCP/web search/nested), streaming events, chat mode.
18. [CLI (`wmill`)](https://www.windmill.dev/docs/advanced/cli) — unified `list/get/new`, `wmill docs`, AI-assistant integration.
19. [Sync (`wmill sync`)](https://www.windmill.dev/docs/advanced/cli/sync) — `wmill.yaml` schema, workspace bindings, promotion overrides, instance cloning.
20. [Windmill Hub](https://hub.windmill.dev/) — community repo of resource types, scripts, flows, and approval helpers referenced throughout the docs.
21. [Windmill OpenAPI](https://app.windmill.dev/openapi.html) — REST API reference for `run_wait_result`, `getJob`, resume endpoints, etc.
