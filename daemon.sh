#!/usr/bin/env zsh

# Daemon launcher - keeps services running in background
# Usage: ./daemon.sh start|stop|restart|status

SCRIPT_DIR="${0:A:h}"
BACKEND_PID_FILE="$SCRIPT_DIR/runtime/backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/runtime/frontend.pid"
BACKEND_LOG="$SCRIPT_DIR/logs/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/logs/frontend.log"

# Use pyenv Python directly instead of broken venv
PYTHON_BIN="/Users/gunnarhostetler/.pyenv/versions/3.12.9/bin/python"
UVICORN_BIN="/Users/gunnarhostetler/.pyenv/versions/3.12.9/bin/uvicorn"
STREAMLIT_BIN="/Users/gunnarhostetler/.pyenv/versions/3.12.9/bin/streamlit"

start_backend() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Backend already running (PID: $PID)"
            return 0
        fi
    fi

    echo "🚀 Starting backend daemon..."
    cd "$SCRIPT_DIR"
    nohup "$UVICORN_BIN" app.main:app --host 0.0.0.0 --port 8000 >> "$BACKEND_LOG" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    sleep 2

    if curl -s http://127.0.0.1:8000/health > /dev/null; then
        echo "✅ Backend running (PID: $(cat $BACKEND_PID_FILE))"
    else
        echo "❌ Backend failed to start"
        return 1
    fi
}

start_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Frontend already running (PID: $PID)"
            return 0
        fi
    fi

    echo "🎨 Starting frontend daemon..."
    cd "$SCRIPT_DIR"
    nohup "$STREAMLIT_BIN" run frontend/chat_ui.py --server.port 8501 --server.headless true >> "$FRONTEND_LOG" 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
    sleep 2
    echo "✅ Frontend running (PID: $(cat $FRONTEND_PID_FILE))"
}

stop_backend() {
    # Stop by PID file
    if [ -f "$BACKEND_PID_FILE" ]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "🛑 Stopping backend (PID: $PID)..."
            kill $PID
            rm "$BACKEND_PID_FILE"
            echo "✅ Backend stopped"
        else
            echo "⚠️  Backend not running (cleaning stale PID)"
            rm "$BACKEND_PID_FILE"
        fi
    else
        echo "⚠️  No backend PID file found"
    fi

    # Kill any orphaned uvicorn processes on port 8000
    ORPHANS=$(lsof -ti:8000 2>/dev/null)
    if [ -n "$ORPHANS" ]; then
        echo "🧹 Cleaning up orphaned backend processes..."
        echo "$ORPHANS" | xargs kill -9 2>/dev/null
    fi
}

stop_frontend() {
    # Stop by PID file
    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "🛑 Stopping frontend (PID: $PID)..."
            kill $PID
            rm "$FRONTEND_PID_FILE"
            echo "✅ Frontend stopped"
        else
            echo "⚠️  Frontend not running (cleaning stale PID)"
            rm "$FRONTEND_PID_FILE"
        fi
    else
        echo "⚠️  No frontend PID file found"
    fi

    # Kill any orphaned streamlit processes on port 8501
    ORPHANS=$(lsof -ti:8501 2>/dev/null)
    if [ -n "$ORPHANS" ]; then
        echo "🧹 Cleaning up orphaned frontend processes..."
        echo "$ORPHANS" | xargs kill -9 2>/dev/null
    fi
}

show_status() {
    echo "📊 MCP Assistant Status"
    echo "======================="

    if [ -f "$BACKEND_PID_FILE" ]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Backend: Running (PID: $PID)"
            echo "   URL: http://127.0.0.1:8000"
        else
            echo "❌ Backend: Not running (stale PID file)"
        fi
    else
        echo "❌ Backend: Not running"
    fi

    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Frontend: Running (PID: $PID)"
            echo "   URL: http://localhost:8501"
        else
            echo "❌ Frontend: Not running (stale PID file)"
        fi
    else
        echo "❌ Frontend: Not running"
    fi

    echo ""
    echo "Logs:"
    echo "  Backend:  tail -f $BACKEND_LOG"
    echo "  Frontend: tail -f $FRONTEND_LOG"
}

case "$1" in
    start)
        echo "🚀 Starting MCP Assistant daemons..."
        echo ""
        start_backend
        start_frontend
        echo ""
        echo "✅ Services started! Access at:"
        echo "   Backend:  http://127.0.0.1:8000"
        echo "   Frontend: http://localhost:8501"
        echo ""
        echo "Run './daemon.sh status' to check status"
        ;;
    stop)
        echo "🛑 Stopping MCP Assistant daemons..."
        echo ""
        stop_backend
        stop_frontend
        ;;
    restart)
        echo "🔄 Restarting MCP Assistant daemons..."
        echo ""
        stop_backend
        stop_frontend
        sleep 1
        start_backend
        start_frontend
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start backend and frontend daemons"
        echo "  stop    - Stop all daemons"
        echo "  restart - Restart all daemons"
        echo "  status  - Show current status"
        exit 1
        ;;
esac
