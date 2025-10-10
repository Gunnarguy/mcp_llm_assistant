#!/bin/bash

# Start Streamlit Frontend

echo "🎨 Starting Streamlit Frontend..."
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://127.0.0.1:8000/health &> /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️  WARNING: Backend doesn't seem to be running"
    echo "Please start the backend first: ./start_backend.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the frontend
echo ""
echo "Starting Streamlit..."
echo "Frontend will open in your browser automatically"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run frontend/chat_ui.py
