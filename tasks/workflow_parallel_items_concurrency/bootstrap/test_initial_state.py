import os
import shutil


def test_wmill_binary_in_path():
    """wmill CLI binary must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. Ensure windmill-cli is installed (npm install -g windmill-cli)."
    )


def test_windmill_project_directory_exists():
    """The /home/user/windmill-project directory must exist."""
    project_dir = "/home/user/windmill-project"
    assert os.path.isdir(project_dir), (
        f"Expected directory '{project_dir}' does not exist."
    )


def test_workflows_directory_exists():
    """The /home/user/windmill-project/f/workflows directory must exist."""
    workflows_dir = "/home/user/windmill-project/f/workflows"
    assert os.path.isdir(workflows_dir), (
        f"Expected directory '{workflows_dir}' does not exist."
    )


def test_batch_processor_does_not_exist():
    """The batch_processor.ts file must NOT exist yet — the user must create it."""
    target_file = "/home/user/windmill-project/f/workflows/batch_processor.ts"
    assert not os.path.exists(target_file), (
        f"File '{target_file}' already exists. It should be absent at the start of the task."
    )
