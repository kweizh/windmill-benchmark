# TypeScript Windmill Script with Object-Typed Parameter

## Background

Windmill supports object-typed parameters for TypeScript scripts. When the parameter type is an inline object type, Windmill generates a nested form in its UI. This pattern is common for grouping related configuration fields together (e.g., database config, API credentials).

## Requirements

- Create a TypeScript script at `/home/user/windmill-project/f/scripts/send_email.ts`.
- Export an async `main` function:
  ```typescript
  export async function main(
    recipient: { email: string; name: string },
    subject: string,
    body: string,
    dry_run: boolean = true
  )
  ```
- The function must return:
  ```typescript
  {
    to: `${recipient.name} <${recipient.email}>`,
    subject,
    body,
    dry_run,
    sent: !dry_run,
    preview: `To: ${recipient.name} <${recipient.email}>\nSubject: ${subject}\n\n${body}`
  }
  ```
- Create the metadata file at `/home/user/windmill-project/f/scripts/send_email.script.yaml` with:
  - `summary: "Compose and optionally send an email"`
  - `language: typescript`

## Constraints

- Project path: `/home/user/windmill-project`
- `sent` must be `true` only when `dry_run` is `false`
- `to` format: `"Name <email@domain>"`
- `preview` must join header and body with `\n\n`

## Integrations

None.
