# TypeScript Windmill Script — Filter and Transform an Array

## Background

Windmill scripts often process collections of records passed in from a previous flow step or a webhook payload. TypeScript's native array methods (`filter`, `map`) are the idiomatic way to transform these collections before passing results downstream.

## Requirements

- Create a TypeScript script at `/home/user/windmill-project/f/scripts/filter_users.ts`.
- Export an async `main` function:
  ```typescript
  export async function main(
    users: Array<{ id: number; name: string; active: boolean }>,
    active_only: boolean = true
  )
  ```
- The function must:
  1. If `active_only` is `true`, keep only users where `active === true`.
  2. Return an array of objects `{ id: number; name: string; display: string }` where `display` is `` `#${id} — ${name}` ``.
- Create the metadata file at `/home/user/windmill-project/f/scripts/filter_users.script.yaml` with:
  - `summary: "Filter and format a list of users"`
  - `language: typescript`

## Implementation Guide

1. Create `f/scripts/filter_users.ts`:
   ```typescript
   export async function main(
     users: Array<{ id: number; name: string; active: boolean }>,
     active_only: boolean = true
   ) {
     const filtered = active_only ? users.filter(u => u.active) : users;
     return filtered.map(u => ({ id: u.id, name: u.name, display: `#${u.id} — ${u.name}` }));
   }
   ```
2. Create the metadata YAML.

## Constraints

- Project path: `/home/user/windmill-project`
- `display` format: `` `#${id} — ${name}` `` (em dash `—`, not a hyphen)
- When `active_only=false`, return all users

## Integrations

None.
