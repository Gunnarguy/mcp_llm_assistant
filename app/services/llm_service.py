"""
LLM Service Layer with Agentic Tool Use

Handles all interactions with Google Gemini API, including:
- Basic text generation
- Function calling / tool use for Docker orchestration
- Multi-turn conversation management
- Agentic loop for complex tasks
"""

import google.generativeai as genai
import google.ai.generativelanguage as glm
from typing import List, Dict, Any, Optional
from app.config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL_PRIMARY,
    GEMINI_MODEL_FALLBACKS,
)
from app.services.docker_service import get_docker_service
from app.logger import setup_logger
from app.exceptions import (
    LLMConfigurationError,
    DockerCommandError,
    DockerTimeoutError,
)

# Setup logger for this module
logger = setup_logger(__name__, log_file="logs/llm_service.log")


class LanguageModelService:
    """
    Service class for managing LLM interactions with tool-use capabilities.

    This class implements an "agentic loop" where the LLM can:
    1. Decide when to use Docker tools
    2. Execute commands in containers
    3. Process results and generate natural responses
    """

    def __init__(self):
        """
        Initializes the Gemini client and configures available tools.
        """
        if not GOOGLE_API_KEY:
            logger.error("Google API key not configured")
            raise LLMConfigurationError(
                "Google API key not configured. "
                "Please set GOOGLE_API_KEY in your .env file"
            )

        # Configure the Gemini API
        genai.configure(api_key=GOOGLE_API_KEY)

        # Store system instruction and tool declarations
        self.system_instruction = self._get_system_instruction()
        self.tools = self._get_tool_declarations()

        # Model fallback configuration
        self.current_model_name = GEMINI_MODEL_PRIMARY
        self.available_fallbacks = GEMINI_MODEL_FALLBACKS.copy()

        # Initialize the model WITH tools configured
        self.model = genai.GenerativeModel(
            model_name=self.current_model_name, tools=self.tools
        )

        # Get reference to Docker service
        self.docker_service = get_docker_service()

        logger.info(f"LLM Service initialized with model: {self.current_model_name}")
        logger.info(f"Fallback models available: {self.available_fallbacks}")
        logger.debug(
            "Docker tools registered: execute_command, list_containers, get_logs"
        )

    def _get_system_instruction(self) -> str:
        """
        Defines the system prompt that shapes the LLM's behavior.

        Returns:
            System instruction string
        """
        return """You have access to Notion via MCP commands.

Available tools:
- execute_command(cmd) - Run MCP commands. Format: "tools call <TOOL> '<JSON>'"
- list_containers()
- get_logs(tail)

Common Notion commands (pass to execute_command):
- Search all: tools call API-post-search
- Query DB: tools call API-post-database-query '{"database_id":"ID"}'
- Create page: tools call API-post-page '{"parent":{"database_id":"ID"},"properties":{...}}'
- Get page: tools call API-retrieve-a-page '{"page_id":"ID"}'
- Get DB schema: tools call API-retrieve-a-database '{"database_id":"ID"}'

When user asks to do something:
1. Find what you need (search if needed)
2. Do it
3. Confirm

Be proactive. Don't ask for IDs - find them yourself.

IMPORTANT: When calling execute_command, pass ONLY the MCP command part.
Example: execute_command("tools call API-post-search") NOT
execute_command("docker mcp tools call...")"""

    def _get_tool_declarations(self) -> List[Dict[str, Any]]:
        """
        Declares the functions (tools) available to the LLM in the format expected by the older SDK.

        Returns:
            List with tool declaration dictionary
        """
        return [
            {
                "function_declarations": [
                    {
                        "name": "execute_command",
                        "description": (
                            "Executes a shell command inside the MCP "
                            "Docker container. Use this to interact with MCP "
                            "tools, check files, run scripts, or perform any "
                            "operation inside the container. Examples: "
                            "'docker mcp server list', 'ls -la /app', "
                            "'cat /etc/config'"
                        ),
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "command": {
                                    "type": "STRING",
                                    "description": "The shell command to execute in the container",
                                }
                            },
                            "required": ["command"],
                        },
                    },
                    {
                        "name": "list_containers",
                        "description": (
                            "Lists all Docker containers on the system "
                            "(running and stopped). Use this to see what "
                            "containers are available."
                        ),
                        "parameters": {"type": "OBJECT", "properties": {}},
                    },
                    {
                        "name": "get_logs",
                        "description": (
                            "Retrieves recent log output from the MCP "
                            "container. Useful for debugging or checking "
                            "container activity."
                        ),
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "tail": {
                                    "type": "INTEGER",
                                    "description": (
                                        "Number of log lines to retrieve "
                                        "(default: 50)"
                                    ),
                                }
                            },
                        },
                    },
                ]
            }
        ]

    def _execute_function_call(self, function_name: str, args: Dict[str, Any]) -> str:
        """
        Routes function calls from the LLM to the appropriate service method.

        Args:
            function_name: Name of the function the LLM wants to call
            args: Arguments for the function

        Returns:
            Result of the function execution as a string
        """
        logger.info(f"LLM calling function: {function_name}")
        logger.debug(f"Function arguments: {args}")

        try:
            if function_name == "execute_command":
                command = args.get("command", "")
                result = self.docker_service.execute_mcp_command(command)
                return result

            elif function_name == "list_containers":
                result = self.docker_service.list_containers()
                return result

            elif function_name == "get_logs":
                tail = args.get("tail", 50)
                result = self.docker_service.get_logs(tail=tail)
                return result

            else:
                error_msg = f"Unknown function '{function_name}'"
                logger.error(error_msg)
                return f"Error: {error_msg}"

        except (DockerCommandError, DockerTimeoutError) as e:
            # Docker-specific errors - return as string to LLM
            logger.warning(f"Docker error in function {function_name}: {str(e)}")
            return f"Error: {str(e)}"

        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error in function {function_name}: {str(e)}")
            return f"Error: {str(e)}"

    def _switch_to_fallback_model(self) -> bool:
        """
        Switches to the next available fallback model when rate limits are hit.
        Preserves tools configuration for seamless context transfer.

        Returns:
            True if fallback successful, False if no fallbacks remaining
        """
        if not self.available_fallbacks:
            logger.error("No fallback models remaining - all rate limited!")
            return False

        # Get next fallback model
        next_model = self.available_fallbacks.pop(0)
        previous_model = self.current_model_name
        self.current_model_name = next_model

        # Reinitialize model with same tools (preserves conversation context)
        self.model = genai.GenerativeModel(
            model_name=self.current_model_name, tools=self.tools
        )

        logger.warning(f"Rate limit hit on {previous_model}")
        logger.info(f"Switched to fallback model: {self.current_model_name}")
        logger.info(f"Remaining fallbacks: {self.available_fallbacks}")

        return True

    async def get_response(self, prompt: str, history: List[Dict[str, Any]]) -> str:
        """
        Generates a response using the agentic loop with tool use.
        Automatically switches to fallback models on rate limit errors.

        This implements the full cycle:
        1. Send prompt to LLM
        2. If LLM requests tool use, execute the tool
        3. Send tool result back to LLM
        4. Get final natural language response
        5. If rate limit hit (429), switch model and retry seamlessly

        Args:
            prompt: The user's current message
            history: Previous conversation messages

        Returns:
            The assistant's response as a string
        """
        max_model_retries = len(self.available_fallbacks) + 1  # Primary + fallbacks

        for retry_attempt in range(max_model_retries):
            try:
                # Build the conversation history in Gemini's format
                # Add system instruction as the first message
                history_with_system = [
                    {"role": "user", "parts": [self.system_instruction]},
                    {
                        "role": "model",
                        "parts": [
                            "Understood! I have direct access to Docker "
                            "MCP tools and will use them proactively to "
                            "answer your questions."
                        ],
                    },
                ] + self._convert_history(history)

                chat = self.model.start_chat(history=history_with_system)

                # Send the user's prompt - tools are already configured in the model
                logger.info(
                    f"User prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
                )
                response = await chat.send_message_async(prompt)

                # Agentic Loop: Handle function calls
                max_iterations = 5  # Prevent infinite loops
                iteration = 0

                while iteration < max_iterations:
                    iteration += 1

                    # Check if the model wants to call a function
                    if response.candidates[0].content.parts[0].function_call:
                        function_call = (
                            response.candidates[0].content.parts[0].function_call
                        )
                        function_name = function_call.name
                        function_args = dict(function_call.args)

                        logger.info(f"Iteration {iteration}: Function call requested")

                        # Execute the function
                        function_result = self._execute_function_call(
                            function_name, function_args
                        )

                        logger.debug(f"Function result: {function_result[:100]}...")

                        # Send the function result back to the model
                        response = await chat.send_message_async(
                            glm.Content(
                                parts=[
                                    glm.Part(
                                        function_response=glm.FunctionResponse(
                                            name=function_name,
                                            response={"result": function_result},
                                        )
                                    )
                                ]
                            )
                        )

                    else:
                        # No function call - we have the final response
                        break

                if iteration >= max_iterations:
                    logger.warning("Reached maximum number of tool uses")
                    return (
                        "I apologize, but I reached the maximum number of "
                        "tool uses. Please try rephrasing your request."
                    )

                # Extract and return the final text response
                # Check if response has simple text or needs part extraction
                try:
                    final_response = response.text
                except Exception:
                    # If response.text fails, extract from parts
                    final_response = ""
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "text"):
                            final_response += part.text

                logger.info(
                    f"Assistant response: {final_response[:100]}"
                    f"{'...' if len(final_response) > 100 else ''}"
                )

                return final_response

            except Exception as e:
                error_str = str(e).lower()

                # Detect rate limit errors (429, quota exceeded, resource exhausted)
                is_rate_limit = any(
                    indicator in error_str
                    for indicator in [
                        "429",
                        "rate limit",
                        "quota exceeded",
                        "resource_exhausted",
                        "please retry",
                    ]
                )

                if is_rate_limit and retry_attempt < max_model_retries - 1:
                    # Try to switch to fallback model
                    if self._switch_to_fallback_model():
                        logger.info(
                            f"Retrying with fallback model (attempt "
                            f"{retry_attempt + 2}/{max_model_retries})..."
                        )
                        continue  # Retry with new model
                    else:
                        logger.error("All models rate limited")
                        return (
                            "I'm experiencing rate limits across all "
                            "available models. Please try again in a minute."
                        )
                else:
                    # Non-rate-limit error or out of fallbacks
                    error_message = f"Error generating response: {str(e)}"
                    logger.error(error_message)
                    return f"I encountered an error: {error_message}"

        # Exhausted all retries
        logger.error("Exhausted all model retries due to rate limits")
        return (
            "I'm experiencing rate limits across all available models. "
            "Please try again in a minute."
        )

    def _convert_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Converts the API history format to Gemini's expected format.

        Args:
            history: List of messages in API format (role, content)

        Returns:
            List of messages in Gemini format
        """
        gemini_history = []

        for message in history:
            role = message.get("role", "user")
            content = message.get("content", "")

            # Gemini uses "user" and "model" instead of "user" and "assistant"
            gemini_role = "model" if role == "assistant" else "user"

            gemini_history.append({"role": gemini_role, "parts": [{"text": content}]})

        return gemini_history

    def get_simple_response(self, prompt: str) -> str:
        """
        Generates a simple response without tool use.
        Useful for basic questions that don't require Docker interaction.

        Args:
            prompt: The user's message

        Returns:
            The assistant's response
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"


# Singleton instance
_llm_service_instance: Optional[LanguageModelService] = None


def get_llm_service() -> LanguageModelService:
    """
    Returns a singleton instance of the LanguageModelService.

    This ensures we only initialize the Gemini client once.
    """
    global _llm_service_instance

    if _llm_service_instance is None:
        _llm_service_instance = LanguageModelService()

    return _llm_service_instance
