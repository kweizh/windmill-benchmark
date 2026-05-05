# Create a Windmill Flow with a Conditional Branch

## Background

Windmill flows support `branchone` modules that evaluate a set of branch conditions in order and execute the first matching branch. This is Windmill's equivalent of an if/else — a key building block for decision-making pipelines.

## Requirements

Create three TypeScript scripts and a flow with a conditional branch:

### Script 1: `/home/user/windmill-project/f/scripts/check_score.ts`
```typescript
export async function main(score: number) {
  return { score, passed: score >= 60 };
}
```
Metadata: `summary: "Check if a score passes"`, `language: typescript`

### Script 2a: `/home/user/windmill-project/f/scripts/on_pass.ts`
```typescript
export async function main(score: number) {
  return `Score ${score}: PASSED`;
}
```
Metadata: `summary: "Emit a pass message"`, `language: typescript`

### Script 2b: `/home/user/windmill-project/f/scripts/on_fail.ts`
```typescript
export async function main(score: number) {
  return `Score ${score}: FAILED`;
}
```
Metadata: `summary: "Emit a fail message"`, `language: typescript`

### Flow: `/home/user/windmill-project/f/flows/score_check.yaml`
```yaml
summary: "Route based on score pass/fail"
value:
  modules:
    - id: a
      value:
        type: script
        path: f/scripts/check_score
        input_transforms:
          score:
            type: static
            value: 75
    - id: b
      value:
        type: branchone
        branches:
          - summary: "Passed"
            expr: "results.a.passed === true"
            modules:
              - id: c
                value:
                  type: script
                  path: f/scripts/on_pass
                  input_transforms:
                    score:
                      type: javascript
                      expr: "results.a.score"
        default:
          - id: d
            value:
              type: script
              path: f/scripts/on_fail
              input_transforms:
                score:
                  type: javascript
                  expr: "results.a.score"
```

## Constraints

- Project path: `/home/user/windmill-project`
- Flow file: `/home/user/windmill-project/f/flows/score_check.yaml`
- The `branchone` module must reference `results.a.passed` in the branch expression
- Default branch must route to `on_fail`

## Integrations

None.
