"""
Tests for API Endpoints

Tests the FastAPI endpoints including chat and health check.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app


@pytest.fixture
def client(monkeypatch):
    """Create test client with mocked services."""
    # Mock the services to prevent initialization during tests
    mock_docker = MagicMock()
    mock_llm = MagicMock()

    def mock_get_docker():
        return mock_docker

    def mock_get_llm():
        return mock_llm

    monkeypatch.setattr("app.main.get_docker_service", mock_get_docker)
    monkeypatch.setattr("app.main.get_llm_service", mock_get_llm)

    # Disable startup event
    app.router.on_startup = []

    with TestClient(app) as test_client:
        yield test_client


class TestAPIEndpoints:
    """Test suite for API endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns basic info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_health_check_healthy(self, mock_llm, mock_docker, client):
        """Test health check when all services are healthy."""
        # Setup mocks
        mock_docker_instance = mock_docker.return_value
        mock_docker_instance.is_healthy.return_value = True
        mock_docker_instance.get_container_info.return_value = {
            "gateway": "MCP Gateway",
            "status": "running",
        }

        # Make request
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["docker_connected"] is True

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    @patch("app.main.verify_config")
    def test_health_check_partial(self, mock_config, mock_llm, mock_docker, client):
        """Test health check with partial availability."""
        # Setup mocks
        mock_docker_instance = mock_docker.return_value
        mock_docker_instance.is_healthy.return_value = False
        mock_docker_instance.get_container_info.return_value = {
            "gateway": "MCP Gateway",
            "status": "disconnected",
        }

        mock_config.return_value = {
            "valid": True,
            "google_api_configured": True,
        }

        # Make request
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["partial", "unhealthy"]

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_chat_endpoint_success(
        self, mock_llm, mock_docker, client, sample_chat_request
    ):
        """Test successful chat interaction."""
        # Setup mocks
        mock_docker_instance = mock_docker.return_value
        mock_docker_instance.is_healthy.return_value = True

        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.get_response = AsyncMock(
            return_value="Here are the running containers..."
        )

        # Make request
        response = client.post("/chat", json=sample_chat_request)

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert len(data["reply"]) > 0

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_chat_endpoint_docker_unavailable(
        self, mock_llm, mock_docker, client, sample_chat_request
    ):
        """Test chat endpoint when Docker is unavailable."""
        # Setup mocks
        mock_docker_instance = mock_docker.return_value
        mock_docker_instance.is_healthy.return_value = False

        # Make request
        response = client.post("/chat", json=sample_chat_request)

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data

    def test_chat_endpoint_invalid_request(self, client):
        """Test chat endpoint with invalid request."""
        # Missing required prompt field
        invalid_request = {"history": []}

        response = client.post("/chat", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_empty_prompt(self, client):
        """Test chat endpoint with empty prompt."""
        invalid_request = {"prompt": "", "history": []}

        response = client.post("/chat", json=invalid_request)

        assert response.status_code == 422  # Validation error
