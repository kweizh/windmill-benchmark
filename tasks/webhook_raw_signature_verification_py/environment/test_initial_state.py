import os
import shutil

import pytest


PROJECT_DIR = "/home/user/wmtask"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "The 'wmill' CLI binary is not available in PATH; the Windmill CLI must be "
        "pre-installed in the evaluation image."
    )


def test_python_available():
    assert shutil.which("python3") is not None, (
        "python3 is not available in PATH; it is required to author the Windmill script."
    )


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected the project directory {PROJECT_DIR} to already exist for the executor "
        "to work in, but it does not."
    )


def test_wm_token_env_present():
    token = os.environ.get("WM_TOKEN")
    assert token, (
        "WM_TOKEN environment variable is not set. The Windmill cloud API token must be "
        "provided so the executor can authenticate against https://app.windmill.dev."
    )


def test_wm_workspace_env_present():
    ws = os.environ.get("WM_WORKSPACE")
    assert ws, (
        "WM_WORKSPACE environment variable is not set. The Windmill cloud workspace id "
        "must be provided so the executor can deploy assets there."
    )


def test_zealt_run_id_env_present():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, (
        "ZEALT_RUN_ID environment variable is not set. It is required to scope deployed "
        "Windmill assets so concurrent evaluation runs do not collide."
    )


def test_requests_importable():
    # The final-state verifier uses 'requests' to call the Windmill HTTP API, so it must
    # be importable in the verification environment.
    pytest.importorskip("requests")
