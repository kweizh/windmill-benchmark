# TypeScript Windmill Script — Date Formatting and Difference

## Background

Windmill scripts often need to work with dates — formatting timestamps for display, computing how many days until a deadline, or checking if something is overdue. This task involves building a utility script that performs both.

## Requirements

- Create a TypeScript script at `/home/user/windmill-project/f/scripts/date_utils.ts`.
- Export an async `main` function:
  ```typescript
  export async function main(iso_date: string, label: string = "Event")
  ```
  where `iso_date` is an ISO 8601 date string (e.g., `"2025-12-31"`).
- The function must return:
  ```typescript
  {
    label: string,
    formatted: string,   // "December 31, 2025"
    iso: string,         // the original iso_date
    days_from_today: number  // positive = future, negative = past
  }
  ```
  Use `toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' })` for `formatted`.
  For `days_from_today`, compute `Math.round((target - today) / 86400000)` where today is midnight UTC.
- Create the metadata file at `/home/user/windmill-project/f/scripts/date_utils.script.yaml` with:
  - `summary: "Format a date and compute days from today"`
  - `language: typescript`

## Implementation Guide

```typescript
export async function main(iso_date: string, label: string = "Event") {
  const target = new Date(iso_date);
  const today = new Date(new Date().toISOString().split('T')[0]);
  const days_from_today = Math.round((target.getTime() - today.getTime()) / 86400000);
  return {
    label,
    formatted: target.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
    iso: iso_date,
    days_from_today,
  };
}
```

## Constraints

- Project path: `/home/user/windmill-project`
- Return keys must be exactly: `label`, `formatted`, `iso`, `days_from_today`
- `formatted` must use `en-US` locale: e.g., `"December 31, 2025"`

## Integrations

None.
