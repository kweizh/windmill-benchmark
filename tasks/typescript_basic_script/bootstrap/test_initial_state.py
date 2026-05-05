import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/windmill-project"
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "f", "scripts")


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. "
        "Install it with: npm install -g windmill-cli"
    )


def test_node_binary_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH. Node.js v20+ is required."
    )


def test_wmill_version():
    result = subprocess.run(
        ["wmill", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"'wmill --version' failed with return code {result.returncode}: {result.stderr}"
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory '{PROJECT_DIR}' does not exist. "
        "It should have been created by the environment setup."
    )


def test_scripts_directory_exists():
    assert os.path.isdir(SCRIPTS_DIR), (
        f"Scripts directory '{SCRIPTS_DIR}' does not exist. "
        "It should have been created by the environment setup."
    )


def test_greet_ts_does_not_exist_yet():
    greet_ts = os.path.join(SCRIPTS_DIR, "greet.ts")
    assert not os.path.exists(greet_ts), (
        f"'{greet_ts}' already exists before the task — "
        "the agent should be the one creating it."
    )


def test_greet_script_yaml_does_not_exist_yet():
    greet_yaml = os.path.join(SCRIPTS_DIR, "greet.script.yaml")
    assert not os.path.exists(greet_yaml), (
        f"'{greet_yaml}' already exists before the task — "
        "the agent should be the one creating it."
    )
