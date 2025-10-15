"""
FastAPI Backend Application - Enhanced Edition

Main entry point for the MCP AI Assistant API.
Provides endpoints for chat interaction, system health checks, and configuration.

Features:
- Intelligent chat with agentic tool use
- Comprehensive health monitoring
- Configuration introspection
- Enhanced error handling
- Request logging and metrics
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import time

from app.schemas import ChatRequest, ChatResponse, HealthCheckResponse
from app.config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    APP_NAME,
    APP_VERSION,
    ENVIRONMENT,
    CORS_ORIGINS,
    GEMINI_MODEL_PRIMARY,
    verify_config,
    get_config_summary,
    get_active_features,
)
from app.services.llm_service import get_llm_service
from app.services.docker_service import get_docker_service
from app.logger import setup_logger

# Setup logger
logger = setup_logger(__name__, log_file="logs/backend.log")


# Initialize FastAPI application with enhanced metadata
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "System",
            "description": "System health, status, and configuration endpoints",
        },
        {
            "name": "Chat",
            "description": "AI chat interface with agentic tool capabilities",
        },
        {
            "name": "Metrics",
            "description": "Performance metrics and statistics",
        },
    ],
)

# Add CORS middleware with configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Track request metrics
request_metrics = {"total_requests": 0, "total_errors": 0, "total_chat_requests": 0}


# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts.
    Initializes services and validates configuration.
    """
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info("=" * 60)

    print("\n" + "=" * 60)
    print(f"🚀 Starting {APP_NAME} v{APP_VERSION}")
    print(f"Environment: {ENVIRONMENT}")
    print("=" * 60)

    # Verify configuration
    config_status = verify_config()

    if config_status["valid"]:
        print("\n✓ Configuration validated successfully")
        logger.info("Configuration validated successfully")
    else:
        print("\n⚠ CONFIGURATION ISSUES DETECTED:")
        logger.warning("Configuration issues detected:")
        for issue in config_status["issues"]:
            print(f"  • {issue}")
            logger.warning(f"  • {issue}")
        print("\nThe API will start, but some features may not work.")
        print("Please check your .env file.\n")

    # Show warnings if any
    if config_status.get("warnings"):
        print("\n⚠ CONFIGURATION WARNINGS:")
        for warning in config_status["warnings"]:
            print(f"  • {warning}")
            logger.warning(f"  • {warning}")

    # Show active features
    active_features = get_active_features()
    if active_features:
        print(f"\n✓ Active Features: {', '.join(active_features)}")
        logger.info(f"Active Features: {', '.join(active_features)}")

    # Initialize Docker service
    try:
        docker_service = get_docker_service()
        if docker_service.is_healthy():
            print("✓ Docker service: Ready")
            logger.info("Docker service initialized successfully")
        else:
            print("⚠ Docker service: Not healthy (container may not be running)")
            logger.warning("Docker service not healthy")
    except Exception as e:
        print(f"✗ Docker service: Failed to initialize ({e})")
        logger.error(f"Docker service initialization failed: {e}")

    # Initialize LLM service
    try:
        if config_status["google_api_configured"]:
            get_llm_service()  # Initialize the service
            print(f"✓ LLM service: Ready (Model: {GEMINI_MODEL_PRIMARY})")
            logger.info(f"LLM service initialized with model: {GEMINI_MODEL_PRIMARY}")
        else:
            print("⚠ LLM service: API key not configured")
            logger.warning("LLM service not configured - API key missing")
    except Exception as e:
        print(f"✗ LLM service: Failed to initialize ({e})")
        logger.error(f"LLM service initialization failed: {e}")

    print("\n" + "=" * 60)
    print("📡 API Documentation available at:")
    print("   http://127.0.0.1:8000/docs")
    print("   http://127.0.0.1:8000/redoc")
    print("=" * 60 + "\n")

    logger.info("Startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when application shuts down."""
    logger.info("Shutting down application")
    print("\n👋 Shutting down gracefully...")


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - provides basic API information and quick links.
    """
    request_metrics["total_requests"] += 1
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "config": "/config",
        "metrics": "/metrics",
        "message": "🤖 Welcome to MCP AI Assistant API!",
    }


@app.get("/config", tags=["System"])
async def get_configuration():
    """
    Returns current configuration summary (sensitive data excluded).
    """
    request_metrics["total_requests"] += 1
    config_summary = get_config_summary()
    config_status = verify_config()

    return {
        "configuration": config_summary,
        "status": config_status,
        "features": get_active_features(),
    }


@app.get("/metrics", tags=["Metrics"])
async def get_metrics():
    """
    Returns application metrics and statistics.
    """
    request_metrics["total_requests"] += 1

    # Calculate error rate
    error_rate = 0.0
    if request_metrics["total_requests"] > 0:
        error_rate = (
            request_metrics["total_errors"] / request_metrics["total_requests"]
        ) * 100

    return {
        "requests": {
            "total": request_metrics["total_requests"],
            "chat": request_metrics["total_chat_requests"],
            "errors": request_metrics["total_errors"],
            "error_rate_percent": round(error_rate, 2),
        },
        "services": {
            "docker": get_docker_service().is_healthy(),
            "llm": verify_config()["google_api_configured"],
        },
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint with detailed system status.

    Returns system status including Docker and LLM service availability.
    Useful for monitoring and debugging.
    """
    request_metrics["total_requests"] += 1

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
        model=GEMINI_MODEL_PRIMARY if llm_configured else None,
        environment=ENVIRONMENT,
        version=APP_VERSION,
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint with enhanced error handling and logging.

    Receives a user prompt and conversation history, processes it through
    the LLM with tool-use capabilities, and returns the assistant's response.

    The LLM can autonomously decide to execute Docker commands or call Notion API
    if needed to answer the user's question.

    Args:
        request: ChatRequest containing prompt and history

    Returns:
        ChatResponse with the assistant's reply

    Raises:
        HTTPException: If services are not available or errors occur
    """
    request_metrics["total_requests"] += 1
    request_metrics["total_chat_requests"] += 1

    try:
        # Validate that services are available
        llm_service = get_llm_service()
        docker_service = get_docker_service()

        if not docker_service.is_healthy():
            request_metrics["total_errors"] += 1
            logger.warning("Chat request failed: Docker service not available")
            raise HTTPException(
                status_code=503,
                detail=(
                    "Docker service is not available. "
                    "Please ensure Docker Desktop is running and the "
                    "MCP container is started."
                ),
            )

        # Log the incoming request
        logger.info("=" * 60)
        logger.info("📨 New chat request")
        logger.info(
            f"Prompt: {request.prompt[:100]}{'...' if len(request.prompt) > 100 else ''}"
        )
        logger.info(f"History length: {len(request.history)} messages")

        print(f"\n{'=' * 60}")
        print("📨 New chat request")
        print(f"{'=' * 60}")
        print(
            f"Prompt: {request.prompt[:100]}{'...' if len(request.prompt) > 100 else ''}"
        )
        print(f"History length: {len(request.history)} messages")

        # Generate response using the agentic LLM
        start_time = time.time()
        reply = await llm_service.get_response(
            prompt=request.prompt, history=request.history
        )
        elapsed_time = time.time() - start_time

        logger.info(f"✓ Response generated successfully in {elapsed_time:.2f}s")
        print(f"\n✓ Response generated successfully in {elapsed_time:.2f}s")
        print(f"{'=' * 60}\n")

        return ChatResponse(reply=reply)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except ValueError as e:
        # Configuration errors
        request_metrics["total_errors"] += 1
        logger.error(f"Configuration error in chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

    except Exception as e:
        # Unexpected errors
        request_metrics["total_errors"] += 1
        logger.error(
            f"Unexpected error processing chat request: {str(e)}", exc_info=True
        )
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
    request_metrics["total_errors"] += 1
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
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
    print(f"🚀 Starting {APP_NAME} FastAPI server directly")
    print("=" * 60)
    print("\nFor development, use:")
    print("  uvicorn app.main:app --reload")
    print("\nFor production, use:")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("=" * 60 + "\n")

    uvicorn.run(
        "app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
