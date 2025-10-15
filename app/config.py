"""
Configuration Management - Enhanced Edition

Securely loads environment variables from .env file and validates
that all required configuration is present.

Features:
- Comprehensive environment variable management
- Smart defaults for all settings
- Validation and health checks
- Support for multiple profiles (dev/prod/test)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from app.logger import setup_logger
from typing import Dict, Any, List

# Find the project root (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent

# Setup logger for config module
logger = setup_logger(__name__, log_file="logs/config.log")

# Load environment variables from .env file in project root
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Loaded environment variables from: {env_path}")
else:
    logger.warning(f".env file not found at {env_path}")
    logger.warning("Please copy .env.template to .env and add your API keys")


# ============================================================
# APPLICATION SETTINGS
# ============================================================
APP_NAME = os.getenv("APP_NAME", "MCP AI Assistant")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Server settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8501"))


# ============================================================
# GOOGLE GEMINI API CONFIGURATION
# ============================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
    logger.warning("GOOGLE_API_KEY not configured properly!")
    logger.warning("Get your free API key from: https://aistudio.google.com/app/apikey")
    logger.warning("Then add it to your .env file")
    GOOGLE_API_KEY = None


# LLM Model Selection with Automatic Fallback
GEMINI_MODEL_PRIMARY = os.getenv("GEMINI_MODEL_PRIMARY", "gemini-2.5-flash")

# Fallback models (tried in order when rate limits hit)
GEMINI_MODEL_FALLBACKS = [
    os.getenv("GEMINI_MODEL_FALLBACK_1", "gemini-2.5-flash-lite"),
    os.getenv("GEMINI_MODEL_FALLBACK_2", "gemini-2.0-flash"),
    os.getenv("GEMINI_MODEL_FALLBACK_3", "gemini-1.5-flash"),
]

# Model parameters
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
GEMINI_TOP_P = float(os.getenv("GEMINI_TOP_P", "0.95"))
GEMINI_TOP_K = int(os.getenv("GEMINI_TOP_K", "40"))
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048"))

# Safety settings
GEMINI_SAFETY_HARASSMENT = os.getenv("GEMINI_SAFETY_HARASSMENT", "BLOCK_ONLY_HIGH")
GEMINI_SAFETY_HATE = os.getenv("GEMINI_SAFETY_HATE", "BLOCK_ONLY_HIGH")
GEMINI_SAFETY_SEXUAL = os.getenv("GEMINI_SAFETY_SEXUAL", "BLOCK_ONLY_HIGH")
GEMINI_SAFETY_DANGEROUS = os.getenv("GEMINI_SAFETY_DANGEROUS", "BLOCK_ONLY_HIGH")


# ============================================================
# DOCKER & MCP SETTINGS
# ============================================================
MCP_CONTAINER_NAME = os.getenv("MCP_CONTAINER_NAME", "mcp-toolkit")
if not MCP_CONTAINER_NAME:
    raise ValueError("MCP_CONTAINER_NAME not found in environment variables.")

DOCKER_COMMAND_TIMEOUT = int(os.getenv("DOCKER_COMMAND_TIMEOUT", "30"))
DOCKER_HEALTH_CHECK_TIMEOUT = int(os.getenv("DOCKER_HEALTH_CHECK_TIMEOUT", "5"))


# ============================================================
# NOTION API CONFIGURATION
# ============================================================
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
if not NOTION_TOKEN:
    logger.warning("NOTION_TOKEN not configured!")
    logger.warning("Get your token from: https://www.notion.so/my-integrations")
    logger.warning("Notion integration features will be disabled")
    NOTION_TOKEN = None

NOTION_API_VERSION = os.getenv("NOTION_API_VERSION", "2022-06-28")
NOTION_REQUEST_TIMEOUT = int(os.getenv("NOTION_REQUEST_TIMEOUT", "30"))


# ============================================================
# CHAT & UI SETTINGS
# ============================================================
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
CHAT_REQUEST_TIMEOUT = int(os.getenv("CHAT_REQUEST_TIMEOUT", "60"))

# Feature flags
ENABLE_DOCKER_TOOLS = os.getenv("ENABLE_DOCKER_TOOLS", "true").lower() == "true"
ENABLE_NOTION_INTEGRATION = (
    os.getenv("ENABLE_NOTION_INTEGRATION", "true").lower() == "true"
)
ENABLE_CODE_EXECUTION = os.getenv("ENABLE_CODE_EXECUTION", "false").lower() == "true"


# ============================================================
# LOGGING CONFIGURATION
# ============================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "logs")

# Ensure log directory exists
log_path = PROJECT_ROOT / LOG_DIR
log_path.mkdir(exist_ok=True)

# Log files
APP_LOG_FILE = os.getenv("APP_LOG_FILE", "logs/app.log")
BACKEND_LOG_FILE = os.getenv("BACKEND_LOG_FILE", "logs/backend.log")
FRONTEND_LOG_FILE = os.getenv("FRONTEND_LOG_FILE", "logs/frontend.log")
LLM_LOG_FILE = os.getenv("LLM_LOG_FILE", "logs/llm_service.log")
DOCKER_LOG_FILE = os.getenv("DOCKER_LOG_FILE", "logs/docker_service.log")

# Debug settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
LOG_API_REQUESTS = os.getenv("LOG_API_REQUESTS", "true").lower() == "true"
LOG_DOCKER_COMMANDS = os.getenv("LOG_DOCKER_COMMANDS", "true").lower() == "true"
LOG_LLM_INTERACTIONS = os.getenv("LOG_LLM_INTERACTIONS", "true").lower() == "true"


# ============================================================
# RATE LIMITING & PERFORMANCE
# ============================================================
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true"
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))

MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))

# Agentic loop settings
MAX_TOOL_ITERATIONS = int(os.getenv("MAX_TOOL_ITERATIONS", "5"))


# ============================================================
# SECURITY SETTINGS
# ============================================================
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501"
).split(",")


# ============================================================
# API METADATA
# ============================================================
API_TITLE = f"{APP_NAME} API"
API_DESCRIPTION = (
    f"An AI-powered API that integrates Google Gemini with Docker containers "
    f"for intelligent orchestration of MCP tools and Notion integration. "
    f"Environment: {ENVIRONMENT}"
)
API_VERSION = APP_VERSION


def get_active_features() -> List[str]:
    """
    Returns a list of currently active features.

    Returns:
        List of feature names that are enabled
    """
    features = []
    if ENABLE_DOCKER_TOOLS:
        features.append("Docker Tools")
    if ENABLE_NOTION_INTEGRATION and NOTION_TOKEN:
        features.append("Notion Integration")
    if ENABLE_CODE_EXECUTION:
        features.append("Code Execution")
    if ENABLE_RATE_LIMITING:
        features.append("Rate Limiting")

    return features


def get_config_summary() -> Dict[str, Any]:
    """
    Returns a summary of the current configuration.

    Returns:
        Dictionary with configuration details
    """
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "host": HOST,
        "port": PORT,
        "primary_model": GEMINI_MODEL_PRIMARY,
        "fallback_models": GEMINI_MODEL_FALLBACKS,
        "active_features": get_active_features(),
        "max_tool_iterations": MAX_TOOL_ITERATIONS,
        "max_conversation_history": MAX_CONVERSATION_HISTORY,
        "log_level": LOG_LEVEL,
        "debug_mode": DEBUG_MODE,
    }


def verify_config() -> Dict[str, Any]:
    """
    Validates that all critical configuration is present.
    Returns a dict with status information.

    Returns:
        Dictionary with validation status and issues
    """
    issues = []
    warnings = []

    # Critical checks
    if not GOOGLE_API_KEY:
        issues.append("GOOGLE_API_KEY is missing or invalid")

    if not MCP_CONTAINER_NAME:
        issues.append("MCP_CONTAINER_NAME is not configured")

    # Warning checks
    if not NOTION_TOKEN and ENABLE_NOTION_INTEGRATION:
        warnings.append(
            "NOTION_TOKEN is not configured but Notion integration is enabled"
        )

    if DEBUG_MODE and ENVIRONMENT == "production":
        warnings.append("DEBUG_MODE is enabled in production environment")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "google_api_configured": bool(GOOGLE_API_KEY),
        "notion_configured": bool(NOTION_TOKEN),
        "container_name": MCP_CONTAINER_NAME,
        "active_features": get_active_features(),
        "config_summary": get_config_summary(),
    }


# Log configuration status on import
if __name__ != "__main__":
    config_status = verify_config()

    logger.info("=" * 60)
    logger.info(f"Initializing {APP_NAME} v{APP_VERSION}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info("=" * 60)

    if config_status["valid"]:
        logger.info("✓ Configuration loaded successfully")
        logger.info(f"✓ Primary Model: {GEMINI_MODEL_PRIMARY}")
        logger.info(f"✓ Target Container: {MCP_CONTAINER_NAME}")
        logger.info(f"✓ Active Features: {', '.join(get_active_features())}")
    else:
        logger.warning("⚠ Configuration issues detected:")
        for issue in config_status["issues"]:
            logger.warning(f"  • {issue}")

    if config_status["warnings"]:
        logger.warning("⚠ Configuration warnings:")
        for warning in config_status["warnings"]:
            logger.warning(f"  • {warning}")

    logger.info("=" * 60)
