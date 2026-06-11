import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_node_available():
    assert shutil.which("node") is not None, (
        "node binary not found in PATH; Node.js is required to install windmill-cli."
    )


def test_npm_available():
    assert shutil.which("npm") is not None, (
        "npm binary not found in PATH; npm is required to install windmill-cli."
    )


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH; install via 'npm install -g windmill-cli'."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_windmill_token_env():
    assert os.environ.get("WINDMILL_TOKEN"), (
        "WINDMILL_TOKEN environment variable must be set to authenticate against "
        "https://app.windmill.dev."
    )


def test_windmill_workspace_env():
    assert os.environ.get("WINDMILL_WORKSPACE"), (
        "WINDMILL_WORKSPACE environment variable must be set to identify the cloud "
        "workspace on https://app.windmill.dev."
    )
