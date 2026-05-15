# Windmill WAC Companion-Module Refactoring Notes

## What changed

### Before
`f/workflows/data_processor.ts` was a **monolithic** script:
- All helper functions (`fetchData`, `processRecords`, `saveReport`) were
  defined inline in the same file.
- The workflow used `task(fn)(args)` – wrapping local function references.
- No companion module folder existed.

### After
The file tree now follows the **WAC `__mod/` companion-module pattern**:

```
f/workflows/
├── data_processor.ts               ← orchestration-only workflow
└── data_processor/
    └── __mod/
        ├── fetch_data.ts           ← Step 1: HTTP fetch
        ├── process_records.ts      ← Step 2: record enrichment
        └── save_report.ts          ← Step 3: summary / persistence
```

## Key design decisions

| Concern | Before | After |
|---------|--------|-------|
| Helper location | Inline in workflow file | Separate `__mod/` task scripts |
| Windmill API used | `task(localFn)(args)` | `taskScript("f/…/__mod/name")(args)` |
| Business logic in workflow | Yes | No – workflow is pure orchestration |
| Each step independently deployable | No | Yes |
| Each step independently testable | No | Yes |

## Per-module summary

### `__mod/fetch_data.ts`
- **Input:** `url: string`
- **Output:** `any` (parsed JSON body)
- **Behaviour:** issues a `fetch()`, throws on non-2xx, returns parsed JSON.

### `__mod/process_records.ts`
- **Input:** `data: any[]`
- **Output:** `any[]`
- **Behaviour:** maps each record, stamping `processed: true` and `count`.

### `__mod/save_report.ts`
- **Input:** `results: any[]`
- **Output:** `{ total: number; status: "saved" }`
- **Behaviour:** logs a summary line and returns a structured report object.

## How `taskScript()` works in Windmill

`taskScript("f/path/to/script")` returns a callable that, when invoked,
schedules the referenced script as a **child job** inside the current
workflow run.  Windmill resolves the script path against the workspace,
meaning each module can be versioned, permissioned, and monitored
independently – exactly as if it were called from a flow step.
