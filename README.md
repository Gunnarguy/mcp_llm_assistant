# MCP LLM Assistant

AI assistant that connects to Docker MCP servers (Notion, GitHub, Playwright, Perplexity).

## Quick Start

```bash
# First time
./setup.sh              # Install dependencies
# Edit .env, add GOOGLE_API_KEY

# Daily use
./daemon.sh start       # Start (background)
./daemon.sh status      # Check status
./daemon.sh stop        # Stop
```

Open browser: <http://localhost:8501>

## What It Does

Ask the AI to:
- Search Notion databases
- Check GitHub repos
- Automate browser tasks
- Search the web with Perplexity

It automatically calls Docker MCP tools to complete your requests.

## Files

- `.env` - Your API keys
- `daemon.sh` - Main control script
- `setup.sh` - One-time setup
- `README.md` - This file
- `SECURITY.md` - Security best practices
- `OVERVIEW.md` - Architecture details

## Troubleshooting

**Services won't start?**

```bash
./daemon.sh stop
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
./daemon.sh start
```

**Check health:**

```bash
curl http://127.0.0.1:8000/health
```

**View logs:**

```bash
tail -f backend.log
tail -f frontend.log
```

## Tech Stack

- **Backend:** FastAPI (port 8000)
- **Frontend:** Streamlit (port 8501)
- **LLM:** Google Gemini 2.5 Flash
- **MCP:** Docker MCP Gateway

## Security

Never commit your `.env` file. Get API key: <https://aistudio.google.com/app/apikey>

See `SECURITY.md` for details.

## License

MIT
