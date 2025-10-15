"""
Docker Service Layer

Handles all interactions with the Docker MCP Gateway.
Provides methods for server discovery, health checks, and command execution.
"""

import subprocess
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
        Initializes the Docker service without touching the Docker SDK.
        """
        self.connection_error: Optional[str] = None

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
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, timeout=2)
            return result.returncode == 0
        except Exception:
            return False

    def get_container_info(self) -> Dict[str, Any]:
        """
        Retrieves information about MCP Gateway and Docker.

        Returns:
            Dictionary containing status information.
        """
        return {
            "connected": self.is_healthy(),
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
            error_msg = "Command timed out after 30 seconds"
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
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--format",
                    "{{.Names}}\t{{.Status}}\t{{.Image}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return "Error: Could not list containers"

            output = result.stdout.strip()
            if not output:
                return "No containers found on this system"

            formatted = "Containers on this system:\n\n"
            for line in output.splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:
                    formatted += (
                        f"• {parts[0]}\n"
                        f"  Status: {parts[1]}\n"
                        f"  Image: {parts[2]}\n\n"
                    )

            return formatted.rstrip()

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
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), MCP_CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return (
                    f"Error: Container '{MCP_CONTAINER_NAME}' not found or not running"
                )

            logs = result.stdout.strip()

            if not logs:
                return "No logs available"

            return f"Last {tail} lines of container logs:\n\n{logs}"

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
