"""
Pydantic Schemas for API Data Validation

These models define the structure of JSON data for API requests and responses,
ensuring type safety and automatic validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ChatMessage(BaseModel):
    """
    Represents a single message in the conversation.
    """

    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="The message content")


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
    """

    status: str
    docker_connected: bool
    llm_configured: bool
    container_name: Optional[str] = None
    container_status: Optional[str] = None
