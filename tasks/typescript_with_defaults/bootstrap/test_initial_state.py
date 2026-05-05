import os
import shutil
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill binary not found in PATH."


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_scripts_directory_exists():
    assert os.path.isdir(SCRIPTS_DIR), f"Scripts directory '{SCRIPTS_DIR}' does not exist."


def test_format_price_ts_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "format_price.ts")), \
        "format_price.ts already exists — agent must create it."


def test_format_price_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "format_price.script.yaml")), \
        "format_price.script.yaml already exists — agent must create it."
