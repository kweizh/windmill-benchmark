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


def test_generate_message_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "generate_message.ts")), \
        "generate_message.ts already exists — agent must create it."


def test_wrap_message_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "wrap_message.ts")), \
        "wrap_message.ts already exists — agent must create it."


def test_flow_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(FLOWS_DIR, "greet_and_wrap.yaml")), \
        "greet_and_wrap.yaml already exists — agent must create it."
