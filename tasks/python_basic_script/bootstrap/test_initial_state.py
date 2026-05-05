import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/windmill-project"
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "f", "scripts")


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill binary not found in PATH."


def test_python3_binary_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory '{PROJECT_DIR}' does not exist."


def test_scripts_directory_exists():
    assert os.path.isdir(SCRIPTS_DIR), f"Scripts directory '{SCRIPTS_DIR}' does not exist."


def test_hello_py_does_not_exist_yet():
    target = os.path.join(SCRIPTS_DIR, "hello.py")
    assert not os.path.exists(target), f"'{target}' already exists — agent must create it."


def test_hello_script_yaml_does_not_exist_yet():
    target = os.path.join(SCRIPTS_DIR, "hello.script.yaml")
    assert not os.path.exists(target), f"'{target}' already exists — agent must create it."
