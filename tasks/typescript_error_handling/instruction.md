# TypeScript Windmill Script with Input Validation and Error Handling

## Background

In Windmill, when a script throws an error, the step fails and the error message is surfaced in the Windmill UI or passed to an error handler branch in a flow. Writing scripts that validate inputs and throw meaningful errors is a best practice in Windmill development.

## Requirements

- Create a TypeScript script at `/home/user/windmill-project/f/scripts/divide.ts`.
- Export an async `main` function:
  ```typescript
  export async function main(numerator: number, denominator: number)
  ```
- If `denominator === 0`, throw: `new Error("Division by zero is not allowed")`
- Otherwise, return `{ result: numerator / denominator, numerator, denominator }`
- Create the metadata file at `/home/user/windmill-project/f/scripts/divide.script.yaml` with:
  - `summary: "Divide two numbers with zero-check"`
  - `language: typescript`

## Implementation Guide

1. Create `f/scripts/divide.ts`:
   ```typescript
   export async function main(numerator: number, denominator: number) {
     if (denominator === 0) {
       throw new Error("Division by zero is not allowed");
     }
     return { result: numerator / denominator, numerator, denominator };
   }
   ```
2. Create the metadata YAML.

## Constraints

- Project path: `/home/user/windmill-project`
- Error message must be exactly: `"Division by zero is not allowed"`
- Return object keys: `result`, `numerator`, `denominator`

## Integrations

None.
