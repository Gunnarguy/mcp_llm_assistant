"""
LLM Service Layer with Agentic Tool Use

Handles all interactions with Google Gemini API, including:
- Basic text generation
- Function calling / tool use for Docker orchestration
- Multi-turn conversation management
- Agentic loop for complex tasks
- Direct Notion API integration
"""

import google.generativeai as genai
import google.ai.generativelanguage as glm
import requests
import json
from typing import List, Dict, Any, Optional
from app.config import (
    GOOGLE_API_KEY,
    GEMINI_MODEL_PRIMARY,
    GEMINI_MODEL_FALLBACKS,
    NOTION_TOKEN,
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
    Manages LLM interactions, including agentic tool use.

    This service orchestrates the agentic loop where the LLM can decide to
    use tools (like Docker commands), execute them, and process the results
    to generate a final, natural language response. It also handles model

    fallback for rate limit resilience.
    """

    def __init__(self):
        """
        Initializes the Gemini client, configures tools, and sets up the model.
        """
        if not GOOGLE_API_KEY:
            logger.error("Google API key not configured.")
            raise LLMConfigurationError(
                "Google API key is missing. Please set it in your .env file."
            )

        # Configure the core Gemini API client.
        genai.configure(api_key=GOOGLE_API_KEY)

        # Load system instructions and tool declarations from helper methods.
        self.system_instruction = self._get_system_instruction()
        self.tools = self._get_tool_declarations()

        # Set up the primary model and a queue of fallbacks for resilience.
        self.current_model_name = GEMINI_MODEL_PRIMARY
        self.available_fallbacks = GEMINI_MODEL_FALLBACKS.copy()

        # Initialize the generative model with the tool configuration.
        self.model = genai.GenerativeModel(
            model_name=self.current_model_name, tools=self.tools
        )

        # Get a singleton instance of the Docker service for tool execution.
        self.docker_service = get_docker_service()

        logger.info(f"LLM Service initialized with model: {self.current_model_name}")
        logger.info(f"Fallback models available: {self.available_fallbacks}")

    def _get_system_instruction(self) -> str:
        """
        Defines the system prompt that guides the LLM's behavior and tool use.

        Returns:
            The system instruction string.
        """
        return """You are an AI agent with Notion API and Docker MCP tools.

**Finding databases:**
1. Call notion_api_call with POST /v1/search and empty body "{}" to list ALL resources
2. Filter results client-side by checking object="database" and matching title
3. Search queries often return empty results - always start with empty search

**Searching page content:** Use API-get-block-children (search API only searches titles).

**Creating pages:** Use notion_api_call POST /v1/pages with parent.database_id and properties.

Use tools proactively."""

    def _get_tool_declarations(self) -> List[Dict[str, Any]]:
        """
        Declares the functions (tools) available to the LLM.

        This structure informs the LLM about the available functions, their
        purpose, and their parameters, enabling it to make decisions about
        when and how to call them.

        Returns:
            A list containing the tool declaration dictionary for the Gemini API.
        """
        return [
            {
                "function_declarations": [
                    {
                        "name": "execute_command",
                        "description": (
                            "Executes a shell command to interact with the MCP "
                            "gateway. Use this for all MCP-related operations."
                        ),
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "command": {
                                    "type": "STRING",
                                    "description": (
                                        "The MCP command to execute "
                                        "(e.g., 'tools call API-post-search')."
                                    ),
                                }
                            },
                            "required": ["command"],
                        },
                    },
                    {
                        "name": "list_containers",
                        "description": (
                            "Lists all Docker containers on the system, running or stopped. "
                            "Helps to identify available containers."
                        ),
                        "parameters": {"type": "OBJECT", "properties": {}},
                    },
                    {
                        "name": "get_logs",
                        "description": "Retrieves recent logs from a specific Docker container.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "container_name": {
                                    "type": "STRING",
                                    "description": "The name of the container to get logs from.",
                                },
                                "tail": {
                                    "type": "INTEGER",
                                    "description": "Number of log lines to retrieve (default: 50).",
                                },
                            },
                            "required": ["container_name"],
                        },
                    },
                    {
                        "name": "notion_api_call",
                        "description": (
                            "Makes a direct HTTP request to the Notion API. "
                            "Use this to search, create, update, or query "
                            "Notion databases and pages. "
                            "Supports dynamic API versioning - will automatically "
                            "retry with newer versions if needed. "
                            "Full API docs: "
                            "https://developers.notion.com/reference"
                        ),
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "method": {
                                    "type": "STRING",
                                    "description": (
                                        "HTTP method: GET, POST, PATCH, DELETE"
                                    ),
                                },
                                "endpoint": {
                                    "type": "STRING",
                                    "description": (
                                        "API endpoint path "
                                        "(e.g., '/v1/search', "
                                        "'/v1/databases/DATABASE_ID')"
                                    ),
                                },
                                "body": {
                                    "type": "STRING",
                                    "description": (
                                        "JSON body as a string "
                                        "(use empty string '{}' for GET)"
                                    ),
                                },
                                "api_version": {
                                    "type": "STRING",
                                    "description": (
                                        "Optional: Notion API version to use "
                                        "(e.g., '2022-06-28', '2025-09-03'). "
                                        "Defaults to '2022-06-28'. Use newer versions "
                                        "for databases with advanced features."
                                    ),
                                },
                            },
                            "required": ["method", "endpoint", "body"],
                        },
                    },
                ]
            }
        ]

    def _execute_function_call(self, function_name: str, args: Dict[str, Any]) -> str:
        """
        Routes LLM-initiated function calls to the appropriate service method.

        This acts as a dispatcher, translating the LLM's intent into actual
        application logic.

        Args:
            function_name: The name of the function to call.
            args: A dictionary of arguments for the function.

        Returns:
            The result of the function execution as a string.
        """
        logger.info(f"LLM calling function: {function_name} with args: {args}")

        try:
            if function_name == "execute_command":
                command = args.get("command", "")
                if not command:
                    return "Error: 'command' argument is required."
                return self.docker_service.execute_mcp_command(command)

            elif function_name == "list_containers":
                return self.docker_service.list_containers()

            elif function_name == "get_logs":
                container_name = args.get("container_name")
                if not container_name:
                    return "Error: 'container_name' is a required argument."
                tail = args.get("tail", 50)
                return self.docker_service.get_logs(
                    container_name=container_name, tail=tail
                )

            elif function_name == "notion_api_call":
                method = args.get("method", "").upper()
                endpoint = args.get("endpoint", "")
                body_str = args.get("body", "{}").strip()
                api_version = args.get(
                    "api_version", "2025-09-03"
                )  # Default to newer version to see all resources

                if not method or not endpoint:
                    return "Error: 'method' and 'endpoint' are required arguments."

                if not NOTION_TOKEN:
                    return "Error: NOTION_TOKEN not configured. Please add it to your .env file."

                # Parse the body JSON string
                try:
                    # AUTO-FIX: Remove triple quotes if LLM wrapped JSON in them
                    if body_str.startswith("'''") and body_str.endswith("'''"):
                        body_str = body_str[3:-3].strip()
                        logger.info("🔧 AUTO-FIX: Removed triple quotes from JSON body")
                    elif body_str.startswith('"""') and body_str.endswith('"""'):
                        body_str = body_str[3:-3].strip()
                        logger.info(
                            "🔧 AUTO-FIX: Removed triple double-quotes from JSON body"
                        )

                    if "\\'" in body_str:
                        body_str = body_str.replace("\\'", "'")
                        logger.info(
                            "🔧 AUTO-FIX: Replaced escaped apostrophes in JSON body"
                        )

                    body = json.loads(body_str) if body_str and body_str != "{}" else {}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON body: {body_str[:200]}")
                    return f"Error: Invalid JSON in body parameter: {str(e)}"

                # AUTO-FIX: Empty search works best - remove query if present on search endpoint
                if endpoint == "/v1/search" and "query" in body:
                    query_text = body.get("query", "")
                    if query_text:
                        logger.info(
                            f"🔧 AUTO-FIX: Removing search query '{query_text}' - empty search returns all resources reliably"
                        )
                        # Keep filter if present, but remove query
                        body.pop("query", None)
                        body_str = json.dumps(body)

                # AUTO-FIX: LLM keeps trying to use "database" filter value even though it's invalid
                if endpoint == "/v1/search" and isinstance(body.get("filter"), dict):
                    filter_value = body["filter"].get("value")
                    if filter_value == "database":
                        logger.warning(
                            "🔧 AUTO-FIX: LLM tried to use invalid filter value 'database', correcting to 'page'"
                        )
                        body["filter"]["value"] = "page"
                        body_str = json.dumps(body)  # Update body_str for logging

                # AUTO-WORKAROUND: Database query endpoint is broken, use search API instead
                if (
                    method == "POST"
                    and "/databases/" in endpoint
                    and endpoint.endswith("/query")
                ):
                    database_id = endpoint.split("/databases/")[1].split("/")[0]
                    logger.info(
                        f"Auto-converting broken query endpoint to search API for database {database_id}"
                    )

                    return self._query_database_via_search(
                        database_id, body, api_version
                    )

                # Make the API call with dynamic versioning and auto-retry
                return self._make_notion_api_call(method, endpoint, body, api_version)

            else:
                return f"Error: Unknown function '{function_name}'."

        except (DockerCommandError, DockerTimeoutError) as e:
            logger.error(f"Docker error during function call '{function_name}': {e}")
            return f"Error executing Docker command: {e}"
        except Exception as e:
            logger.error(
                f"Unexpected error in function '{function_name}': {e}", exc_info=True
            )
            return f"An unexpected error occurred: {e}"

    def _make_notion_api_call(
        self, method: str, endpoint: str, body: Dict[str, Any], api_version: str
    ) -> str:
        """
        Makes a Notion API call with proper error handling and intelligent fallback logic.

        AUTO-WORKAROUNDS:
        1. Database not found (404) -> Try extracting real database ID from data sources
        2. Multiple data sources error -> Automatically use older API version (2022-06-28)
        3. Query endpoint broken -> Already handled by _query_database_via_search

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path (e.g., /v1/pages)
            body: Request body as dict
            api_version: Notion API version

        Returns:
            JSON response as string or error message
        """
        url = f"https://api.notion.com{endpoint}"
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": api_version,
            "Content-Type": "application/json",
        }

        logger.info(
            f"Making Notion API call: {method} {url} (API version: {api_version})"
        )

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=body, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=body, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return f"Error: Unsupported HTTP method '{method}'"

            if response.status_code >= 200 and response.status_code < 300:
                result = response.json()
                logger.info(f"Notion API success: {response.status_code}")
                return json.dumps(result, indent=2)
            else:
                error_data = (
                    response.json()
                    if response.headers.get("Content-Type", "").startswith(
                        "application/json"
                    )
                    else {}
                )
                error_message = error_data.get("message", response.text)

                # AUTO-WORKAROUND 1: Database not found - might be a view ID, try to find real database ID
                if (
                    (response.status_code == 404 or response.status_code == 400)
                    and method == "POST"
                    and endpoint == "/v1/pages"
                ):
                    attempted_db_id = body.get("parent", {}).get("database_id")
                    if attempted_db_id:
                        logger.info(
                            f"🔧 AUTO-WORKAROUND: Database {attempted_db_id} not found, searching for actual database ID..."
                        )
                        real_db_id = self._find_real_database_id(
                            attempted_db_id, api_version
                        )
                        if real_db_id and real_db_id != attempted_db_id:
                            logger.info(f"✅ Found real database ID: {real_db_id}")
                            body["parent"]["database_id"] = real_db_id
                            return self._make_notion_api_call(
                                method, endpoint, body, api_version
                            )

                # AUTO-WORKAROUND 2: Multiple data sources error - use older API version
                if (
                    "multiple data sources" in error_message.lower()
                    and api_version != "2022-06-28"
                ):
                    logger.info(
                        "🔧 AUTO-WORKAROUND: Multiple data sources detected, retrying with API version 2022-06-28"
                    )
                    return self._make_notion_api_call(
                        method, endpoint, body, "2022-06-28"
                    )

                logger.error(
                    f"Notion API error: {response.status_code} - {error_message}"
                )
                return f"Notion API Error ({response.status_code}): {json.dumps(error_data, indent=2)}"

        except requests.exceptions.Timeout:
            return "Error: Notion API request timed out after 30 seconds."
        except requests.exceptions.RequestException as e:
            return f"Error: Notion API request failed: {str(e)}"

    def _find_real_database_id(
        self, view_or_db_id: str, api_version: str
    ) -> Optional[str]:
        """
        Finds the actual database ID when given a view ID or database page ID.

        Many Notion databases with "multiple data sources" show a view ID in the URL,
        not the actual database ID. This method searches for the real database.

        Args:
            view_or_db_id: The ID from the URL (might be view, page, or database)
            api_version: Notion API version to use

        Returns:
            The actual database ID, or None if not found
        """
        # First, try to GET it as a page - it might reveal the database structure
        page_result = self._make_notion_api_call(
            "GET", f"/v1/pages/{view_or_db_id}", {}, api_version
        )

        try:
            page_data = json.loads(page_result)
            if page_data.get("object") == "page":
                # Check if this page is a database
                if page_data.get("parent", {}).get("type") == "workspace":
                    # This is a top-level page that might be a database view
                    # Try to get it as a database
                    db_result = self._make_notion_api_call(
                        "GET", f"/v1/databases/{view_or_db_id}", {}, api_version
                    )
                    db_data = json.loads(db_result)

                    if db_data.get("object") == "database":
                        # Check for data_sources (linked databases)
                        data_sources = db_data.get("data_sources", [])
                        if data_sources and len(data_sources) > 0:
                            # Return the first linked database ID
                            first_source = data_sources[0]
                            real_id = first_source.get("database_id")
                            if real_id:
                                logger.info(
                                    f"Found linked database in data_sources: {real_id}"
                                )
                                return real_id

                        # No data sources, this IS the database
                        return view_or_db_id
        except (json.JSONDecodeError, KeyError):
            pass

        # Fallback: Search for databases and try to match by similar ID pattern
        search_result = self._make_notion_api_call(
            "POST",
            "/v1/search",
            {"filter": {"property": "object", "value": "database"}, "page_size": 100},
            api_version,
        )

        try:
            search_data = json.loads(search_result)
            # Try to find a database with similar ID pattern (first part matches)
            view_prefix = (
                view_or_db_id.split("-")[0]
                if "-" in view_or_db_id
                else view_or_db_id[:8]
            )

            for db in search_data.get("results", []):
                db_id = db.get("id", "")
                if db_id.startswith(view_prefix):
                    logger.info(f"Found database with matching ID prefix: {db_id}")
                    return db_id
        except (json.JSONDecodeError, KeyError):
            pass

        return None

    def _query_database_via_search(
        self, database_id: str, query_body: Dict[str, Any], api_version: str
    ) -> str:
        """
        Workaround for broken /databases/{id}/query endpoint.
        Uses search API to get all pages, then filters by database_id.

        Args:
            database_id: The database ID to query
            query_body: Original query body (currently ignored - search doesn't support filters)
            api_version: Notion API version

        Returns:
            JSON array of pages from the database
        """
        logger.info(
            f"🔧 AUTO-WORKAROUND: Converting database query to search API for database {database_id}"
        )

        # Use search API to get all pages
        search_body = {
            "filter": {"property": "object", "value": "page"},
            "page_size": 100,
        }

        search_result = self._make_notion_api_call(
            "POST", "/v1/search", search_body, api_version
        )

        try:
            search_data = json.loads(search_result)
            if "results" not in search_data:
                return search_result  # Return error if search failed

            # Filter to only pages from this database
            matching_pages = [
                page
                for page in search_data["results"]
                if page.get("parent", {}).get("database_id") == database_id
            ]

            logger.info(
                f"✅ Found {len(matching_pages)} pages in database {database_id}"
            )

            # Return in same format as query endpoint
            return json.dumps({"results": matching_pages, "has_more": False}, indent=2)

        except json.JSONDecodeError:
            return search_result  # Return original error

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
