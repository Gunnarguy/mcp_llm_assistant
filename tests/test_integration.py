"""
Integration Tests

Tests that verify the full workflow from API endpoints through
services with realistic interactions and mocking.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def test_app(monkeypatch):
    """Create test client with controlled mocking."""
    # Disable startup events
    app.router.on_startup = []

    with TestClient(app) as client:
        yield client


class TestChatWorkflow:
    """Integration tests for complete chat workflow."""

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_full_chat_workflow_simple(self, mock_llm, mock_docker, test_app):
        """Test complete chat workflow without tool use."""
        # Setup Docker service
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker.return_value = mock_docker_instance

        # Setup LLM service with simple response
        mock_llm_instance = MagicMock()
        mock_llm_instance.get_response = AsyncMock(
            return_value="I can help you with Docker containers!"
        )
        mock_llm.return_value = mock_llm_instance

        # Make chat request
        response = test_app.post(
            "/chat",
            json={"prompt": "What can you help me with?", "history": []},
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "Docker" in data["reply"]

        # Verify LLM was called
        mock_llm_instance.get_response.assert_called_once()

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_full_chat_workflow_with_docker_command(
        self, mock_llm, mock_docker, test_app
    ):
        """Test complete chat workflow with Docker command execution."""
        # Setup Docker service
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker_instance.execute_mcp_command.return_value = "notion github-official"
        mock_docker.return_value = mock_docker_instance

        # Setup LLM service - simulate agentic loop
        mock_llm_instance = MagicMock()
        mock_llm_instance.get_response = AsyncMock(
            return_value="The available MCP servers are: notion and github-official"
        )
        mock_llm.return_value = mock_llm_instance

        # Make chat request
        response = test_app.post(
            "/chat",
            json={"prompt": "List MCP servers", "history": []},
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data

        # LLM should have been called
        mock_llm_instance.get_response.assert_called_once()

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_chat_with_conversation_history(self, mock_llm, mock_docker, test_app):
        """Test chat with conversation history."""
        # Setup services
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker.return_value = mock_docker_instance

        mock_llm_instance = MagicMock()
        mock_llm_instance.get_response = AsyncMock(
            return_value="Based on our previous conversation, I can help with that."
        )
        mock_llm.return_value = mock_llm_instance

        # Make request with history
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"},
            {"role": "user", "content": "What's my container status?"},
            {"role": "assistant", "content": "Your container is running."},
        ]

        response = test_app.post(
            "/chat",
            json={"prompt": "Can you do more?", "history": history},
        )

        # Assertions
        assert response.status_code == 200

        # Verify history was passed
        call_args = mock_llm_instance.get_response.call_args
        assert call_args is not None
        assert len(call_args[1]["history"]) == 4


class TestErrorHandlingIntegration:
    """Integration tests for error handling across the stack."""

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_docker_unavailable_error(self, mock_llm, mock_docker, test_app):
        """Test error when Docker service is unavailable."""
        # Setup Docker as unavailable
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = False
        mock_docker.return_value = mock_docker_instance

        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        # Make chat request
        response = test_app.post(
            "/chat",
            json={"prompt": "Test", "history": []},
        )

        # Should return 503 Service Unavailable
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_llm_error_handling(self, mock_llm, mock_docker, test_app):
        """Test error handling when LLM fails."""
        # Setup services
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker.return_value = mock_docker_instance

        # LLM raises exception
        mock_llm_instance = MagicMock()
        mock_llm_instance.get_response = AsyncMock(
            side_effect=Exception("LLM API error")
        )
        mock_llm.return_value = mock_llm_instance

        # Make request
        response = test_app.post(
            "/chat",
            json={"prompt": "Test", "history": []},
        )

        # Should return error
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestHealthCheckIntegration:
    """Integration tests for health check workflow."""

    @patch("app.main.get_docker_service")
    @patch("app.main.verify_config")
    def test_health_check_all_systems_healthy(self, mock_config, mock_docker, test_app):
        """Test health check with all systems operational."""
        # Setup Docker
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker_instance.get_container_info.return_value = {
            "gateway": "MCP Gateway",
            "status": "running",
        }
        mock_docker.return_value = mock_docker_instance

        # Setup config
        mock_config.return_value = {
            "valid": True,
            "google_api_configured": True,
        }

        # Make request
        response = test_app.get("/health")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["docker_connected"] is True
        assert data["llm_configured"] is True

    @patch("app.main.get_docker_service")
    @patch("app.main.verify_config")
    def test_health_check_docker_down(self, mock_config, mock_docker, test_app):
        """Test health check with Docker unavailable."""
        # Setup Docker as down
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = False
        mock_docker_instance.get_container_info.return_value = {
            "gateway": "MCP Gateway",
            "status": "disconnected",
        }
        mock_docker.return_value = mock_docker_instance

        # Setup config
        mock_config.return_value = {
            "valid": True,
            "google_api_configured": True,
        }

        # Make request
        response = test_app.get("/health")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["partial", "unhealthy"]
        assert data["docker_connected"] is False

    @patch("app.main.get_docker_service")
    @patch("app.main.verify_config")
    def test_health_check_llm_not_configured(self, mock_config, mock_docker, test_app):
        """Test health check with LLM not configured."""
        # Setup Docker
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker_instance.get_container_info.return_value = {
            "gateway": "MCP Gateway",
            "status": "running",
        }
        mock_docker.return_value = mock_docker_instance

        # Setup config - LLM not configured
        mock_config.return_value = {
            "valid": False,
            "google_api_configured": False,
        }

        # Make request
        response = test_app.get("/health")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["partial", "unhealthy"]
        assert data["llm_configured"] is False


class TestInputValidation:
    """Integration tests for input validation."""

    def test_chat_missing_prompt(self, test_app):
        """Test validation when prompt is missing."""
        response = test_app.post("/chat", json={"history": []})

        assert response.status_code == 422  # Validation error

    def test_chat_empty_prompt(self, test_app):
        """Test validation when prompt is empty."""
        response = test_app.post("/chat", json={"prompt": "", "history": []})

        assert response.status_code == 422  # Validation error

    def test_chat_invalid_history(self, test_app):
        """Test validation with invalid history format."""
        response = test_app.post("/chat", json={"prompt": "Test", "history": "invalid"})

        assert response.status_code == 422  # Validation error

    def test_chat_valid_minimal_request(self, test_app):
        """Test validation with minimal valid request."""
        # Mock services
        with patch("app.main.get_docker_service") as mock_docker:
            with patch("app.main.get_llm_service") as mock_llm:
                mock_docker_instance = MagicMock()
                mock_docker_instance.is_healthy.return_value = True
                mock_docker.return_value = mock_docker_instance

                mock_llm_instance = MagicMock()
                mock_llm_instance.get_response = AsyncMock(return_value="Response")
                mock_llm.return_value = mock_llm_instance

                response = test_app.post("/chat", json={"prompt": "Test"})

                # Should succeed (history is optional)
                assert response.status_code == 200


class TestEndToEndScenarios:
    """End-to-end scenario tests."""

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_scenario_check_health_then_chat(self, mock_llm, mock_docker, test_app):
        """Test typical user scenario: check health then chat."""
        # Setup services
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker_instance.get_container_info.return_value = {
            "gateway": "MCP Gateway",
            "status": "running",
        }
        mock_docker.return_value = mock_docker_instance

        mock_llm_instance = MagicMock()
        mock_llm_instance.get_response = AsyncMock(return_value="Hello!")
        mock_llm.return_value = mock_llm_instance

        with patch("app.main.verify_config") as mock_config:
            mock_config.return_value = {
                "valid": True,
                "google_api_configured": True,
            }

            # Step 1: Check health
            health_response = test_app.get("/health")
            assert health_response.status_code == 200
            assert health_response.json()["status"] == "healthy"

            # Step 2: Send chat
            chat_response = test_app.post(
                "/chat", json={"prompt": "Hello", "history": []}
            )
            assert chat_response.status_code == 200
            assert "reply" in chat_response.json()

    @patch("app.main.get_docker_service")
    @patch("app.main.get_llm_service")
    def test_scenario_multi_turn_conversation(self, mock_llm, mock_docker, test_app):
        """Test multi-turn conversation scenario."""
        # Setup services
        mock_docker_instance = MagicMock()
        mock_docker_instance.is_healthy.return_value = True
        mock_docker.return_value = mock_docker_instance

        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        # Simulate multiple conversation turns
        conversation_history = []

        # Turn 1
        mock_llm_instance.get_response = AsyncMock(return_value="Hi! How can I help?")
        response1 = test_app.post(
            "/chat", json={"prompt": "Hello", "history": conversation_history}
        )
        assert response1.status_code == 200

        conversation_history.append({"role": "user", "content": "Hello"})
        conversation_history.append(
            {"role": "assistant", "content": response1.json()["reply"]}
        )

        # Turn 2
        mock_llm_instance.get_response = AsyncMock(
            return_value="You have 3 containers running"
        )
        response2 = test_app.post(
            "/chat",
            json={"prompt": "List my containers", "history": conversation_history},
        )
        assert response2.status_code == 200

        conversation_history.append({"role": "user", "content": "List my containers"})
        conversation_history.append(
            {"role": "assistant", "content": response2.json()["reply"]}
        )

        # Turn 3
        mock_llm_instance.get_response = AsyncMock(return_value="Here are the logs...")
        response3 = test_app.post(
            "/chat",
            json={"prompt": "Show me logs", "history": conversation_history},
        )
        assert response3.status_code == 200

        # Verify conversation tracking
        assert len(conversation_history) == 4  # 2 user + 2 assistant messages
