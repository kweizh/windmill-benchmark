# Create a Windmill Flow with Two Sequential Script Steps

## Background

Windmill flows are YAML definitions that chain scripts into pipelines. Each flow module has an `id`, a `value` describing what to run, and `input_transforms` that wire outputs from previous steps into the current step's inputs. The flow file lives in a `.flow/` directory or as a single `.yaml` file.

## Requirements

Create two TypeScript scripts and a flow that chains them:

### Script 1: `/home/user/windmill-project/f/scripts/generate_message.ts`
```typescript
export async function main(name: string) {
  return { message: `Hello, ${name}!`, timestamp: new Date().toISOString() };
}
```
With metadata `generate_message.script.yaml`: `summary: "Generate a greeting message"`, `language: typescript`

### Script 2: `/home/user/windmill-project/f/scripts/wrap_message.ts`
```typescript
export async function main(message: string, prefix: string = ">>>") {
  return `${prefix} ${message}`;
}
```
With metadata `wrap_message.script.yaml`: `summary: "Wrap a message with a prefix"`, `language: typescript`

### Flow: `/home/user/windmill-project/f/flows/greet_and_wrap.yaml`
A flow with two sequential steps:
- **Step `a`**: runs `f/scripts/generate_message` with a static input `name: "Windmill"`
- **Step `b`**: runs `f/scripts/wrap_message`, wiring `message` from `results.a.message` via a JavaScript expression input transform

The flow YAML must follow the Windmill flow format:
```yaml
summary: "Greet and wrap a message"
value:
  modules:
    - id: a
      value:
        type: script
        path: f/scripts/generate_message
        input_transforms:
          name:
            type: static
            value: "Windmill"
    - id: b
      value:
        type: script
        path: f/scripts/wrap_message
        input_transforms:
          message:
            type: javascript
            expr: "results.a.message"
```

## Constraints

- Project path: `/home/user/windmill-project`
- Flows directory: `/home/user/windmill-project/f/flows/`
- Flow file: `/home/user/windmill-project/f/flows/greet_and_wrap.yaml`
- Script step ids must be `a` and `b`
- Input transform for `message` in step `b` must use `type: javascript` with `expr: "results.a.message"`

## Integrations

None.
