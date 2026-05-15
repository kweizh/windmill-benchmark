import os
import shutil


def test_wmill_cli_in_path():
    """wmill CLI binary must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill CLI not found in PATH. Ensure the windmill npm package is installed."
    )


def test_windmill_project_directory_exists():
    """The /home/user/windmill-project directory must exist."""
    assert os.path.isdir("/home/user/windmill-project"), (
        "/home/user/windmill-project directory does not exist."
    )


def test_workflows_directory_exists():
    """The /home/user/windmill-project/f/workflows directory must exist."""
    assert os.path.isdir("/home/user/windmill-project/f/workflows"), (
        "/home/user/windmill-project/f/workflows directory does not exist."
    )


def test_url_monitor_file_does_not_exist():
    """url_monitor.py must NOT exist yet — the user is expected to create it."""
    assert not os.path.exists(
        "/home/user/windmill-project/f/workflows/url_monitor.py"
    ), (
        "/home/user/windmill-project/f/workflows/url_monitor.py already exists "
        "but should be absent before the task is attempted."
    )
