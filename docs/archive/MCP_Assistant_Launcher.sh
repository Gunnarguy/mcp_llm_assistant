#!/bin/bash
#
# MCP LLM Assistant Launcher
# Double-click safe launcher for macOS
#

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   🤖 MCP LLM Assistant Launcher${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Running setup first...${NC}"
    ./setup.sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}Setup failed. Please check the error above.${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${GREEN}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Backend already running on port 8000${NC}"
    echo -e "${YELLOW}   Stopping existing instance...${NC}"
    ./stop.sh 2>/dev/null
    sleep 2
fi

# Start backend in background with proper detachment
echo -e "${GREEN}🚀 Starting FastAPI backend...${NC}"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
disown $BACKEND_PID  # Fully detach from shell
echo $BACKEND_PID > backend.pid
echo -e "${GREEN}   Backend PID: $BACKEND_PID${NC}"

# Wait for backend to be ready
echo -e "${BLUE}⏳ Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check backend.log${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi
done

# Start frontend (this will open browser automatically)
echo -e "${GREEN}🎨 Starting Streamlit frontend...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Application starting!${NC}"
echo -e "${BLUE}   Frontend: ${NC}http://localhost:8501"
echo -e "${BLUE}   API Docs: ${NC}http://localhost:8000/docs"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}💡 TIP: Keep this window open while using the app${NC}"
echo -e "${YELLOW}    Close this window (Cmd+W) to stop the app${NC}"
echo ""

# Start Streamlit (this blocks until user closes it)
streamlit run frontend/chat_ui.py --server.port 8501 --server.headless false

# When Streamlit exits, cleanup
echo ""
echo -e "${YELLOW}🛑 Shutting down...${NC}"
./stop.sh
echo -e "${GREEN}✅ Application stopped successfully${NC}"
echo ""
read -p "Press Enter to close..."
