import os
import shutil
import pytest

PROJECT_DIR = "/home/user/windmill-project"
WORKFLOWS_DIR = os.path.join(PROJECT_DIR, "f", "workflows")
ETL_FILE = os.path.join(WORKFLOWS_DIR, "etl_pipeline.py")

def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill CLI binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflows_directory_exists():
    assert os.path.isdir(WORKFLOWS_DIR), f"Workflows directory {WORKFLOWS_DIR} does not exist."

def test_etl_pipeline_file_does_not_exist():
    assert not os.path.isfile(ETL_FILE), \
        f"etl_pipeline.py already exists at {ETL_FILE} — expected it to be absent before the task."
