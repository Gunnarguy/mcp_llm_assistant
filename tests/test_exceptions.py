"""
Tests for Exception Classes

Tests custom exception handling and error messages.
"""

from app.exceptions import (
    DockerCommandError,
    DockerTimeoutError,
    LLMRateLimitError,
    ServiceUnavailableError,
)


class TestCustomExceptions:
    """Test suite for custom exception classes."""

    def test_docker_command_error(self):
        """Test DockerCommandError with details."""
        error = DockerCommandError("server list", "Connection refused", returncode=1)

        assert "server list" in str(error)
        assert "Connection refused" in str(error)
        assert error.command == "server list"
        assert error.returncode == 1

    def test_docker_timeout_error(self):
        """Test DockerTimeoutError with timeout value."""
        error = DockerTimeoutError("tools call API-post-search", 30)

        assert "tools call API-post-search" in str(error)
        assert "30" in str(error)
        assert error.timeout == 30

    def test_llm_rate_limit_error(self):
        """Test LLMRateLimitError with models list."""
        models = ["gemini-2.5-flash", "gemini-2.0-flash"]
        error = LLMRateLimitError(models)

        assert "gemini-2.5-flash" in str(error)
        assert "gemini-2.0-flash" in str(error)
        assert error.models_tried == models

    def test_service_unavailable_error(self):
        """Test ServiceUnavailableError with service name."""
        error = ServiceUnavailableError("Docker", "Container not running")

        assert "Docker" in str(error)
        assert "Container not running" in str(error)
        assert error.service == "Docker"
        assert error.reason == "Container not running"

    def test_service_unavailable_error_no_reason(self):
        """Test ServiceUnavailableError without reason."""
        error = ServiceUnavailableError("LLM")

        assert "LLM" in str(error)
        assert error.reason is None
