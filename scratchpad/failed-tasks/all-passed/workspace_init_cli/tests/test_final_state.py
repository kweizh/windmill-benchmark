import os

import pytest
import yaml

PROJECT_DIR = "/home/user/myproject"
WMILL_YAML = os.path.join(PROJECT_DIR, "wmill.yaml")


@pytest.fixture(scope="module")
def wmill_yaml_text() -> str:
    assert os.path.isfile(WMILL_YAML), (
        f"Expected `wmill.yaml` at {WMILL_YAML} after running `wmill init`, but "
        "the file does not exist or is not a regular file."
    )
    with open(WMILL_YAML, "r", encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def wmill_yaml_parsed(wmill_yaml_text: str):
    try:
        parsed = yaml.safe_load(wmill_yaml_text)
    except yaml.YAMLError as exc:
        pytest.fail(
            f"`wmill.yaml` at {WMILL_YAML} is not valid YAML and failed to parse: "
            f"{exc}"
        )
    return parsed


def test_wmill_yaml_exists():
    assert os.path.isfile(WMILL_YAML), (
        f"Expected `wmill.yaml` to be created at {WMILL_YAML} by `wmill init`, "
        "but no regular file was found there."
    )


def test_wmill_yaml_non_empty(wmill_yaml_text: str):
    assert wmill_yaml_text.strip(), (
        f"`wmill.yaml` at {WMILL_YAML} exists but is empty; `wmill init` should "
        "have populated it with a default configuration."
    )


def test_wmill_yaml_parses_as_mapping(wmill_yaml_parsed):
    assert isinstance(wmill_yaml_parsed, dict), (
        "Expected the top level of `wmill.yaml` to parse as a YAML mapping "
        f"(dict), but got: {type(wmill_yaml_parsed).__name__}."
    )


def test_wmill_yaml_has_includes_key(wmill_yaml_parsed):
    assert isinstance(wmill_yaml_parsed, dict) and "includes" in wmill_yaml_parsed, (
        "Expected `wmill.yaml` to contain a top-level `includes` key as "
        "documented for the file produced by `wmill init`. See "
        "https://www.windmill.dev/docs/advanced/cli/wmill-yaml-reference."
    )


def test_wmill_yaml_has_excludes_key(wmill_yaml_parsed):
    assert isinstance(wmill_yaml_parsed, dict) and "excludes" in wmill_yaml_parsed, (
        "Expected `wmill.yaml` to contain a top-level `excludes` key as "
        "documented for the file produced by `wmill init`. See "
        "https://www.windmill.dev/docs/advanced/cli/wmill-yaml-reference."
    )
