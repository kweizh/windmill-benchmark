import json
import os
import re
import shutil
import socketserver
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
import requests

PROJECT_DIR = "/home/user/myproject"
SCRIPT_REL = "f/eval/fanout_workflow.ts"
SCRIPT_PATH = os.path.join(PROJECT_DIR, SCRIPT_REL)
PORT = 8080


# ---------------------------------------------------------------------------
# Concurrency-tracking HTTP server
# ---------------------------------------------------------------------------


class _Tracker:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.in_flight = 0
        self.peak = 0
        self.served = 0

    def acquire(self) -> None:
        with self.lock:
            self.in_flight += 1
            if self.in_flight > self.peak:
                self.peak = self.in_flight

    def release(self) -> None:
        with self.lock:
            self.in_flight -= 1
            self.served += 1

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "peak": self.peak,
                "served": self.served,
                "in_flight": self.in_flight,
            }


TRACKER = _Tracker()


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # silence access log
        return

    def do_GET(self) -> None:  # noqa: N802
        path = self.path
        if path == "/__stats__":
            body = json.dumps(TRACKER.snapshot()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Treat any /n/<id> path (allow arbitrary id, including the probe /n/0)
        # as a tracked request. We deliberately hold the connection open for ~1s
        # so concurrent in-flight requests overlap and the peak counter rises.
        m = re.match(r"^/n/([^/?#]+)$", path)
        if m is not None:
            tracked = m.group(1) != "0"  # don't count the readiness probe
            if tracked:
                TRACKER.acquire()
            try:
                time.sleep(1.0)
                body = json.dumps({"id": m.group(1)}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            finally:
                if tracked:
                    TRACKER.release()
            return

        self.send_response(404)
        self.end_headers()


class _ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


@pytest.fixture(scope="module")
def http_server():
    server = _ThreadingHTTPServer(("0.0.0.0", PORT), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # Wait briefly for the socket to bind
    deadline = time.time() + 5.0
    while time.time() < deadline:
        try:
            with requests.Session() as s:
                r = s.get(f"http://127.0.0.1:{PORT}/__stats__", timeout=1.0)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.1)
    yield server
    server.shutdown()
    server.server_close()


# ---------------------------------------------------------------------------
# Cloudflared quick tunnel so Windmill cloud workers can reach the local server
# ---------------------------------------------------------------------------


_TRYCF_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


@pytest.fixture(scope="module")
def public_url(http_server):  # noqa: ARG001  (depends on server being up)
    assert shutil.which("cloudflared") is not None, "cloudflared not installed"
    proc = subprocess.Popen(
        [
            "cloudflared",
            "tunnel",
            "--no-autoupdate",
            "--url",
            f"http://localhost:{PORT}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    url_holder: dict = {}
    log_lines: list = []

    def reader():
        assert proc.stdout is not None
        for line in proc.stdout:
            log_lines.append(line.rstrip())
            if "url" not in url_holder:
                m = _TRYCF_RE.search(line)
                if m is not None:
                    url_holder["url"] = m.group(0)

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    deadline = time.time() + 60.0
    while time.time() < deadline and "url" not in url_holder:
        time.sleep(0.5)

    if "url" not in url_holder:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        pytest.fail(
            "cloudflared did not produce a trycloudflare.com URL within 60s. "
            "Tail of cloudflared log: " + "\n".join(log_lines[-40:])
        )

    url = url_holder["url"]

    # Probe the public URL until it round-trips (DNS / routing propagation)
    probe_deadline = time.time() + 60.0
    last_err = None
    while time.time() < probe_deadline:
        try:
            r = requests.get(f"{url}/n/0", timeout=5.0)
            if r.status_code == 200:
                break
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(1.0)
    else:
        proc.terminate()
        pytest.fail(
            f"Public cloudflared URL {url} never returned 200 from /n/0. "
            f"Last error: {last_err!r}"
        )

    yield url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID", "")
    assert rid, "ZEALT_RUN_ID environment variable is not set"
    assert re.fullmatch(r"zr-[a-z0-9]+", rid), f"Bad ZEALT_RUN_ID format: {rid!r}"
    return rid


def _read_script_source() -> str:
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_script_file_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Workflow-as-Code script file not found at {SCRIPT_PATH}."
    )


def test_script_uses_canonical_wac_primitives():
    """Static analysis: workflow(, parallel(, task(, concurrency: 3, windmill-client import."""
    src = _read_script_source()

    assert re.search(r"\bworkflow\s*\(", src), (
        "Script must call `workflow(...)` to mark the entry point."
    )
    assert re.search(r"\bparallel\s*\(", src), (
        "Script must use `parallel(...)` from windmill-client to fan out."
    )
    assert re.search(r"\btask\s*\(", src), (
        "Script must wrap each HTTP call inside a `task(...)` invocation."
    )
    assert re.search(r"""['"]concurrency['"]?\s*:\s*3\b""", src), (
        "Script must pass a concurrency cap of 3 to `parallel(...)` "
        "(e.g. `{ concurrency: 3 }`)."
    )
    assert re.search(
        r"""from\s+['"]windmill-client['"]""", src
    ), "Script must import from 'windmill-client'."


def test_workflow_execution_honours_bounded_concurrency(public_url):
    run_id = _run_id()
    deployed_path = f"f/eval/fanout_workflow_{run_id.replace('-', '_')}"
    deployed_file = os.path.join(PROJECT_DIR, f"{deployed_path}.ts")

    # 1. Copy the agent's script to a run-id-scoped path so concurrent trials
    #    do not stomp on each other when pushing to the shared cloud workspace.
    os.makedirs(os.path.dirname(deployed_file), exist_ok=True)
    shutil.copyfile(SCRIPT_PATH, deployed_file)

    env = os.environ.copy()

    # 2. Push the run-id-scoped script to Windmill cloud.
    push = subprocess.run(
        ["wmill", "sync", "push", "--yes"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert push.returncode == 0, (
        f"`wmill sync push` failed (rc={push.returncode}).\n"
        f"stdout={push.stdout}\nstderr={push.stderr}"
    )

    # 3. Reset concurrency tracker right before invocation.
    with TRACKER.lock:
        TRACKER.in_flight = 0
        TRACKER.peak = 0
        TRACKER.served = 0

    # 4. Invoke the workflow with 9 URLs targeting the public tunnel.
    urls = [f"{public_url}/n/{i}" for i in range(1, 10)]
    payload = json.dumps({"urls": urls})

    try:
        run = subprocess.run(
            ["wmill", "script", "run", deployed_path, "-d", payload],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
        )
        assert run.returncode == 0, (
            f"`wmill script run {deployed_path}` failed (rc={run.returncode}).\n"
            f"stdout={run.stdout}\nstderr={run.stderr}"
        )

        # 5. Extract the JSON result from stdout (CLI may print log preamble
        #    before the final JSON; pick the last JSON array/object block).
        stdout = run.stdout.strip()
        result = _extract_last_json(stdout)
        assert isinstance(result, list), (
            f"Workflow result must be a JSON array; got {type(result).__name__}: {result!r}"
        )
        assert len(result) == 9, (
            f"Workflow result must have length 9; got {len(result)}: {result!r}"
        )
        for idx, item in enumerate(result):
            assert isinstance(item, dict), (
                f"Element {idx} is not a JSON object: {item!r}"
            )
            assert "url" in item and "status" in item, (
                f"Element {idx} missing 'url' or 'status' field: {item!r}"
            )
            assert item["status"] == 200, (
                f"Element {idx} has non-200 status: {item!r}"
            )
            assert item["url"] == urls[idx], (
                f"Order not preserved at index {idx}: "
                f"expected url={urls[idx]!r}, got {item['url']!r}"
            )

        # 6. Read concurrency stats from the local server.
        stats_resp = requests.get(
            f"http://127.0.0.1:{PORT}/__stats__", timeout=5.0
        )
        assert stats_resp.status_code == 200, (
            f"Failed to read /__stats__: {stats_resp.status_code} {stats_resp.text!r}"
        )
        stats = stats_resp.json()
        assert stats["served"] == 9, (
            f"Local server expected to serve 9 tracked requests; got {stats['served']}. "
            f"Stats: {stats!r}"
        )
        assert stats["peak"] <= 3, (
            f"Observed peak concurrency {stats['peak']} exceeds the cap of 3 — "
            "the `concurrency: 3` option was not honoured."
        )
        assert stats["peak"] >= 2, (
            f"Observed peak concurrency {stats['peak']} is below 2 — "
            "the workflow appears to have serialised the requests instead of "
            "running them in parallel."
        )
    finally:
        # Best-effort cleanup of the run-id-scoped deployed script. Failure here
        # must NOT fail the test (network flakes, eventual consistency, etc.).
        try:
            token = os.environ.get("WINDMILL_TOKEN", "")
            workspace = os.environ.get("WINDMILL_WORKSPACE", "")
            if token and workspace:
                requests.post(
                    "https://app.windmill.dev/api/w/"
                    f"{workspace}/scripts/archive/p/{deployed_path}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=15.0,
                )
        except Exception:
            pass
        try:
            if os.path.isfile(deployed_file):
                os.remove(deployed_file)
        except Exception:
            pass


def _extract_last_json(text: str):
    """Return the last top-level JSON value parsed from `text`.

    wmill CLI may print a small preamble (job ID, links) before the final
    JSON-encoded result. We scan from the end of the output and return the
    last array or object that parses as valid JSON.
    """
    text = text.strip()
    if not text:
        raise AssertionError("wmill stdout was empty; no JSON result to parse.")

    # Fast path: the whole stdout is the JSON result.
    try:
        return json.loads(text)
    except Exception:
        pass

    # Otherwise, walk backwards across lines and try larger and larger suffixes.
    lines = text.splitlines()
    for start in range(len(lines)):
        candidate = "\n".join(lines[start:]).strip()
        if not candidate:
            continue
        if candidate[0] not in "[{":
            continue
        try:
            return json.loads(candidate)
        except Exception:
            continue

    raise AssertionError(
        f"Could not parse a JSON result from wmill stdout. Raw stdout:\n{text}"
    )
