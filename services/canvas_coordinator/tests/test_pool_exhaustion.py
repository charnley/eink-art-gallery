"""
Reproduction test for production failure:

    sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached,
    connection timed out, timeout 30.00

Root cause: exception paths (e.g. 404 before session.close()) leaked pooled
connections. Enough concurrent leaking requests exhausted the pool and every
subsequent request failed with 500.

The bug lives in the real `get_session` dependency, so it cannot be reproduced
through the `tmp_client` fixture (which overrides `get_session`). This test
spawns a real uvicorn subprocess with a temp database and hammers it with
concurrent 404-producing DELETEs, followed by normal GETs.
"""

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import pytest

LEAK_REQUESTS = 25
FOLLOWUP_REQUESTS = 60
WORKERS = 30
REQUEST_TIMEOUT = 60


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 30.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def _status(port: int, path: str, method: str = "GET") -> int:
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


@pytest.fixture()
def live_server(tmp_path: Path):
    """Real uvicorn subprocess + real get_session, temp sqlite database."""
    port = _free_port()
    env = dict(os.environ, STORAGE=str(tmp_path))
    proc = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import uvicorn; "
            "from canvasserver.models.db import create_db_and_tables; "
            "create_db_and_tables(None); "
            f"uvicorn.run('canvasserver.main:app', host='127.0.0.1', port={port}, log_level='warning')",
        ],
        env=env,
    )
    try:
        assert _wait_for_server(port), "server never came up"
        yield port
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_concurrent_404s_do_not_exhaust_connection_pool(live_server):
    port = live_server

    # Phase 1: concurrent DELETEs of nonexistent frames.
    # Old code raised HTTPException before session.close() -> leaked connection.
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        statuses = list(
            ex.map(lambda _: _status(port, f"/frames/{uuid4()}", "DELETE"), range(LEAK_REQUESTS))
        )

    assert all(
        s == 404 for s in statuses
    ), f"pool exhaustion: expected all 404, got {sorted(set(statuses))}"

    # Phase 2: server still healthy for normal traffic
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        statuses = list(ex.map(lambda _: _status(port, "/frames/"), range(FOLLOWUP_REQUESTS)))

    assert all(s == 200 for s in statuses), f"server degraded after burst: {sorted(set(statuses))}"
