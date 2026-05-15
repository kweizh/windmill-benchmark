# WAC Determinism Violations Fixed

## Summary
Fixed all 4 WAC determinism violations in the order workflow by wrapping non-deterministic calls with `step()`.

## Changes Made

### 1. Import Statement
- Added `step` to the imports from `windmill-client`

### 2. Fixed Violations

| Bug | Original Issue | Fix |
|-----|----------------|-----|
| BUG 1 | `Date.now()` called directly in workflow body | Wrapped with `await step(() => Date.now())` |
| BUG 2 | `randomUUID()` called directly in workflow body | Wrapped with `await step(() => randomUUID())` |
| BUG 3 | `Math.random()` called directly in workflow body | Wrapped with `await step(() => Math.random() * 0.1)` |
| BUG 4 | `process.env.TAX_RATE` read directly in workflow body | Wrapped with `await step(() => parseFloat(process.env.TAX_RATE || '0.1'))` |

## Why This Matters

In Windmill workflows, non-deterministic operations (those that produce different results on each execution) must be wrapped with `step()` to ensure:

1. **Deterministic Replay**: Workflows can be replayed and reproduce the same results
2. **Consistency**: The workflow execution is predictable and idempotent
3. **Proper State Management**: Non-deterministic values are captured as workflow state at specific steps

## Files Modified
- `/home/user/windmill-project/f/workflows/order_workflow.ts` (fixed)

## Artifacts Preserved
- `/logs/artifacts/order_workflow_original.ts` (before fix)
- `/logs/artifacts/order_workflow_fixed.ts` (after fix)
- `/logs/artifacts/fix_summary.md` (this file)