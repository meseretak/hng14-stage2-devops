import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock the redis.Redis instance used in main.py before import."""
    with patch("redis.Redis") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


@pytest.fixture()
def client(mock_redis):
    # Import after patching so the module-level `r` uses the mock
    from main import app
    return TestClient(app)


def test_create_job_returns_job_id(client, mock_redis):
    """POST /jobs should return a job_id and push to Redis."""
    mock_redis.ping.return_value = True

    response = client.post("/jobs")

    assert response.status_code == 201
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format

    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()


def test_get_job_found(client, mock_redis):
    """GET /jobs/{id} returns status when job exists."""
    mock_redis.hget.return_value = b"queued"

    response = client.get("/jobs/some-job-id")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["job_id"] == "some-job-id"


def test_get_job_not_found(client, mock_redis):
    """GET /jobs/{id} returns 404 when job does not exist."""
    mock_redis.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_health_endpoint(client, mock_redis):
    """GET /health returns ok when Redis is reachable."""
    mock_redis.ping.return_value = True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
