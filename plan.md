 1. Library Overview

*   **Description**: Windmill is an open-source, self-hostable developer platform and workflow engine designed to build internal tools, automate workflows, and create AI agents. It serves as a high-performance alternative to Retool, Temporal, and Airflow.

*   **Ecosystem Role**: It acts as the orchestration layer for modern tech stacks, integrating with databases (Postgres, Snowflake), messaging (Slack, Discord), and AI services (OpenAI, Anthropic). It supports multiple languages (TypeScript, Python, Go, Rust, SQL) and offers both low-code and full-code development paths.

*   **Project Setup**:

    1.  **Install CLI**: `npm install -g windmill-cli` (requires Node > v20).

    2.  **Authentication**: `wmill login` to connect to a Windmill instance (Cloud or Self-hosted).

    3.  **Local Sync**: `wmill sync pull` to download the workspace structure to a local directory.

    4.  **Development**: Create scripts (e.g., `f/my_folder/my_script.ts`) and accompanying metadata (`f/my_folder/my_script.script.yaml`).

    5.  **Deployment**: `wmill sync push` or `wmill script push f/my_folder/my_script.ts` to deploy to the instance.

### 2. Core Primitives & APIs

*   **Scripts**: The fundamental unit of execution. Functions with typed arguments that Windmill automatically parses into a UI.

    *   [TypeScript Quickstart](https://www.windmill.dev/docs/getting_started/scripts_quickstart/typescript)

    *   ```typescript

        // Basic Script Structure

        import * as wmill from 'windmill-client';

        export async function main(name: string, age: number) {

          return `Hello ${name}, you are ${age} years old.`;

        }

        ```

*   **Workflows as Code (WAC)**: Orchestrate multiple scripts using familiar language constructs with zero worker waste during waits.

    *   [Workflows as Code Docs](https://www.windmill.dev/docs/core_concepts/workflows_as_code)

    *   ```typescript

        import { workflow, task, sleep, waitForApproval } from 'windmill-client';

        export const main = workflow(async (data: string) => {

          const result = await task(processData)(data);

          await sleep(3600); // Suspends parent job, releases worker

          const approval = await waitForApproval({ timeout: 1800 });

          if (approval.approved) {

            return await task(deploy)(result);

          }

        });

        ```

*   **Resources**: Structured JSON objects for credentials and configuration (e.g., Database connections, API keys).

    *   [Resources & Types Docs](https://www.windmill.dev/docs/core_concepts/resources_and_types)

    *   ```typescript

        // Fetching a resource programmatically

        const dbConfig = await wmill.getResource('u/user/my_db');

        ```

*   **States**: Persistent data that survives between different executions of the same script/trigger.

    *   [State Management Docs](https://www.windmill.dev/docs/core_concepts/resources_and_types#states)

    *   ```python

        from wmill import get_state, set_state

        def main():

            last_run = get_state() or 0

            set_state(time.time())

        ```

### 3. Real-World Use Cases & Templates

*   **ETL Pipelines**: Fetching data from APIs in parallel, transforming it, and loading it into a database ([Example](https://www.windmill.dev/docs/core_concepts/workflows_as_code#etl-pipeline-with-retry)).

*   **Human-in-the-loop Deployments**: Running tests, deploying to staging, and waiting for Slack-based approval before production ([Example](https://www.windmill.dev/docs/core_concepts/workflows_as_code#deployment-with-approval-gate)).

*   **Cron-based Monitoring**: Scheduled scripts that check service health and use `set_state` to alert only on status changes.

*   **Windmill Hub**: A community repository of 200+ integrations and scripts (Slack, OpenAI, GSheets, etc.) at [hub.windmill.dev](https://hub.windmill.dev/).

### 4. Developer Friction Points

*   **Determinism in WAC**: Developers often forget that WAC replays on failure/suspension. Using non-deterministic code (like `Date.now()` or `Math.random()`) outside of a `step()` primitive will cause state mismatches. [WAC Determinism Rules](https://www.windmill.dev/docs/core_concepts/workflows_as_code#determinism-requirement).

*   **Resource Permission Scoping**: In the App editor, dynamic resources (those not hardcoded in a select component) require a specific toggle "Resources from users allowed" to be enabled, which is a common source of "Permission Denied" errors. [App Resource Policy](https://www.windmill.dev/docs/core_concepts/resources_and_types#resources-in-apps).

*   **Flow State vs. Persistent State**: Confusion between `getFlowUserState` (lives only for the duration of a flow) and `get_state` (persists across different job runs).

### 5. Evaluation Ideas

*   **Simple**: Create a TypeScript script that accepts a "Postgres" resource and returns the count of rows in a specific table.

*   **Simple**: Implement a Python script that uses `set_state` to track the number of times it has been executed.

*   **Medium**: Build a Workflow-as-Code that fetches a list of URLs in parallel (concurrency=3) and aggregates their status codes.

*   **Medium**: Create a Windmill App with a text input and a button that triggers a script to send a message to a Slack channel defined in a Resource.

*   **Complex**: Implement a multi-stage deployment workflow with an exponential backoff retry for the first step and a `waitForApproval` gate for the final step.

*   **Complex**: Refactor a sequential Flow into a deterministic Workflow-as-Code, correctly using `step()` for ID generation and `taskScript()` for external calls.

### 6. Sources

1.  [Windmill Documentation](https://www.windmill.dev/docs/intro) - Core documentation portal.

2.  [Windmill llms.txt](https://www.windmill.dev/llms.txt) - Structured overview of the documentation.

3.  [Workflows as Code Guide](https://www.windmill.dev/docs/core_concepts/workflows_as_code) - Detailed technical spec for the WAC engine.

4.  [Windmill CLI Docs](https://www.windmill.dev/docs/advanced/cli) - Local development and syncing instructions.

5.  [Windmill Hub](https://hub.windmill.dev/) - Repository of scripts and integrations.

6.  [Windmill OpenAPI Spec](https://app.windmill.dev/api/openapi.json) - Full API reference for backend interactions.
