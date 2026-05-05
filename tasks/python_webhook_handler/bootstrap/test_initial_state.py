import os
import shutil
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill binary not found in PATH."


def test_python3_binary_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_scripts_directory_exists():
    assert os.path.isdir(SCRIPTS_DIR)


def test_handle_webhook_py_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "handle_webhook.py")), \
        "handle_webhook.py already exists — agent must create it."


def test_handle_webhook_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "handle_webhook.script.yaml")), \
        "handle_webhook.script.yaml already exists — agent must create it."
