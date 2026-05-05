# Set Up a Complete Windmill Script Workspace

## Background

A production Windmill workspace typically contains a set of utility scripts organized under `f/scripts/`, flows under `f/flows/`, and consistent metadata files for every script. This task challenges you to set up a coherent workspace with three interdependent scripts and a flow that orchestrates them end-to-end.

## Requirements

Create the following files in `/home/user/windmill-project/`:

### 1. `/home/user/windmill-project/f/scripts/fetch_users.ts`
```typescript
export async function main(limit: number = 10): Promise<Array<{ id: number; name: string; email: string }>> {
  // Simulate fetching users (no real HTTP)
  return Array.from({ length: limit }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`
  }));
}
```
Metadata `fetch_users.script.yaml`: `summary: "Fetch a list of simulated users"`, `language: typescript`

### 2. `/home/user/windmill-project/f/scripts/enrich_users.ts`
```typescript
export async function main(
  users: Array<{ id: number; name: string; email: string }>,
  domain_filter: string = ""
) {
  const filtered = domain_filter
    ? users.filter(u => u.email.endsWith(domain_filter))
    : users;
  return filtered.map(u => ({ ...u, display: `[${u.id}] ${u.name} <${u.email}>` }));
}
```
Metadata `enrich_users.script.yaml`: `summary: "Enrich and optionally filter users by email domain"`, `language: typescript`

### 3. `/home/user/windmill-project/f/scripts/export_csv.ts`
```typescript
export async function main(records: Array<Record<string, unknown>>, delimiter: string = ",") {
  if (records.length === 0) return { csv: "", row_count: 0 };
  const headers = Object.keys(records[0]);
  const rows = [headers.join(delimiter), ...records.map(r => headers.map(h => String(r[h] ?? '')).join(delimiter))];
  return { csv: rows.join("\n"), row_count: records.length };
}
```
Metadata `export_csv.script.yaml`: `summary: "Export an array of records to CSV format"`, `language: typescript`

### 4. `/home/user/windmill-project/f/flows/user_export_pipeline.yaml`
```yaml
summary: "Fetch, enrich, and export users to CSV"
value:
  modules:
    - id: fetch
      value:
        type: script
        path: f/scripts/fetch_users
        input_transforms:
          limit:
            type: static
            value: 5
    - id: enrich
      value:
        type: script
        path: f/scripts/enrich_users
        input_transforms:
          users:
            type: javascript
            expr: "results.fetch"
    - id: export
      value:
        type: script
        path: f/scripts/export_csv
        input_transforms:
          records:
            type: javascript
            expr: "results.enrich"
```

## Constraints

- Project path: `/home/user/windmill-project`
- All 3 scripts + 3 metadata YAML files + 1 flow YAML = 7 files total
- `fetch_users.ts` must generate exactly `limit` users with ids 1..limit
- `export_csv.ts` must use `delimiter` as the column separator

## Integrations

None.
