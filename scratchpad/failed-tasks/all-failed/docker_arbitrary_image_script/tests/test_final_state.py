"""Final-state checks for the docker_arbitrary_image_script Windmill task.

The verifier ensures the executor:
    * authored a Windmill sandboxed Docker script on disk with the documented
      ``# sandbox alpine:3`` annotation (rejecting the legacy ``# docker``),
    * declared the script in ``<name>.script.yaml`` with the canonical
      Windmill ``language: bash`` identifier (no separate ``docker`` language
      exists in the Windmill ScriptLang enum),
    * deployed it to the cloud workspace at https://app.windmill.dev,
    * remotely executed it once and persisted the result to ``output.log``,
    * produced the exact stdout-derived JSON result string when re-invoked by
      the verifier against the cloud workspace.

No assertions about cold-start latency are made; only the script declaration,
deployment, and execution result are checked.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable

import pytest
import requests
import yaml

PROJECT_DIR = "/home/user/myproject"
WINDMILL_BASE_URL = "https://app.windmill.dev"

# Windmill's officially documented file-extension table for shell scripts is
# ``.sh`` (per https://www.windmill.dev/docs/advanced/local_development).
# The Docker quickstart page mentions ``.docker`` as an additional possible
# extension; accept either, since the canonical language is still ``bash``.
SCRIPT_EXTENSIONS: tuple[str, ...] = (".sh", ".docker")

# The Windmill ScriptLang enum (backend/windmill-types/src/scripts.rs) does NOT
# include ``docker``. The canonical identifier for sandboxed Docker scripts is
# ``bash``, since the body is dispatched to the image's ``/bin/sh -c``.
EXPECTED_LANGUAGE = "bash"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    assert value, f"{name} environment variable must be set."
    return value


def _ids() -> tuple[str, str, str, str, str]:
    run_id = _env("ZEALT_RUN_ID")
    safe_id = run_id.replace("-", "_")
    script_path = f"f/docker_{safe_id}/hello_alpine"
    expected_message = f"harbor-{run_id}"
    expected_result = f"hello {expected_message} from Alpine Linux"
    return run_id, safe_id, script_path, expected_message, expected_result


def _local_script_files(safe_id: str) -> dict[str, Path]:
    folder = Path(PROJECT_DIR) / "f" / f"docker_{safe_id}"
    content_files: list[Path] = []
    if folder.is_dir():
        for entry in folder.iterdir():
            if not entry.is_file():
                continue
            if entry.name.startswith("hello_alpine.") and any(
                entry.name.endswith(ext) for ext in SCRIPT_EXTENSIONS
            ):
                content_files.append(entry)
    metadata_file = folder / "hello_alpine.script.yaml"
    return {"folder": folder, "content_files": content_files, "metadata": metadata_file}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _stripped_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def _has_sandbox_alpine3_line(lines: Iterable[str]) -> bool:
    pattern = re.compile(r"^#\s*sandbox\s+alpine:3(?:\.[0-9]+)?$")
    return any(pattern.match(line) for line in lines)


def _has_bare_docker_annotation(lines: Iterable[str]) -> bool:
    # A bare ``# docker`` line (no image after it) selects the legacy daemon-based runtime.
    pattern = re.compile(r"^#\s*docker\s*$", re.IGNORECASE)
    return any(pattern.match(line) for line in lines)


def _has_message_binding(text: str) -> bool:
    # Accept ``message="$1"`` (with or without quotes, with or without spaces around ``=``).
    pattern = re.compile(r'(^|\n)\s*message\s*=\s*"?\$1"?\s*(?:$|\n|#)')
    return bool(pattern.search(text))


def _api_get(url: str, token: str, timeout: int = 60) -> requests.Response:
    return requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=timeout)


def _api_post_json(url: str, token: str, body: dict, timeout: int = 240) -> requests.Response:
    return requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(body),
        timeout=timeout,
    )


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def test_local_script_content_file_exists() -> None:
    _, safe_id, _, _, _ = _ids()
    files = _local_script_files(safe_id)
    assert files["folder"].is_dir(), (
        f"Expected Windmill folder {files['folder']} to exist. The executor must place the "
        f"sandboxed Docker script under f/docker_{safe_id}/."
    )
    assert files["content_files"], (
        "Could not find a Windmill script content file at "
        f"{files['folder']}/hello_alpine.* with an extension in {SCRIPT_EXTENSIONS!r}."
    )


def test_local_script_uses_sandbox_alpine3_annotation() -> None:
    _, safe_id, _, _, _ = _ids()
    files = _local_script_files(safe_id)
    assert files["content_files"], "No script content file found; see previous test."
    failures: list[str] = []
    for path in files["content_files"]:
        text = _read_text(path)
        lines = _stripped_lines(text)
        if not _has_sandbox_alpine3_line(lines):
            failures.append(
                f"{path} does not contain a `# sandbox alpine:3` (or `alpine:3.X`) annotation. "
                "The sandboxed runtime is the only Docker-image mode supported on Windmill Cloud."
            )
        if _has_bare_docker_annotation(lines):
            failures.append(
                f"{path} contains a bare `# docker` annotation (legacy daemon runtime). "
                "Use `# sandbox <image>` instead — the legacy runtime requires a self-hosted "
                "Docker socket and does NOT work on Windmill Cloud."
            )
    assert not failures, "\n".join(failures)


def test_local_script_binds_message_argument() -> None:
    _, safe_id, _, _, _ = _ids()
    files = _local_script_files(safe_id)
    assert files["content_files"], "No script content file found; see previous test."
    bindings_found = [path for path in files["content_files"] if _has_message_binding(_read_text(path))]
    assert bindings_found, (
        "None of the candidate script content files bind a positional argument named `message` "
        "(expected something like `message=\"$1\"`). Windmill infers the typed parameter name "
        "from the left-hand side of positional `$1`, `$2`, … bindings."
    )


def test_local_script_yaml_declares_bash_language() -> None:
    _, safe_id, _, _, _ = _ids()
    files = _local_script_files(safe_id)
    metadata = files["metadata"]
    assert metadata.is_file(), (
        f"Expected the Windmill script metadata file at {metadata} to exist."
    )
    try:
        parsed = yaml.safe_load(_read_text(metadata))
    except yaml.YAMLError as exc:  # pragma: no cover - guards against invalid YAML
        pytest.fail(f"Metadata file {metadata} is not valid YAML: {exc}")
    assert isinstance(parsed, dict), (
        f"Metadata file {metadata} must parse to a YAML mapping at the top level."
    )
    language = parsed.get("language")
    assert language == EXPECTED_LANGUAGE, (
        f"Metadata file {metadata} declares `language: {language!r}`, but Windmill's "
        f"ScriptLang enum does NOT include `docker` — the canonical identifier for "
        f"sandboxed Docker scripts is `language: {EXPECTED_LANGUAGE!r}` because the body is "
        "dispatched to the image's /bin/sh -c."
    )


def test_log_file_contains_required_lines() -> None:
    _, _, script_path, _, expected_result = _ids()
    log_path = Path(PROJECT_DIR) / "output.log"
    assert log_path.is_file(), f"Expected log file {log_path} to exist."
    log_lines = _stripped_lines(_read_text(log_path))
    expected_script_line = f"Script path: {script_path}"
    expected_result_line = f"Result: {expected_result}"
    assert expected_script_line in log_lines, (
        f"Log file {log_path} does not contain the expected `Script path: ...` line. "
        f"Expected: {expected_script_line!r}."
    )
    assert expected_result_line in log_lines, (
        f"Log file {log_path} does not contain the expected `Result: ...` line. "
        f"Expected: {expected_result_line!r}."
    )


def test_script_deployed_to_cloud_workspace() -> None:
    workspace = _env("WINDMILL_WORKSPACE")
    token = _env("WINDMILL_TOKEN")
    _, _, script_path, _, _ = _ids()
    url = f"{WINDMILL_BASE_URL}/api/w/{workspace}/scripts/get/p/{script_path}"
    response = _api_get(url, token)
    assert response.status_code == 200, (
        f"Expected HTTP 200 from {url}, got {response.status_code}. "
        f"Response body: {response.text[:300]}"
    )
    try:
        payload = response.json()
    except ValueError as exc:  # pragma: no cover - guards against malformed cloud responses
        pytest.fail(f"Response from {url} was not valid JSON: {exc}")
    assert payload.get("path") == script_path, (
        f"Deployed script path mismatch: expected {script_path!r}, got {payload.get('path')!r}."
    )
    assert payload.get("language") == EXPECTED_LANGUAGE, (
        f"Deployed script language is {payload.get('language')!r}, expected "
        f"{EXPECTED_LANGUAGE!r} (the canonical Windmill identifier for sandboxed Docker scripts)."
    )
    content = payload.get("content", "")
    assert isinstance(content, str) and content, (
        f"Deployed script content is empty or non-string: {content!r}"
    )
    content_lines = _stripped_lines(content)
    assert _has_sandbox_alpine3_line(content_lines), (
        "Deployed script content does not contain a `# sandbox alpine:3` (or `alpine:3.X`) "
        "annotation."
    )
    assert not _has_bare_docker_annotation(content_lines), (
        "Deployed script content contains a bare `# docker` annotation. The legacy runtime is "
        "not supported on Windmill Cloud; use `# sandbox <image>` instead."
    )


def test_remote_execution_returns_expected_result() -> None:
    workspace = _env("WINDMILL_WORKSPACE")
    token = _env("WINDMILL_TOKEN")
    run_id, _, script_path, expected_message, expected_result = _ids()
    url = (
        f"{WINDMILL_BASE_URL}/api/w/{workspace}/jobs/run_wait_result/p/{script_path}"
    )
    response = _api_post_json(url, token, {"message": expected_message}, timeout=240)
    assert response.status_code == 200, (
        f"Expected HTTP 200 from synchronous run at {url}, got {response.status_code}. "
        f"Response body: {response.text[:500]}"
    )
    try:
        result = response.json()
    except ValueError as exc:  # pragma: no cover
        pytest.fail(
            f"Synchronous run response was not valid JSON. Status={response.status_code}, "
            f"body={response.text[:500]}, error={exc}"
        )
    assert result == expected_result, (
        "Synchronous run of the deployed sandboxed Docker script did not return the expected "
        f"result. Expected the JSON string {expected_result!r} (the last stdout line captured "
        f"by Windmill, with run-id {run_id!r}), got {result!r}."
    )
