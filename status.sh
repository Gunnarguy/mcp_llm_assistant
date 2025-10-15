#!/bin/bash

# Complete MCP LLM Assistant - All-in-One Status & Info

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         MCP LLM ASSISTANT - SYSTEM STATUS                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Not in mcp_llm_assistant directory"
    echo "Please cd to the correct directory"
    exit 1
fi

echo "📁 Project Location: $(pwd)"
echo ""

# Check Python
echo "─────────────────────────────────────────────────────────────"
echo "🐍 Python Environment"
echo "─────────────────────────────────────────────────────────────"
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✅ Virtual environment is ACTIVE"
        PYTHON_VERSION=$(python --version 2>&1)
        echo "   $PYTHON_VERSION"
    else
        echo "⚠️  Virtual environment is NOT active"
        echo "   Run: source venv/bin/activate"
    fi
else
    echo "❌ Virtual environment not found"
    echo "   Run: ./setup.sh"
fi
echo ""

# Check Docker
echo "─────────────────────────────────────────────────────────────"
echo "🐳 Docker Status"
echo "─────────────────────────────────────────────────────────────"
if docker ps &> /dev/null; then
    echo "✅ Docker daemon is running"

    # Check for MCP container
    if [ -f ".env" ]; then
        CONTAINER_NAME=$(grep "MCP_CONTAINER_NAME" .env | cut -d'"' -f2)
        if [ -n "$CONTAINER_NAME" ]; then
            if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
                STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME")
                echo "✅ Container '$CONTAINER_NAME' is $STATUS"
            else
                echo "⚠️  Container '$CONTAINER_NAME' not found"
                echo "   Available containers:"
                docker ps --format "   - {{.Names}} ({{.Status}})"
            fi
        fi
    fi
else
    echo "❌ Docker is not running"
    echo "   Please start Docker Desktop"
fi
echo ""

# Check API Key
echo "─────────────────────────────────────────────────────────────"
echo "🔑 Configuration"
echo "─────────────────────────────────────────────────────────────"
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "your_gemini_api_key_here" .env; then
        echo "❌ Google API key NOT configured"
        echo "   Edit .env and add your API key"
        echo "   Get key from: https://aistudio.google.com/app/apikey"
    else
        echo "✅ Google API key is configured"
    fi
else
    echo "❌ .env file not found"
    echo "   Run: ./setup.sh"
fi
echo ""

# Check Backend
echo "─────────────────────────────────────────────────────────────"
echo "⚡ Backend (FastAPI)"
echo "─────────────────────────────────────────────────────────────"
if curl -s http://127.0.0.1:8000/health &> /dev/null; then
    echo "✅ Backend is RUNNING (http://127.0.0.1:8000)"

    # Get health status
    HEALTH=$(curl -s http://127.0.0.1:8000/health)
    if echo "$HEALTH" | grep -q '"status":"healthy"'; then
        echo "✅ System is HEALTHY"
    elif echo "$HEALTH" | grep -q '"status":"partial"'; then
        echo "⚠️  System is PARTIALLY healthy"
    else
        echo "❌ System is UNHEALTHY"
    fi

    echo "   API Docs: http://127.0.0.1:8000/docs"
else
    echo "❌ Backend is NOT running"
    echo "   Start with: ./start_backend.sh"
fi
echo ""

# Check Frontend
echo "─────────────────────────────────────────────────────────────"
echo "🎨 Frontend (Streamlit)"
echo "─────────────────────────────────────────────────────────────"
if lsof -Pi :8501 -sTCP:LISTEN -t &> /dev/null; then
    echo "✅ Frontend is RUNNING (http://localhost:8501)"
else
    echo "❌ Frontend is NOT running"
    echo "   Start with: ./start_frontend.sh"
fi
echo ""

# Documentation
echo "─────────────────────────────────────────────────────────────"
echo "📚 Documentation"
echo "─────────────────────────────────────────────────────────────"
echo "   QUICKSTART.md  - 5-minute setup guide"
echo "   README.md      - Complete documentation"
echo "   OVERVIEW.md    - System architecture"
echo "   PROJECT_SUMMARY.md - Technical summary"
echo ""

# Quick Actions
echo "─────────────────────────────────────────────────────────────"
echo "🚀 Quick Actions"
echo "─────────────────────────────────────────────────────────────"
echo "   ./setup.sh          - Initial setup"
echo "   ./start_backend.sh  - Start FastAPI backend"
echo "   ./start_frontend.sh - Start Streamlit UI"
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    SYSTEM SUMMARY                          ║"
echo "╚════════════════════════════════════════════════════════════╝"

ALL_GOOD=true

if [ ! -d "venv" ]; then
    echo "❌ Need to run: ./setup.sh"
    ALL_GOOD=false
fi

if ! docker ps &> /dev/null; then
    echo "❌ Need to start Docker Desktop"
    ALL_GOOD=false
fi

if [ -f ".env" ] && grep -q "your_gemini_api_key_here" .env; then
    echo "❌ Need to configure API key in .env"
    ALL_GOOD=false
fi

if ! curl -s http://127.0.0.1:8000/health &> /dev/null; then
    echo "⚠️  Backend not running (./start_backend.sh)"
    ALL_GOOD=false
fi

if ! lsof -Pi :8501 -sTCP:LISTEN -t &> /dev/null; then
    echo "⚠️  Frontend not running (./start_frontend.sh)"
    ALL_GOOD=false
fi

if [ "$ALL_GOOD" = true ]; then
    echo ""
    echo "✅ Everything is READY! 🎉"
    echo ""
    echo "Open your browser to: http://localhost:8501"
    echo ""
else
    echo ""
    echo "⚠️  Some components need attention (see above)"
    echo ""
fi

echo "════════════════════════════════════════════════════════════"
