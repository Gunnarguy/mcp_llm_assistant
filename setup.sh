#!/bin/bash

# MCP LLM Assistant - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "🚀 MCP LLM Assistant - Setup Script"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "Please run this script from the mcp_llm_assistant directory"
    exit 1
fi

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

# Check if Docker is running
echo "📋 Checking Docker..."
if docker ps &> /dev/null; then
    echo "   ✅ Docker is running"
else
    echo "   ❌ Docker is not running or not accessible"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "   ✅ Dependencies installed"

# Create .env file from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "   ✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: You need to add your Google Gemini API key to .env"
    echo "   1. Get your free API key from: https://aistudio.google.com/app/apikey"
    echo "   2. Edit .env and replace 'your_gemini_api_key_here' with your actual key"
    echo "   3. Update MCP_CONTAINER_NAME if needed (check with: docker ps)"
else
    echo "   ✅ .env file already exists"
fi

# Check if API key is configured
if grep -q "your_gemini_api_key_here" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: Google API key not configured yet!"
    echo "   Please edit .env and add your API key before starting the application"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file to add your Google Gemini API key"
echo "2. Make sure your Docker container is running: docker ps"
echo "3. Start the backend: ./start_backend.sh"
echo "4. In a new terminal, start the frontend: ./start_frontend.sh"
echo ""
echo "Or use the combined launcher: ./start_all.sh"
echo ""
