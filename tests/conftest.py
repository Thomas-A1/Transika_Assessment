import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture()
def client():
    storage.reset()
    with TestClient(app) as c:
        yield c
    storage.reset()
