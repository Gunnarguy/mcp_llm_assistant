#!/bin/bash

# Run tests with coverage

echo "🧪 Running MCP LLM Assistant Tests"
echo "===================================="
echo ""

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not active"
    echo "Activating venv..."
    source venv/bin/activate
fi

# Run pytest with coverage
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed"
    exit 1
fi
