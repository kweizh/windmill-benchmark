import os
import shutil

PROJECT_DIR = "/home/user/project"


def test_wmill_cli_available():
    """The wmill CLI must be installed and on PATH before the executor starts."""
    assert shutil.which("wmill") is not None, (
        "wmill CLI binary not found in PATH. Install windmill-cli via npm before evaluation."
    )


def test_project_directory_exists():
    """The project root that the executor will work in must already exist."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory at {PROJECT_DIR} to exist before evaluation."
    )


def test_wmill_token_available():
    """The executor needs a Windmill API token to authenticate against the cloud workspace."""
    token = os.environ.get("WMILL_TOKEN")
    assert token, (
        "Environment variable WMILL_TOKEN must be set to a valid cloud Windmill API token."
    )


def test_zealt_run_id_available():
    """run-id must be exposed so the executor can isolate resource names per evaluation run."""
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "Environment variable ZEALT_RUN_ID must be set so the executor can build a unique remote path."
    )
