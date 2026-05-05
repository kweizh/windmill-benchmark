import os
import shutil
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill binary not found in PATH."


def test_python3_binary_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_scripts_directory_exists():
    assert os.path.isdir(SCRIPTS_DIR), f"Scripts directory '{SCRIPTS_DIR}' does not exist."


def test_parse_event_py_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "parse_event.py")), \
        "parse_event.py already exists — agent must create it."


def test_parse_event_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "parse_event.script.yaml")), \
        "parse_event.script.yaml already exists — agent must create it."
