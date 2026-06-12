# Windmill Python Script with Pydantic Input Validation

## Background
Windmill is a code-first developer platform that runs Python scripts on a cloud runtime. Python scripts in Windmill expose a single `main` function whose argument signature drives both the generated JSON Schema and the runtime input validation. When a parameter is annotated with a [Pydantic `BaseModel`](https://www.windmill.dev/docs/getting_started/scripts_quickstart/python#pydantic-and-dataclass-support), Windmill instantiates the model from the incoming payload, so any payload that violates the model definition fails fast.

The `wmill` CLI is already authenticated against the cloud workspace at `https://app.windmill.dev`. You will author a Python script that uses a Pydantic `BaseModel` as the input type, deploy it to the cloud workspace, and exercise it twice through `wmill script run` — once with a valid payload and once with a payload that violates the model.

## Requirements
- Read `run-id` from the `ZEALT_RUN_ID` environment variable and append it to the script's remote path so parallel evaluation runs do not collide.
- Author a Python Windmill script under the project root at `/home/user/project` whose remote path is `f/zealt/pydantic_input_${run-id}` (i.e. the local file pair is `f/zealt/pydantic_input_${run-id}.py` and `f/zealt/pydantic_input_${run-id}.script.yaml`).
- Define a Pydantic `BaseModel` named `Order` with the following required fields:
  - `item`: `str`
  - `quantity`: `int`
  - `unit_price`: `float`
- The `main` function must take a single argument `data: Order` and return a JSON object containing the fields `item` (echo of `data.item`) and `total` (numeric value equal to `data.quantity * data.unit_price`).
- Deploy the script to the cloud workspace via the `wmill` CLI before invoking it.
- Invoke the deployed script with the `wmill script run` command using both a valid payload and an invalid payload, demonstrating that Pydantic validation rejects the invalid one.

## Implementation Hints
- Install the CLI from npm and authenticate it against the cloud workspace using the `WMILL_TOKEN` environment variable, then add a workspace pointing at `https://app.windmill.dev`.
- Refer to the [Python quickstart](https://www.windmill.dev/docs/getting_started/scripts_quickstart/python) for the structure of `<path>.py` + `<path>.script.yaml` file pairs.
- A Python file can be deployed individually using [`wmill script push <local_path>`](https://www.windmill.dev/docs/advanced/cli/script#pushing-a-script); the metadata file at `<path>.script.yaml` is generated/regenerated automatically by `wmill generate-metadata <path>` if it is missing or stale.
- A deployed script is invoked via [`wmill script run <remote_path> -d '<json>'`](https://www.windmill.dev/docs/advanced/cli/script#running-a-script). The payload's top-level keys must match the `main` function's parameter names.
- A payload that violates the Pydantic model surfaces as a script error: the CLI exits with a non-zero status and the error output mentions the validation failure.

## Acceptance Criteria
- Project path: `/home/user/project`
- Command (deploy + run): `wmill` CLI executed from `/home/user/project`
- Remote script path: `f/zealt/pydantic_input_${run-id}` where `${run-id}` is the value of `ZEALT_RUN_ID`.
- File pair on disk (relative to the project path):
  - `f/zealt/pydantic_input_${run-id}.py`
  - `f/zealt/pydantic_input_${run-id}.script.yaml`
- Script signature:
  - `class Order(BaseModel)` with required fields `item: str`, `quantity: int`, `unit_price: float`.
  - `def main(data: Order)` returning a JSON object that includes the keys `item` (string) and `total` (number equal to `quantity * unit_price`).
- Valid invocation behavior: `wmill script run f/zealt/pydantic_input_${run-id} -d '<valid_json>'` exits with status `0` and prints a JSON object containing the expected `item` and `total` values.
- Invalid invocation behavior: `wmill script run f/zealt/pydantic_input_${run-id} -d '<invalid_json>'` either exits with a non-zero status or surfaces an error result indicating the input was rejected. Do not enforce a specific error message wording.

