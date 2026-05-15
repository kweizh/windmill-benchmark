# Windmill Workflow-as-Code: Basic Task Chain

## Background
Windmill's Workflow-as-Code (WAC) lets you define multi-step data pipelines entirely in TypeScript. Each step is dispatched as an isolated child job via `task(fn)(args)`, giving it its own logs, worker, and timeline entry while the orchestration body suspends and consumes zero workers between tasks.

## Requirements
Create a TypeScript Workflow-as-Code file that chains **three tasks** in sequence:

1. **`validateInput(raw: string): string`** — Validates that the input is non-empty (throw an error if it is), then returns the trimmed string.
2. **`transformData(input: string): object`** — Transforms the validated string into an object with the shape:
   ```json
   { "original": "<input>", "upper": "<INPUT>", "word_count": <number> }
   ```
   where `word_count` is the number of space-separated words.
3. **`formatOutput(data: object): object`** — Adds metadata to produce the final result:
   ```json
   { ...data, "processed_at": "<ISO timestamp>", "status": "complete" }
   ```
   `new Date().toISOString()` is safe inside a `task()` because each task call is its own isolated child job.

The exported entry point must be:
```typescript
export const main = workflow(async (raw_input: string) => { ... });
```
which chains the three tasks in sequence: `validateInput` → `transformData` → `formatOutput`.

Also create a companion YAML metadata file for the workflow script.

## Implementation Guide

1. Inside `/home/user/windmill-project`, create the directory `f/workflows/` if it does not already exist.
2. Create the file `f/workflows/data_pipeline.ts` with the following structure:
   ```typescript
   import { task, workflow } from 'windmill-client';

   async function validateInput(raw: string): Promise<string> {
     if (!raw || raw.trim().length === 0) {
       throw new Error('Input must be non-empty');
     }
     return raw.trim();
   }

   async function transformData(input: string): Promise<object> {
     return {
       original: input,
       upper: input.toUpperCase(),
       word_count: input.split(' ').length,
     };
   }

   async function formatOutput(data: object): Promise<object> {
     return {
       ...data,
       processed_at: new Date().toISOString(),
       status: 'complete',
     };
   }

   export const main = workflow(async (raw_input: string) => {
     const validated  = await task(validateInput)(raw_input);
     const transformed = await task(transformData)(validated);
     return await task(formatOutput)(transformed);
   });
   ```
3. Create the companion YAML file `f/workflows/data_pipeline.script.yaml`:
   ```yaml
   summary: Basic three-step data pipeline
   description: Validates, transforms, and formats an input string through chained tasks.
   schema:
     $schema: 'https://json-schema.org/draft/2020-12/schema'
     type: object
     properties:
       raw_input:
         type: string
         description: The raw input string to process
         default: ''
     required:
       - raw_input
   is_template: false
   ```

## Constraints
- Project path: /home/user/windmill-project
- Use `windmill-client` for `task` and `workflow` imports — do NOT import `step`.
- The three task functions (`validateInput`, `transformData`, `formatOutput`) must be defined as standalone `async function` declarations (not lambdas), so they can be dispatched via `task()`.
- The `main` export must use `workflow()` as its wrapper.
- No live Windmill server is required; the files are evaluated statically.

## Integrations
- None
