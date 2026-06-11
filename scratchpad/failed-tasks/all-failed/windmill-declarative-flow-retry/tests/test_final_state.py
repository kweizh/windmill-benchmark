import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml


PROJECT_DIR = "/home/user/windmill-project"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
WINDMILL_BASE_URL = "https://app.windmill.dev"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable must be set for verification."
    return run_id


def _safe_id() -> str:
    return _run_id().replace("-", "_")


def _folder() -> str:
    return f"f/eval_{_safe_id()}"


def _windmill_env() -> dict:
    env = os.environ.copy()
    token = env.get("WINDMILL_TOKEN")
    workspace = env.get("WINDMILL_WORKSPACE")
    assert token, "WINDMILL_TOKEN env var must be set for verification."
    assert workspace, "WINDMILL_WORKSPACE env var must be set for verification."
    return env


def _find_flow_yaml() -> Path:
    """Locate the declarative flow's flow.yaml on disk under either layout."""
    folder = Path(PROJECT_DIR) / "f" / f"eval_{_safe_id()}"
    candidates = [
        folder / "retry_pipeline.flow" / "flow.yaml",
        folder / "retry_pipeline__flow" / "flow.yaml",
    ]
    for c in candidates:
        if c.is_file():
            return c
    # Fall back to recursive search just in case the executor used a non-default layout.
    matches = list(folder.rglob("flow.yaml"))
    assert matches, (
        f"No flow.yaml found under {folder}. Expected one of: "
        f"{[str(c) for c in candidates]}"
    )
    return matches[0]


def test_flaky_step_script_file_exists():
    py_path = Path(PROJECT_DIR) / "f" / f"eval_{_safe_id()}" / "flaky_step.py"
    assert py_path.is_file(), (
        f"Expected Python script file at {py_path}; the declarative `f/eval_<run>/flaky_step` "
        "script must be authored on disk as `<name>.py`."
    )


def test_finalize_script_file_exists():
    py_path = Path(PROJECT_DIR) / "f" / f"eval_{_safe_id()}" / "finalize.py"
    assert py_path.is_file(), (
        f"Expected Python script file at {py_path}; the declarative `f/eval_<run>/finalize` "
        "script must be authored on disk as `<name>.py`."
    )


def test_flow_yaml_exists_at_documented_layout():
    flow_yaml = _find_flow_yaml()
    assert flow_yaml.is_file(), f"flow.yaml not found at {flow_yaml}."


def test_flow_yaml_retry_exponential_exact_values():
    flow_yaml_path = _find_flow_yaml()
    data = yaml.safe_load(flow_yaml_path.read_text())
    assert isinstance(data, dict), f"flow.yaml must parse as a mapping, got {type(data)}"

    # The OpenFlow root may expose modules directly under `value.modules` (Windmill default)
    # or directly under `modules`. Accept both.
    flow_value = data.get("value", data)
    assert isinstance(flow_value, dict), "OpenFlow `value` block must be a mapping."
    modules = flow_value.get("modules")
    assert isinstance(modules, list) and len(modules) >= 2, (
        "flow.yaml must declare at least two modules in `value.modules`."
    )

    first_module = modules[0]
    retry = first_module.get("retry")
    assert isinstance(retry, dict), (
        "The first module must declare a `retry` policy. Got: "
        f"{retry!r} (full module: {first_module!r})"
    )
    expo = retry.get("exponential")
    assert isinstance(expo, dict), (
        "First module's retry must use the `exponential` strategy "
        f"with fields attempts/multiplier/seconds. Got: {retry!r}"
    )
    assert expo.get("attempts") == 4, (
        f"retry.exponential.attempts must equal 4, got {expo.get('attempts')!r}"
    )
    assert expo.get("multiplier") == 2, (
        f"retry.exponential.multiplier must equal 2, got {expo.get('multiplier')!r}"
    )
    assert expo.get("seconds") == 1, (
        f"retry.exponential.seconds must equal 1, got {expo.get('seconds')!r}"
    )


def test_flow_yaml_finalize_input_transform_references_flaky_result():
    flow_yaml_path = _find_flow_yaml()
    data = yaml.safe_load(flow_yaml_path.read_text())
    flow_value = data.get("value", data)
    modules = flow_value["modules"]
    second_module = modules[1]
    # Module's script value may live directly under `value` or be the module itself.
    module_value = second_module.get("value", second_module)
    input_transforms = module_value.get("input_transforms")
    assert isinstance(input_transforms, dict), (
        "Second module must declare `input_transforms`. Got: "
        f"{module_value!r}"
    )
    previous = input_transforms.get("previous")
    assert isinstance(previous, dict), (
        "Second module's input_transforms must contain a `previous` entry. Got: "
        f"{input_transforms!r}"
    )
    assert previous.get("type") == "javascript", (
        "`previous` must be a JavaScript input transform "
        f"(type=javascript). Got: {previous!r}"
    )
    expr = previous.get("expr", "")
    assert isinstance(expr, str) and "results.flaky" in expr, (
        "`previous.expr` must reference `results.flaky` to pipe the first module's "
        f"output to the finalize step. Got: {expr!r}"
    )


def test_output_log_contains_flow_result():
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}."
    content = Path(LOG_FILE).read_text()

    # Find the JSON portion following "Flow result:".
    match = re.search(r"Flow result:\s*(\{.*\})", content)
    assert match, (
        "Log file must contain a line beginning with 'Flow result:' followed by the "
        f"JSON result of the flow run. Got contents:\n{content}"
    )
    parsed = json.loads(match.group(1))
    expected = {"final": True, "previous_attempt": 3}
    assert parsed == expected, (
        f"Flow result must equal {expected}, got {parsed} (raw match: {match.group(1)!r})."
    )


def test_flaky_counter_variable_equals_three():
    """Use the wmill CLI to read the variable; confirms exactly 3 attempts ran."""
    env = _windmill_env()
    token = env["WINDMILL_TOKEN"]
    workspace = env["WINDMILL_WORKSPACE"]
    var_path = f"{_folder()}/flaky_counter"

    result = subprocess.run(
        [
            "wmill",
            "variable",
            "get",
            var_path,
            "--token",
            token,
            "--workspace",
            workspace,
            "--base-url",
            WINDMILL_BASE_URL,
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, (
        f"`wmill variable get {var_path}` failed: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )
    # The CLI typically prints the variable value (potentially with surrounding quotes
    # or label). Extract the digits and compare against "3".
    stdout = result.stdout.strip()
    digits = re.findall(r"-?\d+", stdout)
    assert digits, (
        f"Could not find an integer in `wmill variable get` output: {stdout!r}"
    )
    # The final integer printed is the variable value.
    assert digits[-1] == "3", (
        f"Expected `flaky_counter` variable to equal '3' after the flow run "
        f"(exactly three attempts), got {digits[-1]!r} (full output: {stdout!r})."
    )


def test_finalize_script_deployed_and_callable():
    """Sanity check that the finalize script was deployed to the cloud workspace."""
    env = _windmill_env()
    token = env["WINDMILL_TOKEN"]
    workspace = env["WINDMILL_WORKSPACE"]
    script_path = f"{_folder()}/finalize"

    result = subprocess.run(
        [
            "wmill",
            "script",
            "run",
            script_path,
            "-d",
            json.dumps({"previous": {"ok": True, "attempt": 3}}),
            "--silent",
            "--token",
            token,
            "--workspace",
            workspace,
            "--base-url",
            WINDMILL_BASE_URL,
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"`wmill script run {script_path}` failed: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )

    # Parse the JSON result out of stdout (--silent prints only the result).
    raw = result.stdout.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        assert match, f"Could not extract JSON result from output: {raw!r}"
        parsed = json.loads(match.group(0))

    assert parsed == {"final": True, "previous_attempt": 3}, (
        f"finalize script must return {{'final': true, 'previous_attempt': 3}}, "
        f"got {parsed!r}"
    )
