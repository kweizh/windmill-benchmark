# TypeScript Windmill Script with Helper Functions

## Background

In Windmill TypeScript scripts, you can define helper functions in the same file alongside `main`. Only `main` is the entry point Windmill calls, but helper functions keep the logic organized and testable. This is the recommended pattern for scripts with non-trivial logic.

## Requirements

- Create a TypeScript script at `/home/user/windmill-project/f/scripts/invoice.ts`.
- Define these helper functions (NOT exported):
  ```typescript
  function formatCurrency(amount: number, currency: string): string {
    return `${currency} ${amount.toFixed(2)}`;
  }

  function computeSubtotal(items: Array<{ qty: number; unit_price: number }>): number {
    return items.reduce((sum, item) => sum + item.qty * item.unit_price, 0);
  }
  ```
- Export an async `main` function:
  ```typescript
  export async function main(
    items: Array<{ name: string; qty: number; unit_price: number }>,
    tax_rate: number = 0.1,
    currency: string = "USD"
  )
  ```
  returning:
  ```typescript
  {
    subtotal: formatCurrency(subtotal, currency),
    tax: formatCurrency(subtotal * tax_rate, currency),
    total: formatCurrency(subtotal * (1 + tax_rate), currency),
    line_items: items.map(i => ({
      name: i.name,
      amount: formatCurrency(i.qty * i.unit_price, currency)
    }))
  }
  ```
- Create the metadata file at `/home/user/windmill-project/f/scripts/invoice.script.yaml` with:
  - `summary: "Generate an invoice summary from line items"`
  - `language: typescript`

## Constraints

- Project path: `/home/user/windmill-project`
- Helper functions must NOT be exported
- Currency format: `"USD 10.00"` (currency code then amount)

## Integrations

None.
