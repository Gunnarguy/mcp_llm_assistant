# MCP LLM Assistant

An AI assistant that can interact with Docker MCP (Model Context Protocol) servers including GitHub, Notion, Perplexity, and Playwright.

## 🚀 Quick Start (First Time Setup)

```bash
# 1. Run setup once
./setup.sh

# 2. Edit .env file and add your Google API key
# GOOGLE_API_KEY=your_key_here

# 3. Start the application
./start.sh
```

## 📖 Daily Usage

### Start Everything
```bash
./start.sh
```
This will:
- Start the backend server
- Open the chat UI in your browser at http://localhost:8501
- Press `Ctrl+C` in the terminal when you're done

### Stop Everything (if needed)
```bash
./stop.sh
```
Use this if you closed the terminal without pressing `Ctrl+C`, or if something got stuck.

## 🎯 What Can It Do?

Once running, you can ask the AI to:

- **"list servers"** - Show all available MCP servers
- **"notion"** - Interact with Notion
- **"github"** - Check GitHub info
- **"what tools do you have?"** - See available commands

The AI will automatically execute Docker MCP commands to answer your questions.

## 📝 Files You Care About

- **`.env`** - Your API keys (edit this)
- **`start.sh`** - Start everything (run this)
- **`stop.sh`** - Stop everything (run if needed)
- **`backend.log`** - Backend logs (check if errors)

## 🔧 Troubleshooting

**Backend won't start?**
```bash
cat backend.log  # Check for errors
```

**Port already in use?**
```bash
./stop.sh  # Stop everything
./start.sh # Try again
```

**Need to reset?**
```bash
./stop.sh
rm -rf venv
./setup.sh
# Add your API key to .env again
./start.sh
```

## 🛠️ Requirements

- Docker Desktop (must be running)
- Docker MCP Gateway (must be configured)
- Python 3.12+
- Google Gemini API key (free at [Google AI Studio](https://aistudio.google.com/app/apikey))

## 🔒 Security

**IMPORTANT**: This application requires sensitive API credentials.

### First-Time Setup

1. Copy the template file:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # Get your key at: https://aistudio.google.com/app/apikey
   GOOGLE_API_KEY="your_actual_key_here"
   ```

3. **NEVER commit `.env` to version control**:
   ```bash
   # Verify it's gitignored
   git check-ignore .env  # Should output: .env
   ```

### API Key Management

- **Google Gemini API**: Free tier at [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Rotate keys** every 90 days
- **Revoke immediately** if exposed in commits/logs
- Store keys in password manager, not in code

See `SECURITY.md` for vulnerability reporting and best practices.

## � MCP Servers Included

- **github-official** - GitHub integration
- **notion** - Notion workspace access
- **perplexity-ask** - AI-powered search
- **playwright** - Browser automation

### 1. Clone and Setup

```bash
# Navigate to your project
cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.template .env

# Edit with your API key
nano .env
```

Add your Gemini API key:
```env
GOOGLE_API_KEY="your_actual_api_key_here"
MCP_CONTAINER_NAME="mcp-toolkit"
```

### 3. Verify Docker Container

Make sure your MCP container is running:

```bash
# List all containers
docker ps

# If your container name is different, update .env
# The name should match what you see in `docker ps`
```

### 4. Start the Backend

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload
```

You should see:
```
✓ Configuration loaded successfully
✓ Successfully connected to Docker daemon
✓ Connected to container: 'mcp-toolkit' (status: running)
✓ Docker service: Ready
✓ LLM service: Ready
```

Keep this terminal open!

### 5. Start the Frontend

In a **new terminal**:

```bash
# Navigate to project
cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant

# Activate virtual environment
source venv/bin/activate

# Start Streamlit
streamlit run frontend/chat_ui.py
```

The app will open in your browser at `http://localhost:8501`

---

## 💬 Usage Examples

Once both servers are running, try these prompts in the chat:

### Basic Docker Commands
```
"What containers are running on this system?"
"Show me the last 20 lines of logs from the MCP container"
"Execute the command 'ls -la /app' in the container"
```

### MCP-Specific Commands
```
"List all MCP servers"
"What MCP clients are configured?"
"Show me the MCP server list"
"Execute 'docker mcp server list' in the container"
```

### Intelligent Queries
```
"Is the notion MCP server running?"
"What's the status of my MCP setup?"
"Can you check if the github server is configured?"
```

The AI will automatically determine when it needs to execute Docker commands to answer your question!

---

## 🔧 Project Structure

```
mcp_llm_assistant/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── config.py            # Configuration management
│   ├── schemas.py           # Pydantic models for validation
│   └── services/
│       ├── __init__.py
│       ├── llm_service.py   # Gemini API & agentic loop
│       └── docker_service.py # Docker SDK operations
├── frontend/
│   └── chat_ui.py           # Streamlit chat interface
├── .env                     # Your API keys (create from template)
├── .env.template            # Template for environment variables
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🛠️ How It Works

### The Agentic Loop

1. **User sends a message** via Streamlit UI
2. **Streamlit sends HTTP POST** to FastAPI `/chat` endpoint
3. **FastAPI forwards to LLM Service** with conversation history
4. **Gemini analyzes the request** and decides if it needs to use tools
5. If tools needed:
   - **Gemini returns a function call** (e.g., "execute_command")
   - **Backend executes the function** via Docker SDK
   - **Result is sent back to Gemini**
   - **Gemini generates natural response** using the result
6. **Final response is returned** to user via FastAPI → Streamlit

### Available Tools (Functions)

The LLM has access to these tools:

1. **execute_command(command: str)**
   - Executes any shell command inside the MCP container
   - Example: `docker mcp server list`

2. **list_containers()**
   - Lists all Docker containers on the system
   - Shows status, image, and ID

3. **get_logs(tail: int = 50)**
   - Retrieves recent logs from the MCP container
   - Useful for debugging

---

## 📊 API Documentation

While the backend is running, access interactive API docs at:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Health Check:** http://127.0.0.1:8000/health

### Key Endpoints

#### POST `/chat`
Send a chat message and get an AI response.

**Request:**
```json
{
  "prompt": "What MCP servers are running?",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response:**
```json
{
  "reply": "I found 3 MCP servers running: notion, github-official, and playwright."
}
```

#### GET `/health`
Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "docker_connected": true,
  "llm_configured": true,
  "container_name": "mcp-toolkit",
  "container_status": "running"
}
```

---

## 🐛 Troubleshooting

### "Cannot connect to Docker daemon"

**Problem:** Docker is not running or not accessible.

**Solution:**
```bash
# Open Docker Desktop from Applications
# Verify it's running:
docker ps

# If it shows containers, Docker is working
```

### "Container 'mcp-toolkit' not found"

**Problem:** Container name in `.env` doesn't match your actual container.

**Solution:**
```bash
# Find your actual container name
docker ps

# Update .env with the correct name
nano .env
# Change: MCP_CONTAINER_NAME="your_actual_container_name"

# Restart the backend
```

### "GOOGLE_API_KEY not configured"

**Problem:** API key is missing or invalid.

**Solution:**
```bash
# Get free API key from:
# https://aistudio.google.com/app/apikey

# Add to .env
nano .env
# Add: GOOGLE_API_KEY="your_key_here"

# Restart the backend
```

### Backend starts but chat doesn't work

**Problem:** Services may not be initialized properly.

**Solution:**
```bash
# Check backend logs in the terminal where uvicorn is running
# Look for:
# ✓ Docker service: Ready
# ✓ LLM service: Ready

# If not, check the error messages and fix configuration
```

### "Module not found" errors

**Problem:** Dependencies not installed or wrong Python environment.

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🔐 Security Notes

- **Never commit your `.env` file** to version control (it's in `.gitignore`)
- **API keys are sensitive** - treat them like passwords
- **Default setup binds to localhost** - not exposed to network
- For production: Configure proper CORS origins in `app/main.py`

---

## 🚀 Advanced Usage

### Using Different Gemini Models

Edit `app/config.py`:

```python
# For faster responses (free tier)
GEMINI_MODEL = "gemini-2.0-flash-exp"

# For better reasoning (requires paid tier)
GEMINI_MODEL = "gemini-1.5-pro"

# For maximum capability (requires paid tier)
GEMINI_MODEL = "gemini-2.5-pro"
```

### Adding Custom Tools

Edit `app/services/llm_service.py` to add new tools:

```python
def _get_tool_declarations(self):
    return [
        {
            "function_declarations": [
                # Your new tool here
                {
                    "name": "my_custom_tool",
                    "description": "What this tool does",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "arg1": {"type": "string"}
                        },
                        "required": ["arg1"]
                    }
                }
            ]
        }
    ]
```

Then implement the function in `_execute_function_call()`.

### Running in Production

```bash
# Use gunicorn for better performance
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 📚 Technology Stack

- **Backend:** FastAPI 0.109+ (async Python web framework)
- **Frontend:** Streamlit 1.31+ (interactive web UI)
- **LLM:** Google Gemini API (with function calling)
- **Container Management:** Docker SDK for Python 7.0+
- **Validation:** Pydantic 2.0+ (data models)
- **Server:** Uvicorn (ASGI server)

---

## 🤝 Contributing

This is a personal project, but improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

This project is for personal use. Modify as needed for your purposes.

---

## 🙏 Acknowledgments

- Built following the architecture document "Architecting Your Personal AI Assistant"
- Uses Google's Gemini API for advanced AI capabilities
- Leverages Docker's powerful containerization platform

---

## 📧 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the backend logs in your terminal
3. Check the [API documentation](http://127.0.0.1:8000/docs) for endpoint details
4. Verify your `.env` configuration

---

**Happy chatting with your containers! 🤖🐳**
