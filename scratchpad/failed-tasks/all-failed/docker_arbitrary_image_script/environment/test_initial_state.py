"""Initial-state checks for the docker_arbitrary_image_script Windmill task.

The task targets the cloud-hosted Windmill instance at https://app.windmill.dev,
so the only pre-existing state is:

- The ``wmill`` CLI binary on PATH.
- The bare project directory at ``/home/user/myproject`` (empty).
- A valid Windmill cloud bearer token and workspace id exposed via the
  ``WINDMILL_TOKEN`` and ``WINDMILL_WORKSPACE`` environment variables.

The executor is responsible for everything else (workspace registration, file
authoring, deployment, execution, log file production).
"""

from __future__ import annotations

import os
import shutil

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
WINDMILL_BASE_URL = "https://app.windmill.dev"


def test_wmill_cli_available() -> None:
    """The ``wmill`` CLI must be installed on PATH."""
    assert shutil.which("wmill") is not None, (
        "`wmill` CLI binary not found on PATH. The Windmill CLI is required to "
        "deploy assets to https://app.windmill.dev."
    )


def test_project_dir_exists() -> None:
    """The project root must exist and be a directory."""
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. "
        "The task expects to author and deploy a Windmill Docker script from this folder."
    )


def test_windmill_token_env_var_set() -> None:
    """A non-empty Windmill bearer token must be available for cloud authentication."""
    token = os.environ.get("WINDMILL_TOKEN", "").strip()
    assert token, (
        "WINDMILL_TOKEN environment variable must be set to a non-empty Windmill cloud "
        "API token so the wmill CLI can authenticate against https://app.windmill.dev."
    )


def test_windmill_workspace_env_var_set() -> None:
    """A non-empty Windmill workspace id must be available."""
    workspace = os.environ.get("WINDMILL_WORKSPACE", "").strip()
    assert workspace, (
        "WINDMILL_WORKSPACE environment variable must be set to the cloud workspace id "
        "the task will deploy into."
    )


def test_windmill_cloud_reachable_with_token() -> None:
    """Confirm the supplied token can reach the cloud workspace API."""
    token = os.environ.get("WINDMILL_TOKEN", "").strip()
    workspace = os.environ.get("WINDMILL_WORKSPACE", "").strip()
    assert token and workspace, (
        "WINDMILL_TOKEN and WINDMILL_WORKSPACE must be set for this check; see prior tests."
    )
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/scripts/list"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    assert response.status_code != 401, (
        "WINDMILL_TOKEN is unauthorized against https://app.windmill.dev (HTTP 401). "
        "Provide a valid Windmill cloud API token."
    )
    assert response.status_code != 403, (
        "WINDMILL_TOKEN does not have access to the requested workspace (HTTP 403). "
        f"Workspace id: {workspace!r}."
    )
    assert response.status_code < 500, (
        f"Windmill cloud API returned a server error ({response.status_code}) for "
        f"workspace {workspace!r}: {response.text[:300]}"
    )
