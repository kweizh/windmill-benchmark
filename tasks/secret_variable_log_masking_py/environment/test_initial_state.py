import os
import shutil

PROJECT_DIR = "/home/user/myproject"


def test_wmill_cli_available():
    assert shutil.which("wmill") is not None, (
        "wmill CLI not found in PATH. The Windmill CLI must be installed in the image."
    )


def test_python_wmill_sdk_importable():
    # The wmill Python SDK is required by the script the executor will write.
    try:
        import wmill  # noqa: F401
    except Exception as e:  # pragma: no cover - exact exception varies
        raise AssertionError(
            f"The Windmill Python SDK (wmill) must be importable in the task environment; got: {e!r}"
        )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist. The task environment must pre-create it."
    )


def test_project_directory_is_empty_workspace():
    # The executor is expected to bootstrap wmill.yaml themselves, so the project
    # directory must start without one.
    wmill_yaml = os.path.join(PROJECT_DIR, "wmill.yaml")
    assert not os.path.exists(wmill_yaml), (
        f"{wmill_yaml} must NOT exist before the task begins; the executor bootstraps it."
    )


def test_required_env_vars_present():
    for key in ("WMILL_BASE_URL", "WMILL_WORKSPACE", "WMILL_TOKEN", "ZEALT_RUN_ID"):
        assert os.environ.get(key), (
            f"Environment variable {key} must be set before the task starts."
        )
