"""
Tests for LLM Service

Comprehensive tests for the LLM service including:
- Initialization and configuration
- Response generation (simple and agentic)
- Tool calling and execution
- Rate limit handling and model fallback
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.llm_service import LanguageModelService, get_llm_service
from app.exceptions import LLMConfigurationError, DockerCommandError


class TestLLMServiceInitialization:
    """Test suite for LLM service initialization."""

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_init_success(self, mock_docker, mock_model, mock_configure):
        """Test successful initialization with valid API key."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Assertions
        assert service.current_model_name == "gemini-2.5-flash"
        assert len(service.available_fallbacks) > 0
        mock_configure.assert_called_once_with(
            api_key="test-api-key"  # pragma: allowlist secret
        )
        mock_model.assert_called_once()

    @patch("app.services.llm_service.GOOGLE_API_KEY", None)
    def test_init_no_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(LLMConfigurationError) as exc_info:
            LanguageModelService()

        assert "API key not configured" in str(exc_info.value)

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_tool_declarations(self, mock_docker, mock_model, mock_configure):
        """Test that tools are properly declared."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Check tools
        assert service.tools is not None
        assert len(service.tools) > 0
        assert "function_declarations" in service.tools[0]

        # Check function names
        function_names = [f["name"] for f in service.tools[0]["function_declarations"]]
        assert "execute_command" in function_names
        assert "list_containers" in function_names
        assert "get_logs" in function_names


class TestFunctionExecution:
    """Test suite for function call execution."""

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_execute_command_function(self, mock_docker, mock_model, mock_configure):
        """Test execute_command function call."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker_instance.execute_mcp_command.return_value = (
            "Command executed successfully"
        )
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Execute function
        result = service._execute_function_call(
            "execute_command", {"command": "server list"}
        )

        # Assertions
        assert "successfully" in result
        mock_docker_instance.execute_mcp_command.assert_called_once_with("server list")

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_list_containers_function(self, mock_docker, mock_model, mock_configure):
        """Test list_containers function call."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker_instance.list_containers.return_value = (
            "Container1: running\nContainer2: stopped"
        )
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Execute function
        result = service._execute_function_call("list_containers", {})

        # Assertions
        assert "Container1" in result
        mock_docker_instance.list_containers.assert_called_once()

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_get_logs_function(self, mock_docker, mock_model, mock_configure):
        """Test get_logs function call."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker_instance.get_logs.return_value = "Log line 1\nLog line 2"
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Execute function with default tail
        result = service._execute_function_call("get_logs", {})
        assert "Log line 1" in result
        mock_docker_instance.get_logs.assert_called_with(tail=50)

        # Execute function with custom tail
        result = service._execute_function_call("get_logs", {"tail": 100})
        mock_docker_instance.get_logs.assert_called_with(tail=100)

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_unknown_function(self, mock_docker, mock_model, mock_configure):
        """Test handling of unknown function call."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Execute unknown function
        result = service._execute_function_call("unknown_function", {})

        # Assertions
        assert "Error" in result
        assert "unknown_function" in result

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_function_docker_error(self, mock_docker, mock_model, mock_configure):
        """Test handling of Docker errors in function calls."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker_instance.execute_mcp_command.side_effect = DockerCommandError(
            "server list", "Connection failed", 1
        )
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Execute function that raises error
        result = service._execute_function_call(
            "execute_command", {"command": "server list"}
        )

        # Assertions
        assert "Error" in result
        assert "Connection failed" in result


class TestResponseGeneration:
    """Test suite for response generation with agentic loop."""

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    @pytest.mark.asyncio
    async def test_get_response_no_tool_use(
        self, mock_docker, mock_model_class, mock_configure
    ):
        """Test response generation without tool use."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        # Create mock response without function call
        mock_response = Mock()
        mock_response.text = "Hello! How can I help you?"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content.parts = [Mock()]
        mock_response.candidates[0].content.parts[0].function_call = None

        # Mock chat
        mock_chat = Mock()
        mock_chat.send_message_async = AsyncMock(return_value=mock_response)

        # Mock model
        mock_model = Mock()
        mock_model.start_chat.return_value = mock_chat
        mock_model_class.return_value = mock_model

        # Initialize service
        service = LanguageModelService()

        # Get response
        response = await service.get_response("Hello", [])

        # Assertions
        assert "Hello" in response
        mock_chat.send_message_async.assert_called()

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    @pytest.mark.asyncio
    async def test_get_response_with_tool_use(
        self, mock_docker, mock_model_class, mock_configure
    ):
        """Test response generation with tool use."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker_instance.execute_mcp_command.return_value = "notion github"
        mock_docker.return_value = mock_docker_instance

        # Create mock function call response
        mock_function_call = Mock()
        mock_function_call.name = "execute_command"
        mock_function_call.args = {"command": "server list"}

        mock_response_with_call = Mock()
        mock_response_with_call.candidates = [Mock()]
        mock_response_with_call.candidates[0].content.parts = [Mock()]
        mock_response_with_call.candidates[0].content.parts[
            0
        ].function_call = mock_function_call

        # Create mock final response
        mock_final_response = Mock()
        mock_final_response.text = "The available servers are: notion and github"
        mock_final_response.candidates = [Mock()]
        mock_final_response.candidates[0].content.parts = [Mock()]
        mock_final_response.candidates[0].content.parts[0].function_call = None

        # Mock chat
        mock_chat = Mock()
        mock_chat.send_message_async = AsyncMock(
            side_effect=[mock_response_with_call, mock_final_response]
        )

        # Mock model
        mock_model = Mock()
        mock_model.start_chat.return_value = mock_chat
        mock_model_class.return_value = mock_model

        # Initialize service
        service = LanguageModelService()

        # Get response
        response = await service.get_response("List servers", [])

        # Assertions
        assert "servers" in response.lower()
        assert mock_chat.send_message_async.call_count == 2


class TestRateLimitFallback:
    """Test suite for rate limit handling and model fallback."""

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_switch_to_fallback_model(
        self, mock_docker, mock_model_class, mock_configure
    ):
        """Test switching to fallback model on rate limit."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        mock_model = Mock()
        mock_model_class.return_value = mock_model

        # Initialize service
        service = LanguageModelService()
        initial_model = service.current_model_name
        initial_fallbacks = len(service.available_fallbacks)

        # Switch to fallback
        result = service._switch_to_fallback_model()

        # Assertions
        assert result is True
        assert service.current_model_name != initial_model
        assert len(service.available_fallbacks) == initial_fallbacks - 1

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_switch_no_fallbacks_remaining(
        self, mock_docker, mock_model_class, mock_configure
    ):
        """Test fallback when no models remaining."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        mock_model = Mock()
        mock_model_class.return_value = mock_model

        # Initialize service
        service = LanguageModelService()
        service.available_fallbacks = []  # No fallbacks left

        # Try to switch
        result = service._switch_to_fallback_model()

        # Assertions
        assert result is False

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    @pytest.mark.asyncio
    async def test_get_response_rate_limit_retry(
        self, mock_docker, mock_model_class, mock_configure
    ):
        """Test automatic retry with fallback on rate limit."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        # Create mock response
        mock_response = Mock()
        mock_response.text = "Success after fallback"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content.parts = [Mock()]
        mock_response.candidates[0].content.parts[0].function_call = None

        # Mock chat that fails first time then succeeds
        mock_chat_fail = Mock()
        mock_chat_fail.send_message_async = AsyncMock(
            side_effect=Exception("429 rate limit exceeded")
        )

        mock_chat_success = Mock()
        mock_chat_success.send_message_async = AsyncMock(return_value=mock_response)

        # Mock model
        mock_model = Mock()
        call_count = [0]

        def start_chat_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_chat_fail
            else:
                return mock_chat_success

        mock_model.start_chat.side_effect = start_chat_side_effect
        mock_model_class.return_value = mock_model

        # Initialize service
        service = LanguageModelService()

        # Get response (should retry with fallback)
        response = await service.get_response("Test prompt", [])

        # Assertions
        assert "fallback" in response.lower() or "Success" in response


class TestHistoryConversion:
    """Test suite for conversation history conversion."""

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_convert_history(self, mock_docker, mock_model, mock_configure):
        """Test conversion of API history to Gemini format."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        # Initialize service
        service = LanguageModelService()

        # Convert history
        api_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

        gemini_history = service._convert_history(api_history)

        # Assertions
        assert len(gemini_history) == 3
        assert gemini_history[0]["role"] == "user"
        assert gemini_history[1]["role"] == "model"  # assistant -> model
        assert gemini_history[2]["role"] == "user"
        assert gemini_history[0]["parts"][0]["text"] == "Hello"


class TestSimpleResponse:
    """Test suite for simple response generation."""

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_get_simple_response_success(
        self, mock_docker, mock_model_class, mock_configure
    ):
        """Test simple response generation."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        mock_response = Mock()
        mock_response.text = "Simple response"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        # Initialize service
        service = LanguageModelService()

        # Get simple response
        response = service.get_simple_response("Simple question")

        # Assertions
        assert response == "Simple response"
        mock_model.generate_content.assert_called_once_with("Simple question")

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_get_simple_response_error(
        self, mock_docker, mock_model_class, mock_configure
    ):
        """Test simple response with error."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API error")
        mock_model_class.return_value = mock_model

        # Initialize service
        service = LanguageModelService()

        # Get simple response
        response = service.get_simple_response("Question")

        # Assertions
        assert "Error" in response
        assert "API error" in response


class TestServiceSingleton:
    """Test suite for singleton pattern."""

    @patch("app.services.llm_service.GOOGLE_API_KEY", "test-api-key")
    @patch("app.services.llm_service.genai.configure")
    @patch("app.services.llm_service.genai.GenerativeModel")
    @patch("app.services.llm_service.get_docker_service")
    def test_singleton_pattern(self, mock_docker, mock_model, mock_configure):
        """Test that get_llm_service returns same instance."""
        # Setup mocks
        mock_docker_instance = Mock()
        mock_docker.return_value = mock_docker_instance

        # Clear any existing instance
        import app.services.llm_service as llm_module

        llm_module._llm_service_instance = None

        # Get service twice
        service1 = get_llm_service()
        service2 = get_llm_service()

        # Assertions
        assert service1 is service2  # Same instance
