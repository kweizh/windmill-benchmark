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


def test_batch_process_py_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "batch_process.py")), \
        "batch_process.py already exists — agent must create it."


def test_batch_process_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(SCRIPTS_DIR, "batch_process.script.yaml")), \
        "batch_process.script.yaml already exists — agent must create it."
