# TypeScript Windmill Script — Async Data Enrichment

## Background

Windmill's TypeScript runtime supports native async/await and `Promise.all`, making it well-suited for enriching collections in parallel. This task creates a script that simulates async enrichment of a list of items by adding computed fields.

## Requirements

- Create a TypeScript script at `/home/user/windmill-project/f/scripts/enrich_products.ts`.
- Export an async `main` function:
  ```typescript
  export async function main(
    products: Array<{ id: number; name: string; price: number }>,
    tax_rate: number = 0.1
  )
  ```
- Use `Promise.all` to enrich each product in parallel:
  ```typescript
  const enriched = await Promise.all(
    products.map(async (p) => ({
      ...p,
      tax: parseFloat((p.price * tax_rate).toFixed(2)),
      total: parseFloat((p.price * (1 + tax_rate)).toFixed(2)),
      label: `${p.name} ($${p.price})`,
    }))
  );
  return { count: enriched.length, tax_rate, products: enriched };
  ```
- Create the metadata file at `/home/user/windmill-project/f/scripts/enrich_products.script.yaml` with:
  - `summary: "Enrich a list of products with tax and total price"`
  - `language: typescript`

## Constraints

- Project path: `/home/user/windmill-project`
- Must use `Promise.all` (parallel enrichment, not sequential)
- `tax` and `total` must be rounded to 2 decimal places with `parseFloat(...toFixed(2))`
- Return keys: `count`, `tax_rate`, `products`

## Integrations

None.
