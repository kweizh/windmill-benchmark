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
    assert os.path.isdir(SCRIPTS_DIR), f"Scripts directory '{SCRIPTS_DIR}' does not exist."


def test_check_score_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "check_score.ts")), \
        "check_score.ts already exists — agent must create it."


def test_on_pass_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "on_pass.ts")), \
        "on_pass.ts already exists — agent must create it."


def test_on_fail_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "on_fail.ts")), \
        "on_fail.ts already exists — agent must create it."


def test_flow_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(FLOWS_DIR, "score_check.yaml")), \
        "score_check.yaml already exists — agent must create it."
