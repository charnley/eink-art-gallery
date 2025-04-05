import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)


@pytest.fixture()
def tmp_client(tmp_path: Path):
    client = TestClient(app)
    return client
