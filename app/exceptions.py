"""
Custom Exception Classes

Defines application-specific exceptions for better error handling
and more informative error messages.
"""


class MCPAssistantError(Exception):
    """Base exception for all MCP Assistant errors."""

    pass


class ConfigurationError(MCPAssistantError):
    """Raised when configuration is invalid or missing."""

    pass


class DockerError(MCPAssistantError):
    """Base exception for Docker-related errors."""

    pass


class DockerConnectionError(DockerError):
    """Raised when cannot connect to Docker daemon."""

    pass


class DockerCommandError(DockerError):
    """Raised when Docker command execution fails."""

    def __init__(self, command: str, error: str, returncode: int = None):
        self.command = command
        self.error = error
        self.returncode = returncode
        super().__init__(f"Command '{command}' failed: {error}")


class DockerTimeoutError(DockerError):
    """Raised when Docker command times out."""

    def __init__(self, command: str, timeout: int):
        self.command = command
        self.timeout = timeout
        super().__init__(f"Command '{command}' timed out after {timeout}s")


class LLMError(MCPAssistantError):
    """Base exception for LLM-related errors."""

    pass


class LLMConfigurationError(LLMError):
    """Raised when LLM service is not configured properly."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when all LLM models hit rate limits."""

    def __init__(self, models_tried: list):
        self.models_tried = models_tried
        super().__init__(
            f"Rate limit exceeded for all models: {', '.join(models_tried)}"
        )


class LLMResponseError(LLMError):
    """Raised when LLM generates invalid or unexpected response."""

    pass


class APIError(MCPAssistantError):
    """Base exception for API endpoint errors."""

    pass


class ServiceUnavailableError(APIError):
    """Raised when a required service is unavailable."""

    def __init__(self, service: str, reason: str = None):
        self.service = service
        self.reason = reason
        message = f"Service '{service}' is unavailable"
        if reason:
            message += f": {reason}"
        super().__init__(message)
