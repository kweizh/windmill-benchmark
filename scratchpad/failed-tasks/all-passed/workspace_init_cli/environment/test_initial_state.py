import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH; Node.js is required to install and run "
        "windmill-cli."
    )


def test_npm_available():
    assert shutil.which("npm") is not None, (
        "npm binary not found in PATH; npm is required to install windmill-cli."
    )


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH; the windmill-cli must be preinstalled "
        "(e.g. via 'npm install -g windmill-cli')."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist; the task expects an "
        "empty Windmill project root to be present."
    )


def test_wmill_yaml_not_yet_present():
    # The agent is the one responsible for producing wmill.yaml via `wmill init`.
    # If the file already exists at the start, the initial environment is
    # mis-configured for this task.
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert not os.path.exists(wmill_yaml), (
        f"{wmill_yaml} should NOT exist before the task starts; the agent must "
        "create it via `wmill init`."
    )
