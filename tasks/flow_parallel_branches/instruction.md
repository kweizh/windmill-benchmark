# Create a Windmill Flow with Parallel Branches

## Background

Windmill's `branchall` module runs multiple branches in parallel and collects their results. This is ideal for fan-out patterns: sending the same data to multiple processors simultaneously and aggregating results in a later step.

## Requirements

Create three TypeScript scripts and a flow with parallel branches:

### Script: `/home/user/windmill-project/f/scripts/compute_word_count.ts`
```typescript
export async function main(text: string) {
  return { word_count: text.trim().split(/\s+/).filter(w => w).length };
}
```
Metadata: `summary: "Count words in text"`, `language: typescript`

### Script: `/home/user/windmill-project/f/scripts/compute_char_count.ts`
```typescript
export async function main(text: string) {
  return { char_count: text.length, char_count_no_spaces: text.replace(/\s/g, '').length };
}
```
Metadata: `summary: "Count characters in text"`, `language: typescript`

### Script: `/home/user/windmill-project/f/scripts/compute_line_count.ts`
```typescript
export async function main(text: string) {
  return { line_count: text.split('\n').length };
}
```
Metadata: `summary: "Count lines in text"`, `language: typescript`

### Flow: `/home/user/windmill-project/f/flows/text_stats.yaml`
```yaml
summary: "Compute text statistics in parallel"
value:
  modules:
    - id: stats
      value:
        type: branchall
        parallel: true
        branches:
          - summary: "Word count"
            modules:
              - id: words
                value:
                  type: script
                  path: f/scripts/compute_word_count
                  input_transforms:
                    text:
                      type: static
                      value: "Hello World\nThis is Windmill"
          - summary: "Char count"
            modules:
              - id: chars
                value:
                  type: script
                  path: f/scripts/compute_char_count
                  input_transforms:
                    text:
                      type: static
                      value: "Hello World\nThis is Windmill"
          - summary: "Line count"
            modules:
              - id: lines
                value:
                  type: script
                  path: f/scripts/compute_line_count
                  input_transforms:
                    text:
                      type: static
                      value: "Hello World\nThis is Windmill"
```

## Constraints

- Project path: `/home/user/windmill-project`
- Flow must use `type: branchall` with `parallel: true`
- All three scripts must run as separate branches

## Integrations

None.
