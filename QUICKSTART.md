# 🚀 QUICK START GUIDE

Get your MCP LLM Assistant running in 5 minutes!

## Prerequisites Check

- ✅ macOS with Docker Desktop installed
- ✅ Docker Desktop is **running** (check the menu bar)
- ✅ Python 3.9+ installed
- ✅ A Docker container running (check with `docker ps`)

## Step 1: Get Your Free API Key (2 minutes)

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with "AI...")

## Step 2: Setup (1 minute)

```bash
cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant

# Run the automated setup
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create your `.env` file

## Step 3: Configure (1 minute)

```bash
# Edit the .env file
nano .env
```

Paste your API key:
```env
GOOGLE_API_KEY="AIza...your_actual_key_here"
MCP_CONTAINER_NAME="mcp-toolkit"
```

**Important:** Check your container name with `docker ps` and update if different!

Save and exit (Ctrl+O, Enter, Ctrl+X)

## Step 4: Launch (1 minute)

### Terminal 1 - Backend:
```bash
cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant
./start_backend.sh
```

Wait for:
```
✓ Configuration loaded successfully
✓ Docker service: Ready
✓ LLM service: Ready
```

### Terminal 2 - Frontend:
```bash
cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant
./start_frontend.sh
```

The chat UI will open in your browser automatically! 🎉

## Try It Out!

Ask questions like:
- "What containers are running?"
- "List all MCP servers"
- "Show me the container logs"
- "Execute 'docker mcp server list'"

---

## Troubleshooting

### "Docker is not running"
→ Open Docker Desktop from Applications

### "Container not found"
→ Run `docker ps` and update `MCP_CONTAINER_NAME` in `.env`

### "API key not configured"
→ Make sure you added your Gemini API key to `.env`

### "Cannot connect to backend"
→ Make sure Terminal 1 (backend) is running and shows "Ready"

---

## What You Built

You now have:
- 🤖 An AI assistant that can interact with Docker containers
- ⚡ A FastAPI backend (http://127.0.0.1:8000)
- 🎨 A Streamlit chat UI (http://localhost:8501)
- 🧠 Google Gemini AI with tool-use capabilities
- 🐳 Direct Docker container orchestration

The AI can autonomously execute commands in your containers to answer questions!

---

**Need more details?** Check the full `README.md`

**API Documentation:** http://127.0.0.1:8000/docs (when backend is running)
