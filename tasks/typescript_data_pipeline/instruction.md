# TypeScript Windmill Script — Multi-Stage Data Pipeline

## Background

A single Windmill TypeScript script can implement a complete multi-stage data transformation pipeline as chained function calls within `main`. This is useful when the transformation logic is too simple to warrant a full multi-step flow, but complex enough to need several passes over the data.

## Requirements

- Create a TypeScript script at `/home/user/windmill-project/f/scripts/etl_pipeline.ts`.
- Export an async `main` function:
  ```typescript
  export async function main(
    raw_records: Array<{ name: string; value: string; category: string }>,
    filter_category: string = "",
    value_multiplier: number = 1
  )
  ```
- The pipeline must perform these stages **in order**:
  1. **Parse**: convert `value` from string to float (skip records where `value` is not a valid number, setting `parse_error: true`).
  2. **Filter**: if `filter_category` is non-empty, keep only records where `category === filter_category`.
  3. **Transform**: multiply each numeric value by `value_multiplier`.
  4. **Aggregate**: compute `{ total: sum, count, average }` from the transformed values.
- Return:
  ```typescript
  {
    input_count: number,
    output_count: number,
    parse_errors: number,
    filter_category: string,
    records: Array<{ name: string; value: number; category: string }>,
    aggregate: { total: number; count: number; average: number }
  }
  ```
- Create the metadata file at `/home/user/windmill-project/f/scripts/etl_pipeline.script.yaml` with:
  - `summary: "Multi-stage ETL pipeline: parse, filter, transform, aggregate"`
  - `language: typescript`

## Constraints

- Project path: `/home/user/windmill-project`
- Pipeline stages must run in order: parse → filter → transform → aggregate
- Records with parse errors are excluded from subsequent stages
- `aggregate.average` is 0 if `count` is 0

## Integrations

None.
