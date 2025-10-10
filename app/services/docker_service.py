"""
Docker Service Layer

Handles all interactions with the Docker MCP Gateway.
Provides methods for server discovery, health checks, and command execution.
"""

import docker
import subprocess
from docker.errors import NotFound, APIError, DockerException
from typing import Optional, Dict, Any
from app.config import MCP_CONTAINER_NAME


class DockerService:
    """
    Service class for managing Docker MCP Gateway interactions.

    This class executes MCP commands through the Docker CLI since
    MCP Gateway runs as a process, not a container.
    """

    def __init__(self):
        """
        Initializes the Docker client for general Docker operations.
        """
        self.client: Optional[docker.DockerClient] = None
        self.connection_error: Optional[str] = None

        try:
            # Connect to Docker daemon using environment settings
            self.client = docker.from_env()

            # Verify connection by pinging the daemon
            self.client.ping()
            print("✓ Successfully connected to Docker daemon")

            # Check if MCP gateway is accessible
            self._check_mcp_gateway()

        except DockerException as e:
            error_msg = (
                "Failed to connect to Docker daemon. " "Is Docker Desktop running?"
            )
            print(f"✗ {error_msg}")
            print(f"  Error: {str(e)}")
            self.connection_error = error_msg
            self.client = None

    def _check_mcp_gateway(self):
        """
        Checks if the MCP gateway is accessible by listing servers.
        """
        try:
            result = subprocess.run(
                ["docker", "mcp", "server", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                servers = result.stdout.strip()
                print(f"✓ MCP Gateway accessible - Servers: {servers}")
            else:
                print(f"⚠ MCP Gateway check returned error: {result.stderr}")

        except Exception as e:
            print(f"⚠ Could not verify MCP Gateway: {e}")

    def is_healthy(self) -> bool:
        """
        Checks if the Docker service is healthy and ready to use.

        Returns:
            True if Docker client is connected.
        """
        return self.client is not None

    def get_container_info(self) -> Dict[str, Any]:
        """
        Retrieves information about MCP Gateway and Docker.

        Returns:
            Dictionary containing status information.
        """
        return {
            "connected": self.client is not None,
            "gateway": "MCP Docker Gateway (CLI process)",
            "status": "running" if self.is_healthy() else "disconnected",
        }

    def execute_mcp_command(self, command: str) -> str:
        """
        Executes a docker mcp command using subprocess.

        This is the core method that enables the LLM to interact with
        the MCP Gateway. It runs commands like:
        `docker mcp server list`

        Args:
            command: The MCP command to execute (e.g., "server list")

        Returns:
            A string containing the command's output or an error message.
        """
        try:
            print(f"→ Executing MCP command: docker mcp {command}")

            # Build the full command
            cmd_parts = ["docker", "mcp"] + command.split()

            # Execute command
            result = subprocess.run(
                cmd_parts, capture_output=True, text=True, timeout=30
            )

            # Check result
            if result.returncode == 0:
                output = result.stdout.strip()
                print(f"✓ Command succeeded: {output[:100]}...")
                return (
                    output if output else "(command completed successfully, no output)"
                )
            else:
                error = (
                    result.stderr.strip()
                    if result.stderr
                    else f"Command failed with exit code {result.returncode}"
                )
                print(f"✗ Command failed: {error}")
                return f"Error: {error}"

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after 30 seconds"
            print(f"✗ {error_msg}")
            return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Failed to execute command: {str(e)}"
            print(f"✗ {error_msg}")
            return f"Error: {error_msg}"

    def list_containers(self) -> str:
        """
        Lists all containers (running and stopped) on the system.

        This is a helper method that can be exposed as a tool to the LLM.

        Returns:
            Formatted string listing all containers.
        """
        if not self.client:
            return "Error: Not connected to Docker daemon"

        try:
            containers = self.client.containers.list(all=True)

            if not containers:
                return "No containers found on this system"

            result = "Containers on this system:\n\n"
            for container in containers:
                result += (
                    f"• {container.name}\n"
                    f"  Status: {container.status}\n"
                    f"  Image: {container.image.tags[0] if container.image.tags else 'N/A'}\n"
                    f"  ID: {container.short_id}\n\n"
                )

            return result

        except Exception as e:
            return f"Error listing containers: {str(e)}"

    def get_logs(self, tail: int = 50) -> str:
        """
        Retrieves recent logs from the MCP container.

        Args:
            tail: Number of lines to retrieve from the end of the logs

        Returns:
            The container's log output
        """
        if not self.is_container_running():
            return "Error: Container is not running"

        try:
            logs = self.mcp_container.logs(tail=tail, timestamps=True)
            decoded_logs = logs.decode("utf-8")

            if not decoded_logs:
                return "No logs available"

            return f"Last {tail} lines of container logs:\n\n{decoded_logs}"

        except Exception as e:
            return f"Error retrieving logs: {str(e)}"


# Singleton instance for use across the application
_docker_service_instance: Optional[DockerService] = None


def get_docker_service() -> DockerService:
    """
    Returns a singleton instance of the DockerService.

    This ensures we only have one connection to the Docker daemon
    throughout the application lifecycle.
    """
    global _docker_service_instance

    if _docker_service_instance is None:
        _docker_service_instance = DockerService()

    return _docker_service_instance
