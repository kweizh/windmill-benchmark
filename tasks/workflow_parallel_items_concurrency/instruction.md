# Build a Windmill Workflow Using `parallel()` with Concurrency Control

## Background

Windmill's WAC engine provides a `parallel()` utility for processing a list of items with bounded concurrency. Unlike `Promise.all`, which dispatches all tasks simultaneously, `parallel()` with a `concurrency` option limits how many child jobs run at the same time — essential for rate limiting and resource management.

The signature is:
```typescript
const results = await parallel(items, (item) => task(processItem)(item), { concurrency: 3 });
```

## Requirements

Create a workflow at `/home/user/windmill-project/f/workflows/batch_processor.ts` that:

1. Defines a `checkUrl` task function that accepts a `url: string` and returns `{ url, status: number, ok: boolean }` by fetching the URL with `fetch()` and reading `response.status` and `response.ok`. If the fetch throws (network error), return `{ url, status: 0, ok: false }`.
2. Defines a `summarize` task function that accepts `results: Array<{url: string, status: number, ok: boolean}>` and returns `{ total: results.length, successful: count of ok===true, failed: count of ok===false }`.
3. Exports `main` as a `workflow()` that:
   - Accepts `urls: string[]` as input.
   - Uses `parallel(urls, (url) => task(checkUrl)(url), { concurrency: 3 })` to process all URLs.
   - Passes the results array to `task(summarize)(results)`.
   - Returns the summary object.

## Implementation Guide

1. Create the file `/home/user/windmill-project/f/workflows/batch_processor.ts`.
2. Import `{ task, workflow, parallel }` from `windmill-client`.
3. Implement `checkUrl` and `summarize` as async functions.
4. Implement `main` as `workflow(async (urls: string[]) => { ... })`.
5. Use `parallel(urls, (url) => task(checkUrl)(url), { concurrency: 3 })`.

## Constraints

- Project path: `/home/user/windmill-project`
- Output file: `/home/user/windmill-project/f/workflows/batch_processor.ts`
- The concurrency limit MUST be exactly `3`.
- The `checkUrl` function MUST handle fetch errors (try/catch) and return `{ url, status: 0, ok: false }` on error.
- The `summarize` function must compute `total`, `successful`, and `failed` counts.
- No live Windmill server is required.
