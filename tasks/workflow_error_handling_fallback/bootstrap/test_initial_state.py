import os
import shutil
import subprocess


def test_wmill_binary_in_path():
    """wmill binary must be accessible in PATH."""
    assert shutil.which("wmill") is not None, "wmill binary not found in PATH"


def test_windmill_project_directory_exists():
    """The windmill project directory must exist at /home/user/windmill-project."""
    assert os.path.isdir("/home/user/windmill-project"), (
        "/home/user/windmill-project directory does not exist"
    )


def test_data_pipeline_file_exists():
    """The data_pipeline.ts workflow file must exist."""
    assert os.path.isfile(
        "/home/user/windmill-project/f/workflows/data_pipeline.ts"
    ), "/home/user/windmill-project/f/workflows/data_pipeline.ts does not exist"


def test_file_does_not_have_try_block():
    """The file must NOT already contain a try block (initial broken state)."""
    with open(
        "/home/user/windmill-project/f/workflows/data_pipeline.ts", "r"
    ) as f:
        content = f.read()
    assert "try {" not in content and "try{" not in content, (
        "data_pipeline.ts already contains a try block — initial state is incorrect"
    )


def test_file_contains_fetch_data_task_call():
    """The file must contain task(fetchData) call."""
    with open(
        "/home/user/windmill-project/f/workflows/data_pipeline.ts", "r"
    ) as f:
        content = f.read()
    assert "task(fetchData)" in content, (
        "data_pipeline.ts does not contain task(fetchData) call"
    )


def test_file_contains_fallback_data_function():
    """The file must contain the fallbackData function definition."""
    with open(
        "/home/user/windmill-project/f/workflows/data_pipeline.ts", "r"
    ) as f:
        content = f.read()
    assert "fallbackData" in content, (
        "data_pipeline.ts does not contain a fallbackData function definition"
    )


def test_file_contains_transform_task_call():
    """The file must contain the task(transform) call."""
    with open(
        "/home/user/windmill-project/f/workflows/data_pipeline.ts", "r"
    ) as f:
        content = f.read()
    assert "task(transform)" in content, (
        "data_pipeline.ts does not contain task(transform) call"
    )


def test_file_contains_main_export():
    """The file must export a main workflow function."""
    with open(
        "/home/user/windmill-project/f/workflows/data_pipeline.ts", "r"
    ) as f:
        content = f.read()
    assert "export const main" in content, (
        "data_pipeline.ts does not contain 'export const main'"
    )
