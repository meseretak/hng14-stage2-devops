import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis():
    """Patch main.r (the already-instantiated Redis client) for every test."""
    mock_r = MagicMock()
    with patch.object(main, "r", mock_r):
        yield mock_r


def test_create_job_returns_job_id(mock_redis):
    response = client.post("/jobs")
    assert response.status_code == 201
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()


def test_get_job_found(mock_redis):
    mock_redis.hget.return_value = b"queued"
    response = client.get("/jobs/some-job-id")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["job_id"] == "some-job-id"


def test_get_job_not_found(mock_redis):
    mock_redis.hget.return_value = None
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_health_endpoint(mock_redis):
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
