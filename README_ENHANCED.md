# 🤖 MCP AI Assistant - Enhanced Edition

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Intelligent AI-powered assistant for Docker MCP management and Notion integration**

[Features](#-features) • [Quick Start](#-quick-start) • [Configuration](#-configuration) • [API Docs](#-api-documentation) • [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

### 🧠 **Intelligent AI Assistant**
- **Natural Language Interface**: Chat naturally with your Docker containers and Notion workspace
- **Agentic Tool Use**: AI autonomously decides when to use tools (Docker commands, Notion API)
- **Multi-Turn Conversations**: Maintains context across multiple exchanges
- **Smart Suggestions**: Quick-action buttons for common tasks

### 🐳 **Docker Integration**
- Execute MCP commands through natural language
- List and monitor containers in real-time
- Retrieve and analyze container logs
- Health monitoring and status checks

### 📝 **Notion Integration**
- **Full REST API Access**: Search, create, update pages and databases
- **Database Management**: Query databases, manage properties
- **Schema Updates**: Add/modify database properties dynamically
- **Workspace Search**: Find any content across your Notion workspace

### 🎨 **Beautiful UI**
- **Modern Design**: Gradient backgrounds, smooth animations, custom styling
- **Responsive Layout**: Works on desktop and tablet
- **Dark Theme**: Eye-friendly interface with accent colors
- **Status Indicators**: Real-time health monitoring with visual feedback

### 🔧 **Developer Features**
- **Comprehensive Configuration**: 50+ environment variables for customization
- **Health Endpoints**: Monitor system status programmatically
- **Metrics & Analytics**: Track request counts, error rates, response times
- **Extensive Logging**: Detailed logs for debugging and monitoring
- **Auto-Fallback**: Automatic model switching on rate limits

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Docker Desktop** running ([Download](https://www.docker.com/products/docker-desktop))
- **Google Gemini API Key** ([Get free key](https://aistudio.google.com/app/apikey))
- **Notion Integration Token** (optional) ([Create integration](https://www.notion.so/my-integrations))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/mcp_llm_assistant.git
cd mcp_llm_assistant

# 2. Run setup script (creates venv, installs dependencies)
./setup.sh

# 3. Configure environment variables
cp .env.template .env
# Edit .env and add your API keys

# 4. Start the application
./daemon.sh start
```

That's it! 🎉

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ⚙️ Configuration

### Basic Configuration

Edit `.env` file with your API keys:

```bash
# Required
GOOGLE_API_KEY="your_gemini_api_key_here"  # pragma: allowlist secret

# Optional (for Notion features)
NOTION_TOKEN="your_notion_integration_token_here"  # pragma: allowlist secret

# Docker
MCP_CONTAINER_NAME="mcp-gateway"
```

### Advanced Configuration

The `.env.enhanced` file contains **50+ configuration options**:

#### Application Settings
```bash
APP_NAME="MCP AI Assistant"
APP_VERSION="2.0.0"
ENVIRONMENT="development"  # development, production, testing
```

#### LLM Configuration
```bash
# Model selection
GEMINI_MODEL_PRIMARY="gemini-2.5-flash"
GEMINI_MODEL_FALLBACK_1="gemini-2.5-flash-lite"

# Model parameters
GEMINI_TEMPERATURE=0.7  # 0.0-1.0 (creativity)
GEMINI_TOP_P=0.95
GEMINI_MAX_OUTPUT_TOKENS=2048

# Safety settings
GEMINI_SAFETY_HARASSMENT="BLOCK_ONLY_HIGH"
```

#### Feature Flags
```bash
ENABLE_DOCKER_TOOLS=true
ENABLE_NOTION_INTEGRATION=true
ENABLE_CODE_EXECUTION=false
ENABLE_RATE_LIMITING=false
```

#### Performance Tuning
```bash
MAX_TOOL_ITERATIONS=5  # Agentic loop limit
MAX_CONVERSATION_HISTORY=20  # Context window management
CHAT_REQUEST_TIMEOUT=60  # Seconds
DOCKER_COMMAND_TIMEOUT=30
```

#### Logging
```bash
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
DEBUG_MODE=false
LOG_API_REQUESTS=true
LOG_DOCKER_COMMANDS=true
LOG_LLM_INTERACTIONS=true
```

See `.env.enhanced` for the complete list of options!

---

## 📖 Usage Examples

### Docker Management

```
"List all containers"
"Show me the logs for mcp-gateway"
"What MCP servers are available?"
"Execute: docker mcp server list"
```

### Notion Integration

```
"Search my Notion workspace"
"List all my databases"
"Create a new page in my Projects database"
"Add a 'Priority' property to my Tasks database"
"Query my Arsenal database"
```

### System Operations

```
"Run a health check"
"What's the system status?"
"Tell me about the configuration"
"Show me the active features"
```

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────┐
│         Streamlit Frontend (8501)           │
│  • Beautiful UI with custom CSS             │
│  • Real-time health monitoring              │
│  • Smart suggestions & quick actions        │
└──────────────────┬──────────────────────────┘
                   │ HTTP
                   ▼
┌─────────────────────────────────────────────┐
│          FastAPI Backend (8000)             │
│  • Request handling & validation            │
│  • Health checks & metrics                  │
│  • Error handling & logging                 │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│   LLM Service    │  │  Docker Service  │
│  • Gemini API    │  │  • MCP Gateway   │
│  • Tool calling  │  │  • Container ops │
│  • Auto-fallback │  │  • Log retrieval │
└────────┬─────────┘  └─────────┬────────┘
         │                      │
         ▼                      ▼
┌──────────────────┐  ┌──────────────────┐
│   Notion API     │  │  Docker Engine   │
│  • REST calls    │  │  • Containers    │
│  • CRUD ops      │  │  • MCP servers   │
└──────────────────┘  └──────────────────┘
```

---

## 📚 API Documentation

### Available Endpoints

#### `GET /`
Root endpoint with API information

#### `GET /health`
Comprehensive health check
```json
{
  "status": "healthy",
  "docker_connected": true,
  "llm_configured": true,
  "container_name": "MCP Docker Gateway",
  "container_status": "running",
  "model": "gemini-2.5-flash",
  "environment": "development",
  "version": "2.0.0"
}
```

#### `GET /config`
Current configuration summary (sensitive data excluded)

#### `GET /metrics`
Application metrics and statistics
```json
{
  "requests": {
    "total": 156,
    "chat": 42,
    "errors": 2,
    "error_rate_percent": 1.28
  },
  "services": {
    "docker": true,
    "llm": true
  }
}
```

#### `POST /chat`
Main chat endpoint
```json
{
  "prompt": "List all containers",
  "history": []
}
```

**Interactive docs**: http://localhost:8000/docs

---

## 🛠️ Daemon Management

The `daemon.sh` script provides convenient control:

```bash
# Start both backend and frontend
./daemon.sh start

# Stop all services
./daemon.sh stop

# Restart services
./daemon.sh restart

# Check status
./daemon.sh status
```

### Manual Control

```bash
# Backend only
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend only
streamlit run frontend/chat_ui.py --server.port 8501
```

---

## 🔍 Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
tail -f logs/backend.log
```

**Verify configuration:**
```bash
curl http://localhost:8000/health
```

**Common issues:**
- Missing `GOOGLE_API_KEY` in `.env`
- Port 8000 already in use: `lsof -ti:8000 | xargs kill -9`
- Docker not running: Start Docker Desktop

### Frontend Shows "Backend Unreachable"

1. Ensure backend is running: `./daemon.sh status`
2. Check backend health: `curl http://localhost:8000/health`
3. Review logs: `tail -f logs/frontend.log`

### Rate Limit Errors

The system automatically switches to fallback models when hitting rate limits. Check logs for:
```
Switching to fallback model: gemini-2.5-flash-lite
```

If all models are rate-limited, wait a few minutes and try again.

### Docker Connection Issues

```bash
# Verify Docker is running
docker ps

# Check MCP Gateway
docker mcp server list

# Restart Docker if needed
```

---

## 📊 Monitoring & Logs

### Log Files

All logs are in the `logs/` directory:

- `backend.log` - FastAPI server logs
- `frontend.log` - Streamlit UI logs
- `llm_service.log` - LLM interactions and tool calls
- `docker_service.log` - Docker operations
- `config.log` - Configuration loading

### Real-Time Monitoring

```bash
# Watch all logs
tail -f logs/*.log

# Backend only
tail -f logs/backend.log

# LLM interactions
tail -f logs/llm_service.log
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

---

## 🎨 Customization

### UI Theming

Edit `frontend/chat_ui.py` to customize colors:

```python
CUSTOM_CSS = """
<style>
    /* Primary color */
    --primary-color: #4F46E5;  /* Indigo */

    /* Background */
    --background-gradient: linear-gradient(135deg, #0E1117 0%, #1a1d29 100%);
</style>
"""
```

### System Prompt

Modify `app/services/llm_service.py` → `_get_system_instruction()`:

```python
return """You are an AI agent with tools for Docker MCP and Notion API.
Your custom instructions here...
"""
```

### Add New Tools

1. Add tool declaration in `_get_tool_declarations()`
2. Add handler in `_execute_function_call()`
3. Implement logic in service layer

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use environment-specific configs** - Separate dev/prod settings
3. **Rotate API keys regularly** - Update in Gemini/Notion dashboards
4. **Enable rate limiting** - Set `ENABLE_RATE_LIMITING=true` in production
5. **Review logs regularly** - Monitor for suspicious activity
6. **Use HTTPS in production** - Configure reverse proxy (nginx/Caddy)

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp_llm_assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp_llm_assistant/discussions)
- **Email**: your.email@example.com

---

## 🙏 Acknowledgments

- **Google Gemini** - AI language model
- **FastAPI** - Modern Python web framework
- **Streamlit** - Beautiful data apps
- **Docker** - Container platform
- **Notion** - Workspace integration

---

<div align="center">

**Made with ❤️ using AI**

[⬆ Back to Top](#-mcp-ai-assistant---enhanced-edition)

</div>
