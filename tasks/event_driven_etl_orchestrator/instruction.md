# Build an Event-Driven ETL Orchestrator

## Instruction

Build a TypeScript Windmill workflow at `/home/user/windmill-project/f/workflows/etl_orchestrator.ts` that:

1. Accepts `events: Array<{ id: string, type: string, payload: any }>` and optional `warehouseTarget: string = 'main'` as parameters.
2. Deduplicates events by reading previously processed event IDs from `/home/user/windmill-project/processed_events.json` (array of string IDs). Filter out any events whose `id` is already in this list.
3. Enriches only the new (non-duplicate) events in parallel (max 5 concurrent) using a Windmill task.
4. Obtains resume/approval URLs before requesting human approval, and logs the approval URL.
5. Waits for human approval before writing to the data warehouse.
6. On approval, writes to the warehouse, updates the processed_events.json file with the newly processed IDs, and returns a success summary.
7. On rejection, returns a rejection summary without writing.

## Constraints
- Project path: `/home/user/windmill-project`
- State file: `/home/user/windmill-project/processed_events.json`
- Output file: `/home/user/windmill-project/f/workflows/etl_orchestrator.ts`
