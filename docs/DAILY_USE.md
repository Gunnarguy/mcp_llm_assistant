# 🚀 Quick Start - MCP LLM Assistant

Super simple daily usage guide!

## Daemon Mode (Recommended - Runs in Background)

Reload your shell first: `source ~/.zshrc`

**Start services:**
```bash
mcp start
```

**Check status:**
```bash
mcp status
```

**Stop services:**
```bash
mcp stop
```

**Restart services:**
```bash
mcp restart
```

**View logs:**
```bash
mcp-logs-backend   # Backend logs
mcp-logs-frontend  # Frontend logs
```

Services run in background and stay alive! 🎉

## What It Does

1. Cleans up any old processes
2. Starts the backend API (port 8000)
3. Starts the chat UI (port 8501)
4. Opens in your browser automatically

## Troubleshooting

**Port already in use?**
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

**Check if it's running:**
```bash
curl http://127.0.0.1:8000/health
```

**View logs:**
```bash
tail -f backend.log
```

## Features

- 🤖 Gemini LLM with tool calling
- 🐳 Docker MCP integration
- 📝 Notion API (create/read pages)
- 🐙 GitHub API
- 🌐 Playwright (web automation)
- 🔍 Perplexity (AI search)

Enjoy! 🎉
