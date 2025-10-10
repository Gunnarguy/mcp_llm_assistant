#!/bin/bash

# Simple startup script for MCP LLM Assistant
# Just run: ./start.sh

set -e

echo ""
echo "🚀 Starting MCP LLM Assistant"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first!"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Run ./setup.sh first!"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "📡 Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check backend.log for errors."
    exit 1
fi

# Start frontend
echo ""
echo "🎨 Starting frontend..."
echo ""
streamlit run frontend/chat_ui.py --server.port 8501

# When Streamlit stops (user presses Ctrl+C), clean up
echo ""
echo "🛑 Shutting down..."
