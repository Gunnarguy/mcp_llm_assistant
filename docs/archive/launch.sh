#!/usr/bin/env zsh

# Simple launcher for MCP LLM Assistant
# Usage: ./launch.sh

# Get the script's directory (works even if called from elsewhere)
SCRIPT_DIR="${0:A:h}"
cd "$SCRIPT_DIR"

echo "🚀 Starting MCP LLM Assistant..."
echo ""

# Kill any existing processes on these ports
echo "🧹 Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
sleep 1

# Start backend
echo "📡 Starting backend..."
nohup "$SCRIPT_DIR/venv/bin/python3" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# Wait for backend to be ready
echo "⏳ Waiting for backend..."
sleep 3

# Check backend health
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend running on http://127.0.0.1:8000"
else
    echo "❌ Backend failed to start. Check backend.log"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
echo ""
echo "========================================"
echo "🌐 Opening chat UI at http://localhost:8501"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Run frontend in foreground (so Ctrl+C stops everything)
"$SCRIPT_DIR/venv/bin/streamlit" run frontend/chat_ui.py --server.port 8501

# Cleanup when frontend stops
echo ""
echo "🛑 Shutting down..."
kill $BACKEND_PID 2>/dev/null
rm -f backend.pid
echo "✅ Services stopped"
