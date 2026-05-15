import os
import shutil
from pathlib import Path

PROJECT_DIR = Path("/home/user/windmill-project")
WORKFLOWS_DIR = PROJECT_DIR / "f" / "workflows"
TARGET_FILE = WORKFLOWS_DIR / "cached_enricher.ts"


def test_wmill_binary_in_path():
    """wmill CLI binary must be available in PATH."""
    assert shutil.which("wmill") is not None, (
        "wmill binary not found in PATH. Ensure windmill-cli is installed (npm install -g windmill-cli)."
    )


def test_windmill_project_directory_exists():
    """The /home/user/windmill-project directory must exist."""
    assert PROJECT_DIR.is_dir(), (
        f"Expected directory '{PROJECT_DIR}' does not exist."
    )


def test_workflows_directory_exists():
    """The /home/user/windmill-project/f/workflows directory must exist."""
    assert WORKFLOWS_DIR.is_dir(), (
        f"Expected directory '{WORKFLOWS_DIR}' does not exist."
    )


def test_cached_enricher_file_exists():
    """The cached_enricher.ts file must exist — it is the broken file to be fixed."""
    assert TARGET_FILE.is_file(), (
        f"File '{TARGET_FILE}' does not exist. "
        "The broken workflow file should be present at the start of the task."
    )


def test_file_does_not_contain_cache_ttl():
    """The file must NOT contain 'cache_ttl' in the initial broken state."""
    content = TARGET_FILE.read_text(encoding="utf-8")
    assert "cache_ttl" not in content, (
        f"File '{TARGET_FILE}' already contains 'cache_ttl'. "
        "The initial state must be the broken version without caching."
    )


def test_file_contains_task_enrich_record():
    """The file must contain a 'task(enrichRecord)' call — the broken pattern to fix."""
    content = TARGET_FILE.read_text(encoding="utf-8")
    assert "task(enrichRecord)" in content, (
        f"File '{TARGET_FILE}' does not contain 'task(enrichRecord)'. "
        "The initial broken workflow must call enrichRecord without cache_ttl."
    )
