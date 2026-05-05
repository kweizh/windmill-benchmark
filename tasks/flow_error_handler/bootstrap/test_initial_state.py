import os
import shutil
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill binary not found in PATH."


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_scripts_directory_exists():
    assert os.path.isdir(SCRIPTS_DIR)


def test_risky_operation_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "risky_operation.ts")), \
        "risky_operation.ts already exists — agent must create it."


def test_handle_error_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "handle_error.ts")), \
        "handle_error.ts already exists — agent must create it."


def test_flow_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(FLOWS_DIR, "resilient_pipeline.yaml")), \
        "resilient_pipeline.yaml already exists — agent must create it."
