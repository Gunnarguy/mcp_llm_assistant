"""
FastAPI Backend Application

Main entry point for the MCP LLM Assistant API.
Provides endpoints for chat interaction and system health checks.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys

from app.schemas import ChatRequest, ChatResponse, HealthCheckResponse
from app.config import API_TITLE, API_DESCRIPTION, API_VERSION, verify_config
from app.services.llm_service import get_llm_service
from app.services.docker_service import get_docker_service


# Initialize FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts.
    Initializes services and validates configuration.
    """
    print("\n" + "=" * 60)
    print(f"🚀 Starting {API_TITLE}")
    print("=" * 60)

    # Verify configuration
    config_status = verify_config()
    if not config_status["valid"]:
        print("\n⚠ CONFIGURATION ISSUES DETECTED:")
        for issue in config_status["issues"]:
            print(f"  • {issue}")
        print("\nThe API will start, but some features may not work.")
        print("Please check your .env file.\n")

    # Initialize services (singletons will be created on first access)
    try:
        docker_service = get_docker_service()
        if docker_service.is_healthy():
            print("✓ Docker service: Ready")
        else:
            print("⚠ Docker service: Not healthy (container may not be running)")
    except Exception as e:
        print(f"✗ Docker service: Failed to initialize ({e})")

    try:
        if config_status["google_api_configured"]:
            llm_service = get_llm_service()
            print("✓ LLM service: Ready")
        else:
            print("⚠ LLM service: API key not configured")
    except Exception as e:
        print(f"✗ LLM service: Failed to initialize ({e})")

    print("\n" + "=" * 60)
    print("📡 API Documentation available at:")
    print("   http://127.0.0.1:8000/docs")
    print("=" * 60 + "\n")


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - provides basic API information.
    """
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Returns system status including Docker and LLM service availability.
    Useful for monitoring and debugging.
    """
    docker_service = get_docker_service()

    # Check Docker connection
    docker_connected = docker_service.is_healthy()

    # Get info - for MCP Gateway this returns gateway info, not container
    info = docker_service.get_container_info()
    container_info = info.get("gateway", "MCP Gateway")
    container_status = info.get("status", "disconnected")

    # Check LLM configuration
    config_status = verify_config()
    llm_configured = config_status["google_api_configured"]

    # Determine overall status
    if docker_connected and llm_configured:
        status = "healthy"
    elif docker_connected or llm_configured:
        status = "partial"
    else:
        status = "unhealthy"

    return HealthCheckResponse(
        status=status,
        docker_connected=docker_connected,
        llm_configured=llm_configured,
        container_name=container_info,
        container_status=container_status,
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint.

    Receives a user prompt and conversation history, processes it through
    the LLM with tool-use capabilities, and returns the assistant's response.

    The LLM can autonomously decide to execute Docker commands if needed
    to answer the user's question.

    Args:
        request: ChatRequest containing prompt and history

    Returns:
        ChatResponse with the assistant's reply

    Raises:
        HTTPException: If services are not available or errors occur
    """
    try:
        # Validate that services are available
        llm_service = get_llm_service()
        docker_service = get_docker_service()

        if not docker_service.is_healthy():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Docker service is not available. "
                    "Please ensure Docker Desktop is running and the "
                    "MCP container is started."
                ),
            )

        # Log the incoming request
        print(f"\n{'='*60}")
        print(f"📨 New chat request")
        print(f"{'='*60}")
        print(
            f"Prompt: {request.prompt[:100]}{'...' if len(request.prompt) > 100 else ''}"
        )
        print(f"History length: {len(request.history)} messages")

        # Generate response using the agentic LLM
        reply = await llm_service.get_response(
            prompt=request.prompt, history=request.history
        )

        print(f"\n✓ Response generated successfully")
        print(f"{'='*60}\n")

        return ChatResponse(reply=reply)

    except ValueError as e:
        # Configuration errors
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

    except Exception as e:
        # Unexpected errors
        print(f"\n✗ Error processing chat request: {str(e)}")
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    print(f"\n✗ Unhandled exception: {exc}")
    import traceback

    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred", "error": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("🚀 Starting FastAPI server directly")
    print("=" * 60)
    print("\nFor development, use:")
    print("  uvicorn app.main:app --reload")
    print("\nFor production, use:")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("=" * 60 + "\n")

    uvicorn.run(
        "app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
