# Fix Windmill Workflow: Wrap Non-Deterministic Calls in `step()`

## Background

Windmill's Workflows-as-Code (WAC) engine uses a checkpoint/replay model. When a workflow is suspended and later resumed, the orchestration function replays from the beginning. If the workflow uses non-deterministic expressions like `Date.now()`, `Math.random()`, or `crypto.randomUUID()` directly in the workflow body, each replay will produce **different values** for these expressions, breaking checkpoint consistency and potentially causing incorrect behavior.

The correct fix is to wrap these non-deterministic calls in `step()`, which executes the function inline once and persists the result so that replays return the cached value.

A broken order-processing workflow has been placed at `/home/user/windmill-project/f/workflows/order_processor.ts`. It uses `Date.now()` directly to generate a timestamp and `Math.random()` to generate an order ID. Both must be wrapped in `step()` calls.

## Requirements

- Wrap `Date.now()` in a `step()` call with key `'timestamp'`.
- Wrap `Math.random().toString(36).slice(2)` in a `step()` call with key `'order_id'`.
- Import `step` from `windmill-client` in addition to the existing imports.
- Keep all other workflow logic intact (the `task(processOrder)` and `task(notifyShipping)` calls must remain unchanged).

## Implementation Guide

1. Open `/home/user/windmill-project/f/workflows/order_processor.ts`.
2. Add `step` to the import from `windmill-client`.
3. Replace:
   ```typescript
   const timestamp = Date.now();
   const orderId = Math.random().toString(36).slice(2);
   ```
   With:
   ```typescript
   const timestamp = await step('timestamp', () => Date.now());
   const orderId = await step('order_id', () => Math.random().toString(36).slice(2));
   ```
4. Save the file.

## Constraints

- Project path: `/home/user/windmill-project`
- File to edit: `/home/user/windmill-project/f/workflows/order_processor.ts`
- Do NOT rename any functions or change the exported `main` signature.
- Do NOT use bare `Date.now()` or `Math.random()` calls outside of `step()` in the workflow body.
- No live Windmill server is required; the fix is purely a code change.
