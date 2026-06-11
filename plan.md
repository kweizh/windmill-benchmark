## 1. Library Overview

- **Description**: Windmill is an open-source, self-hostable workflow engine and developer platform designed for programmatically building internal tools, automations, data pipelines, and AI agents. It pairs an asynchronous, multi-language execution runtime (TypeScript/Bun, Python, Go, Rust, PHP, Bash, SQL, Ruby, R, C#, Java, and arbitrary Docker images) with a "workflows-as-code" (WAC) SDK and headless API infrastructure. While it offers visual options, its architecture treats code, configurations, and user interfaces as declarative, version-controlled assets, positioning itself as a highly hackable alternative to Temporal, Prefect, Airflow, and Retool.

- **Ecosystem Role**: Windmill operates as the orchestration, state, and serverless compute layer. It natively integrates with relational databases, object storage (S3/R2/MinIO), message brokers (Kafka, NATS, MQTT), and AI endpoints. For modern full-stack headless architectures, Windmill introduces two major structural layers:
  1. **Built-in Data Tables**: An integrated PostgreSQL instance isolated per workspace, removing external DB management overhead for persistence.
  2. **Worker Tag Routing**: A decoupled architecture where state and queues are managed via Postgres, allowing independent workers to be deployed across varying environments (e.g., GPU nodes, private intranets, edge locations) and targeted dynamically using infrastructure tags.
  Code, UIs, and schemas are authored locally via the `wmill` CLI or VS Code extension and synchronized directly with the workspace via Git or CI/CD pipelines.

- **Project Setup**:
  1. **Install the CLI** (requires Node ≥ 20):
     ```bash
     npm install -g windmill-cli
     ```
  2. **Authenticate against an instance** (using the cloud runtime for evaluation):
     ```bash
     wmill workspace add evaluation-ws evaluation-ws [https://app.windmill.dev](https://app.windmill.dev)
     # Follow prompt to input the Bearer API token generated in Account Settings
     ```
  3. **Bootstrap a local workspace folder** (creates a declarative `wmill.yaml` configuration):
     ```bash
     wmill init
     ```
  4. **Pull existing workspace configurations and assets**:
     ```bash
     wmill sync pull --yes
     ```
  5. **Author assets code-first**. Scripts reside as file pairs on disk:
     - `f/my_folder/task.ts` (or `.py`, `.rs`, `.go`) — executable script entrypoint.
     - `f/my_folder/task.script.yaml` — script metadata, schema constraints, and runtime settings.
  6. **Programmatic execution and deployment via CLI**:
     ```bash
     wmill script run f/my_folder/task -d '{"param": 100}'
     wmill dev                 # Hot-reloading local preview server against cloud workers
     wmill sync push --yes     # Destructive stateless push of local folder state to instance
     ```

---

## 2. Core Primitives & APIs

### 2.1 Scripts & Language Support
A Windmill script maps a typed function signature directly into an executable JSON Schema and high-throughput sync/async webhooks. Along with TypeScript (Bun) and Python, system languages like **Rust** and **Go** are supported as first-class primitives, compiling code directly on the worker with aggressive dependency and binary caching.

- **TypeScript (Bun) Script with Specialized Types**:
```typescript
import * as wmill from "windmill-client"

type Postgresql = {
  host: string;
  port: number;
  user: string;
  dbname: string;
  sslmode: string;
}

// Top-of-file annotation forces strict backend JSON schema validation
// schema_validation
export async function main(
  a: number,
  pg: Postgresql,
  email: wmill.Email,
  variant: { label: "v1"; foo: string } | { label: "v2"; bar: number }
) {
  const secretToken = await wmill.getVariable("u/user/api_key")
  return { success: true, host: pg.host, variant, secretToken }
}
```

- **Python Script with Input Validation and State Tracking**:
```python
import os
import wmill
from pydantic import BaseModel

class Payload(BaseModel):
    metric: str
    value: float

def main(data: Payload):
    # Fetching instance variables using internal tokens
    secret = wmill.get_variable("f/security/token")

    # State persists across atomic script executions
    last_state = wmill.get_state()
    new_state = {"runs": 1} if last_state is None else {**last_state, "runs": last_state["runs"] + 1}
    wmill.set_state(new_state)

    return {"status": "processed", "state": new_state, "worker_user": os.environ.get("WM_USERNAME")}
```

- **Rust Script (System Native Execution)**:
```rust
// Native dependencies are specified via inline annotations or standard cargo structures
// // [dependencies]
// // serde_json = "1.0"

use serde_json::{json, Value};

pub fn main(name: String, threshold: i32) -> Value {
    println!("Executing headless Rust task for: {}", name);
    json!({ "status": "ok", "computed": threshold * 2, "target": name })
}
```

### 2.2 Resources & Resource Types
Resources are JSON-Schema instances defining structured environments (credentials, tokens, connections). They evaluate references dynamically using internal authorization tokens.
```typescript
// Fetching a registered database resource imperatively within code
import * as wmill from "windmill-client"

export async function main() {
  const dbConfig = await wmill.getResource("f/infrastructure/prod_replica")
  return { endpoint: dbConfig.host }
}
```
Resource declarations on disk support parameter injection (`$var:...`, `$res:...`, `$WM_JOB_ID`) resolved at runtime by the executing worker.

### 2.3 Built-In Data Tables & Database Studio
Each workspace provides a zero-config, native PostgreSQL instance. This acts as a headless relational data store directly integrated into the asset pipeline, accessible via direct client APIs and visualized via the browser-based Database Studio.
```python
import wmill

def main():
    # Instantiates an implicit client to the internal workspace database
    db = wmill.datatable()

    # Type-safe execution with runtime schema checking
    query = "SELECT id, status FROM orders WHERE processing = $1"
    results = db.query(query, True).fetch_all()

    return {"count": len(results), "records": results}
```

### 2.4 Variables & Secrets
Variables are encrypted strings stored at rest. Secrets are masked automatically in job logs, preventing credential leaks during automated CI/CD runs and programmatic execution traces.
```typescript
import * as wmill from "windmill-client"
export async function main() {
  const currentToken = await wmill.getVariable("f/auth/session_token")
  // Rotate via API
  await wmill.setVariable("f/auth/session_token", `${currentToken}_rotated`)
}
```

### 2.5 Workflows as Code (WAC)
WAC replaces graphic DAG tools with pure programmatic orchestration in TypeScript or Python. Using an event-driven checkpoint/replay model, the master workflow execution completely suspends its worker thread whenever a `sleep`, `waitForApproval`, or nested subtask executes—eliminating resource consumption during waiting phases.

- **Orchestration Workflow (TypeScript)**:
```typescript
import { task, step, workflow, sleep, parallel, taskScript } from "windmill-client"

async function validatePayload(url: string) {
  const res = await fetch(url)
  return res.json()
}

export const main = workflow(async (targetUrl: string, clusterNodes: number[]) => {
  // Inline checkpoint for non-deterministic operations (timestamps, uuids)
  const executionTimestamp = await step("init_time", () => new Date().toISOString())

  // Distribute execution to an atomic script asset
  const setupConfig = await taskScript("f/ops/provision_check")({ timestamp: executionTimestamp })

  // Headless parallel scaling with explicit concurrency limits
  const nodeStatuses = await parallel(clusterNodes, (nodeId) =>
    task(async () => {
      const data = await validatePayload(`${targetUrl}/node/${nodeId}`)
      return { id: nodeId, active: data.status === "UP" }
    })(),
    { concurrency: 5 } // Strict boundary control
  )

  // Non-blocking sleep: Worker is freed, workflow yields state to database
  await sleep(10)

  return { setupConfig, nodes: nodeStatuses }
})
```

### 2.6 Full-Code Apps (React / Svelte Component Architecture)
For interfaces requiring comprehensive programmatic customization, state management, or browser-based testing automation, Windmill supports **Full-Code Apps**. This bypasses low-code UI limitations by hosting pure React or Svelte Single Page Applications (SPAs).
* **CLI Lifecycle**: Run `wmill app dev <path>` to instantiate a local frontend scaffolding utilizing hot-module replacement (HMR).
* **Type-Safe Binding**: The CLI generates a `wmill.ts` client file directly inferred from backend Script and Flow types, matching parameters seamlessly:
  ```typescript
  // React Component snippet within a Full-Code App structure
  import React, { useState } from 'react'
  import { client } from './wmill' // Auto-generated contract wrapper

  export function OrderTrigger() {
    const [status, setStatus] = useState('')

    const triggerHeadlessPipeline = async () => {
      // Calls backend execution via a strongly-typed proxy
      const response = await client.runScript("f/orders/process", { amount: 250 })
      setStatus(response.status)
    }

    return <button onClick={triggerHeadlessPipeline}>Status: {status}</button>
  }
  ```
* **Deployment**: Frontend bundles compile down to structural YAML files and static directories, completely testable via headless browsers (Playwright/Puppeteer) post-deployment.

### 2.7 Declarative Flows (YAML Representations)
Visual flows are stored natively as structured JSON/YAML DAG manifests, enabling programmatic generation, modification, and evaluation without parsing UI binaries.
```yaml
summary: "Headless Pipeline Execution Manifest"
value:
  modules:
    - id: extract_step
      value:
        type: script
        path: "f/etl/extract"
        input_transforms:
          limit:
            type: javascript
            expr: "100"
    - id: transform_step
      value:
        type: script
        path: "f/etl/transform"
        input_transforms:
          raw_data:
            type: javascript
            expr: "result.extract_step"
  same_worker: false
```

### 2.8 Triggers & Webhook Endpoints
Triggers expose jobs programmatically to external event loops. Every asset generates both synchronous (blocking until completion) and asynchronous (returning a job UUID immediately) endpoints.
```bash
# Headless Async dispatch returning an execution UUID
curl -X POST "[https://app.windmill.dev/api/w/demo/jobs/run/p/f/ops/cleanup](https://app.windmill.dev/api/w/demo/jobs/run/p/f/ops/cleanup)" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $WM_TOKEN" \
  --data '{"force": true}'
```
Advanced routes support native URL query wrapping (`?wrap_body=true`) and signature verification pipelines (`?raw=true`). Additional native connectors execute headless long-polling or pub/sub listening for Kafka, SQS, WebSockets, and PostgreSQL logical replication lines.

### 2.9 Error Handling & Retries
Errors are intercepted at the script level, step level, or via global workspace error handler hooks. Programmatic retries are defined declaratively in the asset's configuration.
```yaml
# Injected into task configurations for automated error resilience
retry:
  exponential:
    attempts: 4
    multiplier: 2
    seconds: 5 # Backoff calculates automatically: delay = multiplier * seconds ^ attempt
```

### 2.10 AI Agents & Tool Executions
AI Agent primitives process LLM tracking instructions headlessly. Tools are exposed to agents directly as specialized scripts or Model Context Protocol (MCP) servers, returning structured payloads verified by strict output schemas.

---

## 3. Real-World Headless Use Cases

- **Highly Concurrent Distributed ETL Pipelines**: Splitting intensive extraction routines into automated steps, utilizing `parallel()` task structures to fetch endpoints via bounded workers, and batch-inserting results via the native `wmill.datatable()` layer.
- **GitOps-Driven CI/CD Infrastructure Loops**: Managing complex continuous integration events headlessly via the `wmill` CLI, handling deployment promotions across isolated workspaces without logging into user interfaces.
- **Automated Human-in-the-Loop Webhook Operations**: Initiating automated system checks, generating secure transient approval tokens with `getResumeUrls()`, and suspending execution safely without holding live machine execution blocks.

---

## 4. Headless Developer Friction Points

- **Non-Determinism in Replayed Workflows (WAC)**: Because WAC relies on checkpoint-and-replay architecture to preserve compute resources, arbitrary calls inside the main workflow function body (e.g., `Math.random()`, `Date.now()`, or direct un-insulated `fetch()` calls) will cause divergence during execution replays. **Mitigation**: Wrap all side-effectful code execution inside explicit `await step("key", () => fn)` assignments.
- **Workflow Step Key Shifting**: Task states match chronologically according to execution order inside Workflows-as-Code. Branch structures that conditionally run or skip tasks out of sequence alter downstream structural keys, inadvertently causing the rerun of completed executions. **Mitigation**: Maintain fixed sequence patterns or explicit structural wrappers.
- **Persistent Script State vs. Active Flow User State**: `wmill.get_state()` tracks variable values across distinct runs of a script asset globally, whereas `getFlowUserState()` isolates values solely within a single unique pipeline execution instance. Confusing these leads to state corruption or unexpected resets.
- **Destructive Sync Semantics in Stateless Deployments**: Commands like `wmill sync push` operate state-destructively; assets discovered on the instance that are absent from the local workspace root are deleted immediately upon deployment. **Mitigation**: Explicitly define `keepDeleted: true` inside the local `wmill.yaml` file to protect un-tracked production resources.
- **Worker Dependency Management Cold Starts**: Injecting large package dependency graphs (e.g., intensive machine learning frameworks or binary bindings) via inline script annotations requires workers to build runtime environments dynamically upon initialization, producing heavy cold start execution overhead. **Mitigation**: Package long-running or dependency-heavy scripts as custom, pre-compiled **arbitrary Docker images** within Windmill's runtime tasks.
- **Cloud Hosted**: Never try to start a local Windmill instance, ALWAYS use the cloud hosted version.

---

## 5. Headless Evaluation Test Suites

### Simple Tests
1. **Resource Database Query**: Author an isolated TypeScript or Rust script accepting a typed `Postgresql` credential structure, executing a raw row count selection query, and returning an exact JSON integer.
2. **Headless Execution Counter**: Construct a Python script utilizing `wmill.get_state` and `wmill.set_state` to atomically track and increment execution indices across standalone CLI executions.
3. **Advanced Cron Event Dispatches**: Define an automated Unix schedule via the extended `croner` syntax and link it to an asset to confirm proper time-zone based execution dispatches via CLI tracking logs.

### Medium Tests
4. **Bounded Concurrency Fanning**: Create a Workflow-as-Code (WAC) routine that processes an array of target endpoints, executes concurrent HTTP calls using `parallel(..., { concurrency: 3 })`, and aggregates responses into an array of `{ url, status }` objects.
5. **Full-Code UI Contract Verification**: Instantiate a Full-Code React Application locally via `wmill app dev`, call an underlying workspace database script using the auto-generated client proxy, and assert behavior via a headless browser testing suite (e.g., Playwright).
6. **Built-In Data Table CRUD**: Programmatically write data records to the internal PostgreSQL store via `wmill.datatable()`, and read the records back from an independent async script ensuring strict JSON schema structure checking.

### Complex Tests
7. **End-to-End GitOps Pipeline Promotion**: Construct an isolated, environment-aware `wmill.yaml` configuration split across `staging` and `production` targets. Execute an automated promotion sequence from a headless CI script utilizing `wmill sync push --workspace production --yes`.
8. **Multi-Stage Replay Resumption Workflow**: Design an advanced deployment WAC pipeline (`runTests -> deployStaging -> waitForApproval -> deployProduction`). Verify via headless API requests that calling the tokenized resumption endpoint generated by `getResumeUrls()` restarts the pipeline exactly from its suspended checkpoint without re-running tests.
9. **Dockerized Environment Failover Integration**: Package an analytics script with heavy native system requirements into an independent Docker container task. Trigger it via a webhook endpoint and assert execution stability on workers without inducing dependency cold start delays.

---

## 6. Sources

1. [Windmill - Top-Level Infrastructure](https://www.windmill.dev/docs/intro)
2. [Windmill Docs Structured Index Manifest](https://www.windmill.dev/llms.txt)
3. [TypeScript & Bun Script Engine Lifecycles](https://www.windmill.dev/docs/getting_started/scripts_quickstart/typescript)
4. [Python Scripting and Validation Integration](https://www.windmill.dev/docs/getting_started/scripts_quickstart/python)
5. [Workflows-as-Code Execution Specifications](https://www.windmill.dev/docs/core_concepts/workflows_as_code)
6. [Resource Formats & Vault State Schemas](https://www.windmill.dev/docs/core_concepts/resources_and_types)
7. [Full-Code Single Page App Hosting Infrastructure](https://www.windmill.dev/docs/apps/app_editor)
8. [Built-In Data Table Management & Schema Architecture](https://www.windmill.dev/docs/core_concepts/resources_and_types#states)
9. [CLI Core Synchronization Commands and YAML Layouts](https://www.windmill.dev/docs/advanced/cli/sync)