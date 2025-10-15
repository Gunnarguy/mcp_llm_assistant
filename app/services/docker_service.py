"""
Docker Service Layer

Handles all interactions with the Docker MCP Gateway.
Provides methods for server discovery, health checks, and command execution.
"""

import subprocess
from typing import Optional, Dict, Any


class DockerService:
    """
    Service class for managing Docker MCP Gateway interactions.

    This class executes MCP commands through the Docker CLI since
    MCP Gateway runs as a process, not a container.
    """

    def __init__(self):
        """
        Initializes the Docker service.
        The connection_error attribute is used to cache connection issues.
        """
        self.connection_error: Optional[str] = None

    def _check_mcp_gateway(self):
        """
        Verifies that the Docker MCP Gateway is accessible.

        This is a diagnostic check that runs a simple 'server list' command.
        It helps confirm that the 'docker mcp' CLI extension is installed and
        responding, which is a prerequisite for all other MCP operations.
        """
        try:
            # Use subprocess to run the command, as MCP Gateway is a CLI process.
            result = subprocess.run(
                ["docker", "mcp", "server", "list"],
                capture_output=True,
                text=True,
                timeout=5,  # Short timeout to avoid long waits on unresponsive systems.
            )

            if result.returncode == 0:
                servers = result.stdout.strip()
                print(f"✓ MCP Gateway accessible - Servers: {servers}")
            else:
                # Log errors if the command fails, which can indicate a setup issue.
                print(f"⚠ MCP Gateway check returned error: {result.stderr}")

        except Exception as e:
            # Catch exceptions like timeouts or if 'docker' isn't in the PATH.
            print(f"⚠ Could not verify MCP Gateway: {e}")

    def is_healthy(self) -> bool:
        """
        Checks if the Docker daemon is running and responsive.

        Returns:
            True if 'docker ps' executes successfully, False otherwise.
        """
        try:
            # A simple 'docker ps' is a reliable way to check Docker daemon health.
            result = subprocess.run(["docker", "ps"], capture_output=True, timeout=2)
            return result.returncode == 0
        except Exception:
            # Any exception (e.g., timeout, command not found) means Docker is not healthy.
            return False

    def get_container_info(self) -> Dict[str, Any]:
        """
        Retrieves static information about the MCP Gateway and Docker status.

        Returns:
            A dictionary with health status and gateway information.
        """
        healthy = self.is_healthy()
        return {
            "connected": healthy,
            "gateway": "MCP Docker Gateway (CLI process)",
            "status": "running" if healthy else "disconnected",
        }

    def execute_mcp_command(self, command: str) -> str:
        """
        Executes a 'docker mcp' command via a subprocess.

        This serves as the primary interface for the LLM to interact with the
        MCP Gateway. It is designed to be robust, with clear error handling
        and timeouts.

        Args:
            command: The MCP command to execute (e.g., "server list").

        Returns:
            A string containing the command's stdout or a descriptive error message.
        """
        try:
            print(f"→ Executing MCP command: docker mcp {command}")

            # The command is split into parts for security and correctness.
            cmd_parts = ["docker", "mcp"] + command.split()

            # Execute the command with a 30-second timeout to prevent hangs.
            result = subprocess.run(
                cmd_parts, capture_output=True, text=True, timeout=30
            )

            # Process the result based on the return code.
            if result.returncode == 0:
                output = result.stdout.strip()
                print(f"✓ Command succeeded: {output[:100]}...")
                return (
                    output
                    if output
                    else "(Command completed successfully with no output)"
                )
            else:
                # Return stderr if available, otherwise a generic error.
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
            # Catch-all for other potential issues (e.g., file not found).
            error_msg = f"An unexpected error occurred: {str(e)}"
            print(f"✗ {error_msg}")
            return f"Error: {error_msg}"

    def list_containers(self) -> str:
        """
        Lists all Docker containers on the system in a readable format.

        This method provides a snapshot of all containers, which is useful
        for diagnostics and giving the user an overview of their environment.

        Returns:
            A formatted string of container information or an error message.
        """
        try:
            # The command is formatted to return only the necessary fields.
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "-a",  # Include all containers (running and stopped).
                    "--format",
                    "{{.Names}}\t{{.Status}}\t{{.Image}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return (
                    "Error: Could not list containers due to a Docker command failure."
                )

            output = result.stdout.strip()
            if not output:
                return "No containers found on this system."

            # Format the output for better readability.
            lines = output.splitlines()
            container_details = [line.split("\t") for line in lines]
            formatted_output = "Containers on this system:\n\n" + "\n".join(
                f"• {name}\n  Status: {status}\n  Image: {image}\n"
                for name, status, image in container_details
                if len(container_details) >= 3
            )

            return formatted_output.rstrip()

        except Exception as e:
            return f"Error listing containers: {str(e)}"

    def get_logs(self, container_name: str, tail: int = 50) -> str:
        """
        Retrieves recent logs from a specified container.

        Args:
            container_name: The name of the container to get logs from.
            tail: The number of lines to retrieve from the end of the logs.

        Returns:
            The container's log output or an error message.
        """
        try:
            # Use the provided container_name instead of a hardcoded one.
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), container_name],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return f"Error: Container '{container_name}' not found or not running."

            logs = result.stdout.strip()
            return (
                f"Last {tail} lines of logs for '{container_name}':\n\n{logs}"
                if logs
                else "No logs available for this container."
            )

        except Exception as e:
            return f"Error retrieving logs for '{container_name}': {str(e)}"


# Singleton instance to ensure only one DockerService is used.
_docker_service_instance: Optional[DockerService] = None


def get_docker_service() -> DockerService:
    """
    Factory function to get the singleton instance of DockerService.

    This pattern ensures that all parts of the application share the same
    service instance, preventing redundant initializations.
    """
    global _docker_service_instance

    if _docker_service_instance is None:
        _docker_service_instance = DockerService()

    return _docker_service_instance
