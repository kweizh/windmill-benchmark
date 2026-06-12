# Windmill AI Agent with a Structured-Output Tool

## Background
Windmill flows can include AI Agent steps that orchestrate an LLM with optional tools (Windmill scripts or MCP server entries) and that return structured payloads matching a JSON `output_schema`. Your job is to declare such an AI Agent flow declaratively on disk and deploy it to the cloud workspace at `https://app.windmill.dev` so that an HTTP caller can trigger the agent, have it call the tool, and receive a JSON object that validates against the agent's declared output schema.

The cloud workspace already has an AI provider preconfigured at the workspace level. Use that workspace AI resource for the agent step; you do not need to create a new AI resource. Picking a specific LLM/model is not constrained — use whatever the documented cloud-workspace default supports.

All work happens against the cloud instance using the Windmill CLI (`wmill`). Do not start a local Windmill instance.

## Requirements
- Author the assets locally under `/home/user/wm-agent/` as code-first Windmill files (declarative YAML + script source), then deploy them to the cloud workspace with `wmill sync push --yes`.
- Define one Windmill script tool that returns structured data about a product SKU. The script must take a single `sku` string argument and return a JSON object with the unit price and currency for that SKU. The script's source language is your choice (TypeScript/Bun, Python, etc.) as long as Windmill accepts it as a script asset.
- Define one Windmill flow that contains an AI Agent step. The AI Agent step must:
  - Use the agent module `type: aiagent` (the documented declarative type for AI Agent steps in flow YAML).
  - Reference the tool script from step above in the agent step's `tools` array (using the documented `tool_type: flowmodule` form with `type: script` and `path:` pointing at the tool script's deployed path), OR alternatively expose it via an MCP tool entry — either documented form is accepted.
  - Declare an `output_schema` (in `input_transforms.output_schema`) that constrains the agent's final reply to a JSON object with at least the fields `sku` (string), `unit_price` (number) and `currency` (string).
  - Take a single `prompt` flow input and pass it through as the AI Agent step's `user_message`.
- Deploy both assets to the cloud workspace under the folder prefix `f/agent_${run_id}/` (see `run-id` rule below).
- After deployment, write the final paths to a log file so the verifier can find them.

## Implementation Hints
- Read the `run-id` from the `ZEALT_RUN_ID` environment variable. Use it as a folder-name suffix when laying out the assets on disk and when pushing them, so concurrent runs do not collide. For example: tool script at `f/agent_${run_id}/lookup_sku` and flow at `f/agent_${run_id}/price_agent`.
- The Windmill CLI is preinstalled. The cloud workspace is already added as the default profile (token in `WMILL_TOKEN`, workspace id in `WMILL_WORKSPACE`, base URL `https://app.windmill.dev`). Use `wmill sync push --yes` from the workspace root to deploy.
- Each Windmill script lives as a pair of files on disk: a source file and a `.script.yaml` metadata file. Each flow lives as a folder containing a `flow.yaml`. The YAML structure for AI Agent steps is the documented `value.type: aiagent` form with `input_transforms`, `tools`, and optionally `tag` and `omit_output_from_conversation`. Each tool entry has an `id`, optional `summary`, and a `value` whose `tool_type` is one of `flowmodule`, `mcp`, or `websearch`.
- The agent step's `input_transforms.output_schema` must be a static JSON schema object — the AI Agent will then return its `output` field conforming to that schema.
- The cloud workspace already exposes a default AI provider, so configuring `input_transforms.provider` against the workspace-default AI resource is sufficient; the verifier will not check which model name you chose.
- Invoking the flow is done with the documented synchronous-result endpoint `POST https://app.windmill.dev/api/w/{workspace}/jobs/run_wait_result/f/{flow_path}` with a JSON body containing the flow's inputs and the `Authorization: Bearer $WMILL_TOKEN` header.

## Acceptance Criteria
- Project path: /home/user/wm-agent
- Ensure the assets are really deployed to the cloud workspace; the verifier will call the cloud Windmill API directly.
- Log file: /home/user/wm-agent/deploy.log
- The log file MUST contain two lines in the exact format:
  - `Tool script path: <full f/... path of the deployed tool script>`
  - `Flow path: <full f/... path of the deployed AI agent flow>`
- The deployed flow's first module MUST be an AI Agent step (`value.type` equals `aiagent`) and MUST include a non-empty `tools` array referencing the deployed tool script (via `tool_type: flowmodule` + `type: script` + matching `path`) or an equivalent documented MCP tool entry.
- The AI Agent step MUST declare a static `output_schema` under `input_transforms.output_schema` whose schema requires at least the fields `sku` (string), `unit_price` (number), and `currency` (string).
- Calling `POST https://app.windmill.dev/api/w/${WMILL_WORKSPACE}/jobs/run_wait_result/f/<flow_path>` with header `Authorization: Bearer ${WMILL_TOKEN}` and JSON body `{"prompt": "Look up the unit price for SKU WIDGET-42 and reply with the structured answer."}` MUST return HTTP 200 and a JSON result whose agent-output payload validates against the declared `output_schema` (the verifier accepts either `result.output` or `result` itself as the validated payload).
- Folder/path prefix MUST embed the run-id: `f/agent_${run_id}/...` where `${run_id}` is read from `ZEALT_RUN_ID`.

