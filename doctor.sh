#!/usr/bin/env zsh

# Doctor script - diagnoses and fixes common issues
# Usage: ./doctor.sh

SCRIPT_DIR="${0:A:h}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "${BLUE}═══════════════════════════════════════════════${NC}"
echo "${BLUE}    MCP Assistant Doctor - System Diagnostics${NC}"
echo "${BLUE}═══════════════════════════════════════════════${NC}\n"

ISSUES_FOUND=0
FIXES_APPLIED=0

# Issue 1: Missing .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "${RED}❌ Issue: .env file missing${NC}"
    echo "${YELLOW}   Fix: Creating .env template...${NC}"

    cat > "$SCRIPT_DIR/.env" << 'EOF'
# Google Gemini API Key (REQUIRED)
# Get your key: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your_api_key_here

# Notion Integration Token (OPTIONAL - for Notion features)
# Create integration: https://www.notion.so/my-integrations
NOTION_TOKEN=

# Model Configuration (OPTIONAL)
GEMINI_MODEL_PRIMARY=gemini-2.5-flash
GEMINI_MODEL_FALLBACKS=gemini-2.5-flash-lite,gemini-2.0-flash,gemini-1.5-flash
EOF

    echo "${GREEN}   ✅ Created .env template${NC}"
    echo "${YELLOW}   ⚠️  ACTION REQUIRED: Edit .env and add your GOOGLE_API_KEY${NC}\n"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    FIXES_APPLIED=$((FIXES_APPLIED + 1))
else
    echo "${GREEN}✅ .env file exists${NC}\n"
fi

# Issue 2: Missing Python dependencies
echo "${BLUE}Checking Python dependencies...${NC}"
MISSING_PKGS=()

for pkg in "fastapi" "uvicorn" "streamlit" "requests" "google-generativeai" "docker" "python-dotenv" "pydantic"; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        MISSING_PKGS+=("$pkg")
    fi
done

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo "${RED}❌ Issue: Missing Python packages: ${MISSING_PKGS[*]}${NC}"
    echo "${YELLOW}   Fix: Installing missing packages...${NC}"

    if pip install -r "$SCRIPT_DIR/requirements.txt" 2>&1 | grep -q "Successfully installed"; then
        echo "${GREEN}   ✅ Packages installed${NC}\n"
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
    else
        echo "${RED}   ❌ Installation failed - run manually: pip install -r requirements.txt${NC}\n"
    fi
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo "${GREEN}✅ All Python packages installed${NC}\n"
fi

# Issue 3: Stale PID files
if [ -f "$SCRIPT_DIR/runtime/backend.pid" ]; then
    PID=$(cat "$SCRIPT_DIR/runtime/backend.pid")
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "${RED}❌ Issue: Stale backend PID file${NC}"
        echo "${YELLOW}   Fix: Removing stale PID...${NC}"
        rm "$SCRIPT_DIR/runtime/backend.pid"
        echo "${GREEN}   ✅ Cleaned${NC}\n"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
    fi
fi

if [ -f "$SCRIPT_DIR/runtime/frontend.pid" ]; then
    PID=$(cat "$SCRIPT_DIR/runtime/frontend.pid")
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "${RED}❌ Issue: Stale frontend PID file${NC}"
        echo "${YELLOW}   Fix: Removing stale PID...${NC}"
        rm "$SCRIPT_DIR/runtime/frontend.pid"
        echo "${GREEN}   ✅ Cleaned${NC}\n"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
    fi
fi

# Issue 4: Port conflicts
PORT_8000=$(lsof -ti:8000 2>/dev/null)
if [ -n "$PORT_8000" ]; then
    echo "${YELLOW}⚠️  Warning: Port 8000 in use by PID: $PORT_8000${NC}"
    echo "${YELLOW}   This will be auto-cleaned on ./daemon.sh start${NC}\n"
fi

PORT_8501=$(lsof -ti:8501 2>/dev/null)
if [ -n "$PORT_8501" ]; then
    echo "${YELLOW}⚠️  Warning: Port 8501 in use by PID: $PORT_8501${NC}"
    echo "${YELLOW}   This will be auto-cleaned on ./daemon.sh start${NC}\n"
fi

# Issue 5: Large log files
BACKEND_LOG_SIZE=$(du -m "$SCRIPT_DIR/logs/backend.log" 2>/dev/null | cut -f1)
FRONTEND_LOG_SIZE=$(du -m "$SCRIPT_DIR/logs/frontend.log" 2>/dev/null | cut -f1)

if [ "$BACKEND_LOG_SIZE" -gt 10 ] || [ "$FRONTEND_LOG_SIZE" -gt 10 ]; then
    echo "${YELLOW}⚠️  Warning: Large log files detected${NC}"
    echo "${YELLOW}   Backend: ${BACKEND_LOG_SIZE}MB, Frontend: ${FRONTEND_LOG_SIZE}MB${NC}"
    echo "${YELLOW}   Tip: Run './daemon.sh restart' to auto-truncate logs${NC}\n"
fi

# Issue 6: Docker not running
if ! docker info >/dev/null 2>&1; then
    echo "${RED}❌ Issue: Docker is not running${NC}"
    echo "${YELLOW}   Fix: Start Docker Desktop and retry${NC}\n"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Issue 7: Google API key validation # pragma: allowlist secret
if [ -f "$SCRIPT_DIR/.env" ]; then
    API_KEY=$(grep "GOOGLE_API_KEY=" "$SCRIPT_DIR/.env" | cut -d'=' -f2-) # pragma: allowlist secret
    if [ "$API_KEY" = "your_api_key_here" ] || [ -z "$API_KEY" ]; then # pragma: allowlist secret
        echo "${RED}❌ Issue: GOOGLE_API_KEY not configured${NC}"
        echo "${YELLOW}   Fix: Edit .env and add your API key from:${NC}" # pragma: allowlist secret
        echo "${YELLOW}        https://aistudio.google.com/app/apikey${NC}\n" # pragma: allowlist secret
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
fi

# Summary
echo "${BLUE}═══════════════════════════════════════════════${NC}"
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "${GREEN}✅ System is healthy! No issues found.${NC}"
    echo "${GREEN}   Ready to start: ./daemon.sh start${NC}"
elif [ $FIXES_APPLIED -gt 0 ]; then
    echo "${YELLOW}⚠️  Found $ISSUES_FOUND issues, fixed $FIXES_APPLIED automatically${NC}"
    echo "${YELLOW}   Review warnings above and retry${NC}"
else
    echo "${RED}❌ Found $ISSUES_FOUND issues requiring manual fixes${NC}"
    echo "${RED}   Fix errors above and run './doctor.sh' again${NC}"
fi
echo "${BLUE}═══════════════════════════════════════════════${NC}"
