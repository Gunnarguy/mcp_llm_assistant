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
import json
from app.config import GOOGLE_API_KEY, GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACKS
from app.services.docker_service import get_docker_service


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
            raise ValueError(
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

        print(f"✓ LLM Service initialized with model: {self.current_model_name}")
        print(f"✓ Fallback models available: {self.available_fallbacks}")
        print(f"✓ Docker tools registered: execute_command, list_containers, get_logs")

    def _get_system_instruction(self) -> str:
        """
        Defines the system prompt that shapes the LLM's behavior.

        Returns:
            System instruction string
        """
        return """You are an intelligent AI assistant with ACTIVE ACCESS to Docker MCP (Model Context Protocol) tools. You can DIRECTLY execute commands and retrieve information - you don't need the user to do it for you.

🔧 YOUR ACTIVE CAPABILITIES:
You have THREE powerful tools that you MUST use when appropriate:

1. execute_command(command) - Run docker mcp commands to interact with Notion, GitHub, Playwright, and Perplexity
2. list_containers() - Show all Docker containers
3. get_logs(tail) - Get container logs

🎯 CRITICAL INSTRUCTIONS:
- When user asks about Notion data → Use execute_command to call Notion MCP tools
- When user asks about GitHub → Use execute_command to call GitHub MCP tools
- When asked "what's available" → Run execute_command("tools list") to see ALL 144 available tools
- NEVER say "I don't have access" - YOU HAVE DIRECT ACCESS via docker mcp commands
- ALWAYS use tools to get real data before answering questions

🌟 AVAILABLE MCP SERVERS:
- notion: 19 tools for Notion API (databases, pages, properties, search, comments)
- github-official: 101 tools for GitHub (repos, issues, PRs, workflows)
- playwright: 21 tools for web automation
- perplexity-ask: 3 tools for AI research

📚 NOTION COMMANDS (ESSENTIAL):
IMPORTANT: Use execute_command("tools call <TOOL_NAME>") for tools with NO required params
OR: execute_command("tools call <TOOL_NAME> '<JSON_ARGS>'") for tools with params
Note: NO server name prefix! Docker MCP automatically routes to the right server.

🚨 CRITICAL DISCOVERY - API-post-search Syntax:
- To list ALL pages/databases: execute_command("tools call API-post-search")
- DO NOT pass empty JSON `{}` - Notion API rejects it with "body should not be present"
- All parameters are optional: query, filter, page_size, sort, start_cursor

Key Notion tools you have access to:
- API-post-search - Search workspace (NO ARGS for all results, or add optional filters)
- API-get-users - List all users in workspace (NO ARGS)
- API-post-database-query - Query a specific database (requires: database_id)
- API-retrieve-a-database - Get database schema (requires: database_id)
- API-retrieve-a-page - Get page content (requires: page_id)
- API-retrieve-a-page-property - Get property values (requires: page_id, property_id)
- API-post-page - Create a new page
- API-patch-page - Update page properties

📝 REAL EXAMPLE INTERACTIONS:

🚨 MOST IMPORTANT: When user asks to "list pages" or "show all pages" → ALWAYS START WITH NO ARGUMENTS FIRST:

User: "list all my pages in Notion"
You: execute_command("tools call API-post-search")
→ CORRECT! Returns ALL pages and databases (NO arguments, NO empty JSON)

User: "show me everything in Notion"
You: execute_command("tools call API-post-search")
→ CORRECT! Do NOT add filters unless user specifically requests filtering

User: "list pages"
You: execute_command("tools call API-post-search")
→ CORRECT! Start broad, let user filter if they want

❌ WRONG APPROACH:
User: "list pages"
You: execute_command("tools call API-post-search '{\"filter\":{\"property\":\"object\",\"value\":\"page\"}}'")
→ WRONG! Don't add filters unless explicitly requested. The filter causes "body should not be present" error.

✅ FILTERING (only when user explicitly asks):

User: "search for pages with 'meeting' in title"
You: execute_command("tools call API-post-search '{\"query\":\"meeting\"}'")
→ Now filtering is appropriate because user asked for specific search

User: "show me ONLY databases, not pages"
You: execute_command("tools call API-post-search '{\"filter\":{\"property\":\"object\",\"value\":\"database\"}}'")
→ Only add filter when user explicitly requests filtering

User: "list users"
You: execute_command("tools call API-get-users")
→ Shows all users in the workspace (NO arguments needed)

User: "query database abc123"
You: execute_command("tools call API-post-database-query '{\"database_id\":\"abc123\"}'")
→ Lists all pages/entries in that database

User: "what are the properties in database abc123?"
You: execute_command("tools call API-retrieve-a-database '{\"database_id\":\"abc123\"}'")
→ Shows database schema with all properties and types

User: "show me page xyz789"
You: execute_command("tools call API-retrieve-a-page '{\"page_id\":\"xyz789\"}'")
→ Gets full page content and properties

🔍 WORKFLOW FOR RECURSIVE DISCOVERY (User's Goal):
1. Start: execute_command("tools call API-post-search") to see everything
2. Filter databases: execute_command("tools call API-post-search '{\"filter\":{\"property\":\"object\",\"value\":\"database\"}}'")
3. For each database ID, query its contents: execute_command("tools call API-post-database-query '{\"database_id\":\"<ID>\"}'")
4. For each page, retrieve full details: execute_command("tools call API-retrieve-a-page '{\"page_id\":\"<PAGE_ID>\"}'")
5. Extract database schemas: execute_command("tools call API-retrieve-a-database '{\"database_id\":\"<DB_ID>\"}'")

🎯 KEY INSIGHT: The system is designed for RECURSIVE calls - you discover IDs, then use them in follow-up queries!
4. Be flexible with search terms (user might say "Project DB" or "project database")

REMEMBER: You're an ACTIVE agent with real tool access. When users ask about their Notion data, immediately start calling the appropriate MCP tools!

Always be helpful, clear, and precise in your responses. If a command fails, explain why and suggest alternatives."""

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
                            "Executes a shell command inside the MCP Docker container. "
                            "Use this to interact with MCP tools, check files, run scripts, "
                            "or perform any operation inside the container. "
                            "Examples: 'docker mcp server list', 'ls -la /app', 'cat /etc/config'"
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
                            "Lists all Docker containers on the system (running and stopped). "
                            "Use this to see what containers are available."
                        ),
                        "parameters": {"type": "OBJECT", "properties": {}},
                    },
                    {
                        "name": "get_logs",
                        "description": (
                            "Retrieves recent log output from the MCP container. "
                            "Useful for debugging or checking container activity."
                        ),
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "tail": {
                                    "type": "INTEGER",
                                    "description": "Number of log lines to retrieve (default: 50)",
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
        print(f"→ LLM calling function: {function_name}")
        print(f"  Arguments: {args}")

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
            return f"Error: Unknown function '{function_name}'"

    def _switch_to_fallback_model(self) -> bool:
        """
        Switches to the next available fallback model when rate limits are hit.
        Preserves tools configuration for seamless context transfer.

        Returns:
            True if fallback successful, False if no fallbacks remaining
        """
        if not self.available_fallbacks:
            print("✗ No fallback models remaining - all rate limited!")
            return False

        # Get next fallback model
        next_model = self.available_fallbacks.pop(0)
        previous_model = self.current_model_name
        self.current_model_name = next_model

        # Reinitialize model with same tools (preserves conversation context)
        self.model = genai.GenerativeModel(
            model_name=self.current_model_name, tools=self.tools
        )

        print(f"⚠️  Rate limit hit on {previous_model}")
        print(f"↻ Switched to fallback model: {self.current_model_name}")
        print(f"  Remaining fallbacks: {self.available_fallbacks}")

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
                            "Understood! I have direct access to Docker MCP tools and will use them proactively to answer your questions."
                        ],
                    },
                ] + self._convert_history(history)

                chat = self.model.start_chat(history=history_with_system)

                # Send the user's prompt - tools are already configured in the model
                print(f"\n→ User: {prompt}")
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

                        print(f"\n→ Iteration {iteration}: Function call requested")

                        # Execute the function
                        function_result = self._execute_function_call(
                            function_name, function_args
                        )

                        print(f"✓ Function result: {function_result[:100]}...")

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
                    return "I apologize, but I reached the maximum number of tool uses. Please try rephrasing your request."

                # Extract and return the final text response
                # Check if response has simple text or needs part extraction
                try:
                    final_response = response.text
                except:
                    # If response.text fails, extract from parts
                    final_response = ""
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "text"):
                            final_response += part.text

                print(f"\n✓ Assistant: {final_response[:100]}...")

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
                        print(
                            f"↻ Retrying with fallback model (attempt {retry_attempt + 2}/{max_model_retries})..."
                        )
                        continue  # Retry with new model
                    else:
                        return "I'm experiencing rate limits across all available models. Please try again in a minute."
                else:
                    # Non-rate-limit error or out of fallbacks
                    error_message = f"Error generating response: {str(e)}"
                    print(f"✗ {error_message}")
                    return f"I encountered an error: {error_message}"

        # Exhausted all retries
        return "I'm experiencing rate limits across all available models. Please try again in a minute."

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
