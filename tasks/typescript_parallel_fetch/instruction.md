# Windmill TypeScript Workflow-as-Code: Parallel URL Status Check

## Background
Windmill's Workflow-as-Code (WAC) model lets you write durable, distributed workflows in plain TypeScript. The `task()` wrapper dispatches each function call as an independent child job, and `parallel()` runs a batch of tasks concurrently with an optional concurrency cap.

Your goal is to create a TypeScript WAC script that checks the HTTP status of a list of URLs in parallel and returns a summary of results.

## Requirements
- Create the TypeScript workflow script at `/home/user/windmill-project/f/workflows/parallel_status_check.ts`.
- Create a companion YAML metadata file at `/home/user/windmill-project/f/workflows/parallel_status_check.script.yaml`.

## Implementation Guide

### Step 1 — Create the project directory
```bash
mkdir -p /home/user/windmill-project/f/workflows
```

### Step 2 — Write the TypeScript script
Create `/home/user/windmill-project/f/workflows/parallel_status_check.ts` with the following structure:

```typescript
import { task, workflow, parallel } from 'windmill-client';

async function checkUrl(url: string): Promise<{ url: string; status: number; ok: boolean }> {
  const response = await fetch(url);
  return { url, status: response.status, ok: response.ok };
}

export const main = workflow(async (urls: string[]) => {
  const results = await parallel(
    urls.map(url => task(checkUrl)(url)),
    { concurrency: 3 }
  );
  const summary = results.filter(r => r.ok).length;
  return { results, summary };
});
```

Key points:
- `task(checkUrl)` wraps `checkUrl` so each URL is checked as a separate child job.
- `parallel([...], { concurrency: 3 })` dispatches all tasks simultaneously but limits in-flight concurrency to 3.
- The returned object has a `results` array and a `summary` field counting the number of successful (ok=true) responses.

### Step 3 — Write the companion YAML
Create `/home/user/windmill-project/f/workflows/parallel_status_check.script.yaml`:

```yaml
description: Parallel URL status checker using Windmill WAC
lang: ts
schema:
  $schema: 'https://json-schema.org/draft/2020-12/schema'
  type: object
  properties:
    urls:
      type: array
      items:
        type: string
      description: List of URLs to check in parallel
  required:
    - urls
```

## Constraints
- Project path: /home/user/windmill-project
- No live Windmill server is required; the task is purely file-creation.
- Use `import { task, workflow, parallel } from 'windmill-client'` — all three named exports must be present.
- The `main` export must be defined as `workflow(async (urls: string[]) => { ... })`.
- The concurrency limit passed to `parallel()` must be 3.
- The return value must include both a `results` array and a `summary` field.
