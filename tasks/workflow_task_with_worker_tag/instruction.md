# Fix Windmill Workflow: Route GPU Task to Worker Tag

## Background

Windmill's Workflow-as-Code (WAC) `task()` primitive accepts an optional options object as its second argument. One key option is `tag`, which routes the dispatched child job to a specific worker group. For example:

```typescript
await task(trainModel, { tag: 'gpu' })(data);
```

This ensures that compute-intensive tasks like model training are executed on workers tagged with `'gpu'` (i.e., GPU-equipped machines), while lighter tasks like preprocessing can run on any standard worker.

A broken ML pipeline workflow has been placed at `/home/user/windmill-project/f/workflows/ml_pipeline.ts`. It calls both `preprocessData` and `trainModel` without any routing tag. The `trainModel` task must be fixed to include `{ tag: 'gpu' }` so it is always dispatched to GPU workers.

## Requirements

- Keep `await task(preprocessData)(rawData)` **unchanged** (no tag should be added).
- Change `await task(trainModel)(processedData)` to `await task(trainModel, { tag: 'gpu' })(processedData)`.
- The `workflow(` wrapper and all function definitions must remain intact.

## Implementation Guide

1. Open `/home/user/windmill-project/f/workflows/ml_pipeline.ts`.
2. Locate the line:
   ```typescript
   const modelResult = await task(trainModel)(processedData);
   ```
3. Replace it with:
   ```typescript
   const modelResult = await task(trainModel, { tag: 'gpu' })(processedData);
   ```
4. Save the file. Do **not** modify any other lines.

## Constraints

- Project path: `/home/user/windmill-project`
- File to edit: `/home/user/windmill-project/f/workflows/ml_pipeline.ts`
- `preprocessData` task must **NOT** have a tag — leave `task(preprocessData)(rawData)` as-is.
- `trainModel` task **MUST** have `tag: 'gpu'` in its options object.
- No live Windmill server is required; the fix is purely a code change.

## Integrations
- None
