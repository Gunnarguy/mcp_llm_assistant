"""
Tests for Docker Service

Tests the Docker service layer including MCP command execution,
container listing, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
import subprocess
from app.services.docker_service import DockerService
from app.exceptions import DockerCommandError, DockerTimeoutError


class TestDockerService:
    """Test suite for DockerService class."""

    @patch("app.services.docker_service.docker.from_env")
    @patch("app.services.docker_service.subprocess.run")
    def test_init_success(self, mock_subprocess, mock_docker):
        """Test successful initialization of Docker service."""
        # Setup mocks
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_docker.return_value = mock_client

        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "notion github-official"

        # Initialize service
        service = DockerService()

        # Assertions
        assert service.client is not None
        assert service.is_healthy() is True
        mock_client.ping.assert_called_once()

    @patch("app.services.docker_service.subprocess.run")
    def test_execute_mcp_command_success(self, mock_subprocess):
        """Test successful MCP command execution."""
        # Setup mock
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Server list: notion, github"
        mock_subprocess.return_value.stderr = ""

        # Create service with mocked client
        with patch("app.services.docker_service.docker.from_env"):
            service = DockerService.__new__(DockerService)
            service.client = Mock()

            # Execute command
            result = service.execute_mcp_command("server list")

            # Assertions
            assert "notion" in result
            assert "github" in result
            mock_subprocess.assert_called_once()

    @patch("app.services.docker_service.subprocess.run")
    def test_execute_mcp_command_failure(self, mock_subprocess):
        """Test MCP command execution failure."""
        # Setup mock for failure
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = "Command not found"

        # Create service
        with patch("app.services.docker_service.docker.from_env"):
            service = DockerService.__new__(DockerService)
            service.client = Mock()

            # Execute command and expect exception
            with pytest.raises(DockerCommandError) as exc_info:
                service.execute_mcp_command("invalid command")

            assert "Command not found" in str(exc_info.value)

    @patch("app.services.docker_service.subprocess.run")
    def test_execute_mcp_command_timeout(self, mock_subprocess):
        """Test MCP command timeout."""
        # Setup mock for timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired("docker", 30)

        # Create service
        with patch("app.services.docker_service.docker.from_env"):
            service = DockerService.__new__(DockerService)
            service.client = Mock()

            # Execute command and expect timeout exception
            with pytest.raises(DockerTimeoutError) as exc_info:
                service.execute_mcp_command("slow command")

            assert "30" in str(exc_info.value)

    def test_list_containers(self, mock_docker_client):
        """Test listing containers."""
        # Setup mock containers
        container1 = Mock()
        container1.name = "test-container"
        container1.status = "running"
        container1.image.tags = ["test:latest"]
        container1.short_id = "abc123"

        mock_docker_client.containers.list.return_value = [container1]

        # Create service
        with patch(
            "app.services.docker_service.docker.from_env",
            return_value=mock_docker_client,
        ):
            service = DockerService.__new__(DockerService)
            service.client = mock_docker_client

            # List containers
            result = service.list_containers()

            # Assertions
            assert "test-container" in result
            assert "running" in result
            mock_docker_client.containers.list.assert_called_once()

    def test_list_containers_empty(self, mock_docker_client):
        """Test listing containers when none exist."""
        mock_docker_client.containers.list.return_value = []

        # Create service
        with patch(
            "app.services.docker_service.docker.from_env",
            return_value=mock_docker_client,
        ):
            service = DockerService.__new__(DockerService)
            service.client = mock_docker_client

            # List containers
            result = service.list_containers()

            # Assertions
            assert "No containers found" in result
