import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eink_rpi_api import app

logger = logging.getLogger(__name__)


@pytest.fixture()
def tmp_client(tmp_path: Path):
    client = TestClient(app)
    return client
