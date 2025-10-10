#!/bin/bash

# Simple shutdown script for MCP LLM Assistant
# Just run: ./stop.sh

echo ""
echo "🛑 Stopping MCP LLM Assistant"
echo "========================================"
echo ""

# Kill backend if PID file exists
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔴 Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm backend.pid
        echo "✅ Backend stopped"
    else
        echo "⚠️  Backend already stopped"
        rm backend.pid
    fi
else
    echo "⚠️  No backend PID file found"
fi

# Kill any remaining streamlit processes
STREAMLIT_PIDS=$(pgrep -f "streamlit run chat_ui.py" || true)
if [ -n "$STREAMLIT_PIDS" ]; then
    echo "🔴 Stopping frontend..."
    echo "$STREAMLIT_PIDS" | xargs kill 2>/dev/null || true
    echo "✅ Frontend stopped"
else
    echo "⚠️  Frontend already stopped"
fi

# Kill any remaining uvicorn processes for this project
UVICORN_PIDS=$(pgrep -f "uvicorn app.main:app" || true)
if [ -n "$UVICORN_PIDS" ]; then
    echo "🔴 Stopping any remaining backend processes..."
    echo "$UVICORN_PIDS" | xargs kill 2>/dev/null || true
    echo "✅ Cleanup complete"
fi

echo ""
echo "✅ All services stopped"
echo ""
