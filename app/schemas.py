"""
Pydantic Schemas for API Data Validation - Enhanced Edition

These models define the structure of JSON data for API requests and responses,
ensuring type safety and automatic validation.

Features:
- Comprehensive field validation
- Rich examples for documentation
- Optional fields with defaults
- Type hints for IDE support
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ChatMessage(BaseModel):
    """
    Represents a single message in the conversation.
    """

    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="The message content")
    timestamp: Optional[str] = Field(
        None, description="ISO format timestamp of the message"
    )


class ChatRequest(BaseModel):
    """
    Defines the structure for an incoming chat request.
    Includes the user's latest message and the conversation history.
    """

    prompt: str = Field(..., description="The user's current message", min_length=1)
    history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Previous messages in the conversation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What containers are running?",
                "history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help you?"},
                ],
            }
        }


class ChatResponse(BaseModel):
    """
    Defines the structure for the response sent back to the client.
    Contains the assistant's generated message.
    """

    reply: str = Field(..., description="The assistant's response message")

    class Config:
        json_schema_extra = {
            "example": {"reply": "There are 3 containers currently running..."}
        }


class HealthCheckResponse(BaseModel):
    """
    Response model for the health check endpoint.
    Provides comprehensive system health information.
    """

    status: str = Field(
        ..., description="Overall system status: healthy, partial, or unhealthy"
    )
    docker_connected: bool = Field(
        ..., description="Docker service connectivity status"
    )
    llm_configured: bool = Field(..., description="LLM service configuration status")
    container_name: Optional[str] = Field(
        None, description="Name of the MCP container or gateway"
    )
    container_status: Optional[str] = Field(
        None, description="Status of the Docker container"
    )
    model: Optional[str] = Field(None, description="Active LLM model name")
    environment: Optional[str] = Field(
        None, description="Current environment (development/production)"
    )
    version: Optional[str] = Field(None, description="Application version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "docker_connected": True,
                "llm_configured": True,
                "container_name": "MCP Docker Gateway",
                "container_status": "running",
                "model": "gemini-2.5-flash",
                "environment": "development",
                "version": "2.0.0",
            }
        }
