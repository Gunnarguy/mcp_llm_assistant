#!/bin/bash

# Start FastAPI Backend

echo "🚀 Starting FastAPI Backend..."
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists and has API key
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

if grep -q "your_gemini_api_key_here" .env; then
    echo "⚠️  WARNING: Google API key not configured!"
    echo "Please edit .env and add your API key"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the backend
echo "Starting uvicorn server..."
echo "Backend will be available at: http://127.0.0.1:8000"
echo "API docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
