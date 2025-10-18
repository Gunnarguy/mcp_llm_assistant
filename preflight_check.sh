#!/usr/bin/env zsh

# Pre-flight check script - validates environment before starting services
# Run automatically by daemon.sh or manually: ./preflight_check.sh

set -e

SCRIPT_DIR="${0:A:h}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "${BLUE}🔍 Running pre-flight checks...${NC}\n"

# Track failures
FAILURES=0
WARNINGS=0

# Helper functions
fail() {
    echo "${RED}❌ FAIL: $1${NC}"
    FAILURES=$((FAILURES + 1))
}

warn() {
    echo "${YELLOW}⚠️  WARN: $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

pass() {
    echo "${GREEN}✅ PASS: $1${NC}"
}

# 1. Check Python installation
echo "${BLUE}[1/10] Checking Python...${NC}"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_PATH=$(which python3)

    # Check version >= 3.12
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [[ $MAJOR -ge 3 && $MINOR -ge 12 ]]; then
        pass "Python $PYTHON_VERSION found at $PYTHON_PATH"
    else
        fail "Python 3.12+ required, found $PYTHON_VERSION"
    fi
else
    fail "Python 3 not found in PATH"
fi

# 2. Check Docker
echo "\n${BLUE}[2/10] Checking Docker...${NC}"
if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
        pass "Docker $DOCKER_VERSION running"
    else
        fail "Docker installed but not running (start Docker Desktop)"
    fi
else
    fail "Docker not installed"
fi

# 3. Check Docker MCP Gateway
echo "\n${BLUE}[3/10] Checking Docker MCP Gateway...${NC}"
if docker mcp server list >/dev/null 2>&1; then
    pass "Docker MCP Gateway is functional"
else
    warn "Docker MCP Gateway not responding (may need 'docker mcp' installed)"
fi

# 4. Check required ports
echo "\n${BLUE}[4/10] Checking ports...${NC}"
PORT_8000=$(lsof -ti:8000 2>/dev/null)
PORT_8501=$(lsof -ti:8501 2>/dev/null)

if [ -z "$PORT_8000" ]; then
    pass "Port 8000 (backend) available"
else
    warn "Port 8000 in use by PID: $PORT_8000 (will auto-clean on start)"
fi

if [ -z "$PORT_8501" ]; then
    pass "Port 8501 (frontend) available"
else
    warn "Port 8501 in use by PID: $PORT_8501 (will auto-clean on start)"
fi

# 5. Check .env file
echo "\n${BLUE}[5/10] Checking environment configuration...${NC}"
if [ -f "$SCRIPT_DIR/.env" ]; then
    pass ".env file exists"

    # Check for Google API key
    if grep -q "GOOGLE_API_KEY=.*[A-Za-z0-9]" "$SCRIPT_DIR/.env"; then
        pass "GOOGLE_API_KEY configured"
    else
        fail "GOOGLE_API_KEY missing or empty in .env"
    fi

    # Check for Notion token
    if grep -q "NOTION_TOKEN=.*[A-Za-z0-9]" "$SCRIPT_DIR/.env"; then
        pass "NOTION_TOKEN configured"
    else
        warn "NOTION_TOKEN missing (Notion features disabled)"
    fi
else
    fail ".env file missing (run ./setup.sh)"
fi

# 6. Check Python dependencies
echo "\n${BLUE}[6/10] Checking Python dependencies...${NC}"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    MISSING_DEPS=0

    # Check critical packages
    for pkg in "fastapi" "uvicorn" "streamlit" "requests" "google-generativeai" "docker"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            : # Silent success
        else
            fail "Missing Python package: $pkg"
            MISSING_DEPS=$((MISSING_DEPS + 1))
        fi
    done

    if [ $MISSING_DEPS -eq 0 ]; then
        pass "All critical Python packages installed"
    else
        echo "${RED}   → Run: pip install -r requirements.txt${NC}"
    fi
else
    warn "requirements.txt not found"
fi

# 7. Check directory structure
echo "\n${BLUE}[7/10] Checking directory structure...${NC}"
REQUIRED_DIRS=("app" "app/services" "frontend" "logs" "runtime" "tests")
MISSING_DIRS=0

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$SCRIPT_DIR/$dir" ]; then
        fail "Missing directory: $dir"
        MISSING_DIRS=$((MISSING_DIRS + 1))
    fi
done

if [ $MISSING_DIRS -eq 0 ]; then
    pass "All required directories exist"
fi

# 8. Check critical files
echo "\n${BLUE}[8/10] Checking critical files...${NC}"
REQUIRED_FILES=(
    "app/main.py"
    "app/services/llm_service.py"
    "app/services/docker_service.py"
    "frontend/chat_ui.py"
    "daemon.sh"
)
MISSING_FILES=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        fail "Missing file: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    pass "All critical files present"
fi

# 9. Check log file permissions
echo "\n${BLUE}[9/10] Checking permissions...${NC}"
mkdir -p "$SCRIPT_DIR/logs" "$SCRIPT_DIR/runtime" 2>/dev/null
if [ -w "$SCRIPT_DIR/logs" ] && [ -w "$SCRIPT_DIR/runtime" ]; then
    pass "Write permissions OK for logs and runtime"
else
    fail "No write permissions for logs/runtime directories"
fi

# 10. Check disk space
echo "\n${BLUE}[10/10] Checking disk space...${NC}"
AVAILABLE_GB=$(df -g "$SCRIPT_DIR" | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_GB" -gt 1 ]; then
    pass "Disk space available: ${AVAILABLE_GB}GB"
else
    warn "Low disk space: ${AVAILABLE_GB}GB remaining"
fi

# Summary
echo "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $FAILURES -eq 0 ]; then
    echo "${GREEN}✅ All checks passed!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo "${YELLOW}   ($WARNINGS warnings - system will work with degraded features)${NC}"
    fi
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo "${RED}❌ $FAILURES critical failures detected${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo "${YELLOW}⚠️  $WARNINGS warnings${NC}"
    fi
    echo "\n${RED}System cannot start safely. Fix errors above and retry.${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
