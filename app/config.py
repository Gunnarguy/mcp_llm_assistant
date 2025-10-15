"""
Configuration Management

Securely loads environment variables from .env file and validates
that all required configuration is present.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from app.logger import setup_logger

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


# --- Google Gemini API Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
    logger.warning("GOOGLE_API_KEY not configured properly!")
    logger.warning("Get your free API key from: https://aistudio.google.com/app/apikey")
    logger.warning("Then add it to your .env file")
    GOOGLE_API_KEY = None  # Allow app to start but LLM won't work


# --- Docker Configuration ---
MCP_CONTAINER_NAME = os.getenv("MCP_CONTAINER_NAME", "mcp-toolkit")
if not MCP_CONTAINER_NAME:
    raise ValueError("MCP_CONTAINER_NAME not found in environment variables.")


# --- Application Configuration ---
API_TITLE = "MCP LLM Assistant API"
API_DESCRIPTION = (
    "An AI-powered API that integrates Google Gemini with Docker containers "
    "for intelligent orchestration of MCP tools."
)
API_VERSION = "1.0.0"

# Server settings
HOST = "127.0.0.1"
PORT = 8000

# LLM Model Selection with Automatic Fallback
# Primary model - best balance of performance and limits
GEMINI_MODEL_PRIMARY = "gemini-2.5-flash"

# Fallback models (tried in order when rate limits hit)
GEMINI_MODEL_FALLBACKS = [
    "gemini-2.5-flash-lite",  # Faster, cheaper, different rate limits
    "gemini-2.0-flash",  # Older but stable, separate quota
    "gemini-1.5-flash",  # Fallback to 1.5 generation
]

# Currently active model (starts with primary)
GEMINI_MODEL = GEMINI_MODEL_PRIMARY


def verify_config():
    """
    Validates that all critical configuration is present.
    Returns a dict with status information.
    """
    issues = []

    if not GOOGLE_API_KEY:
        issues.append("GOOGLE_API_KEY is missing or invalid")

    if not MCP_CONTAINER_NAME:
        issues.append("MCP_CONTAINER_NAME is not configured")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "google_api_configured": bool(GOOGLE_API_KEY),
        "container_name": MCP_CONTAINER_NAME,
    }


# Log configuration status on import
if __name__ != "__main__":
    config_status = verify_config()
    if config_status["valid"]:
        logger.info("Configuration loaded successfully")
        logger.info(f"Model: {GEMINI_MODEL}")
        logger.info(f"Target Container: {MCP_CONTAINER_NAME}")
    else:
        logger.warning("Configuration issues detected:")
        for issue in config_status["issues"]:
            logger.warning(f"  {issue}")
