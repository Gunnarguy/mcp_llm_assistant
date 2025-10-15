"""
Test configuration and fixtures

Provides common test fixtures and configuration for pytest.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from app.services.docker_service import DockerService
from app.services.llm_service import LanguageModelService


@pytest.fixture
def mock_docker_client():
    """Mock Docker client for testing."""
    client = Mock()
    client.ping.return_value = True
    client.containers.list.return_value = []
    return client


@pytest.fixture
def docker_service_mock(mock_docker_client):
    """Mock Docker service instance."""
    service = Mock(spec=DockerService)
    service.is_healthy.return_value = True
    service.execute_mcp_command.return_value = "Success"
    service.list_containers.return_value = "No containers found"
    service.get_logs.return_value = "No logs available"
    return service


@pytest.fixture
def llm_service_mock():
    """Mock LLM service instance."""
    service = Mock(spec=LanguageModelService)
    service.get_response = AsyncMock(return_value="Test response")
    service.get_simple_response.return_value = "Simple test response"
    return service


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "prompt": "What containers are running?",
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"},
        ],
    }


@pytest.fixture
def sample_health_response():
    """Sample health check response."""
    return {
        "status": "healthy",
        "docker_connected": True,
        "llm_configured": True,
        "container_name": "mcp-gateway",
        "container_status": "running",
    }
