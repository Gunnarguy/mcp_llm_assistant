#!/usr/bin/env zsh

# Daemon launcher - keeps services running in background
# Usage: ./daemon.sh start|stop|restart|status

SCRIPT_DIR="${0:A:h}"
BACKEND_PID_FILE="$SCRIPT_DIR/runtime/backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/runtime/frontend.pid"
BACKEND_LOG="$SCRIPT_DIR/logs/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/logs/frontend.log"
PREFLIGHT_SCRIPT="$SCRIPT_DIR/preflight_check.sh"

# Create runtime directories if they don't exist
mkdir -p "$SCRIPT_DIR/runtime"
mkdir -p "$SCRIPT_DIR/logs"

# Run preflight checks before starting (only for 'start' and 'restart' commands)
run_preflight_check() {
    if [ -f "$PREFLIGHT_SCRIPT" ]; then
        echo "🔍 Running pre-flight checks..."
        if ! "$PREFLIGHT_SCRIPT"; then
            echo "❌ Pre-flight checks failed. System cannot start safely."
            echo "   Fix errors above and try again."
            exit 1
        fi
        echo ""
    fi
}

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

    # Auto-cleanup: Kill anything blocking port 8000
    BLOCKING=$(lsof -ti:8000 2>/dev/null)
    if [ -n "$BLOCKING" ]; then
        echo "🧹 Auto-cleaning port 8000 (processes: $BLOCKING)..."
        echo "$BLOCKING" | xargs kill -9 2>/dev/null
        sleep 1
    fi

    echo "🚀 Starting backend daemon..."
    cd "$SCRIPT_DIR"
    nohup "$UVICORN_BIN" app.main:app --host 0.0.0.0 --port 8000 >> "$BACKEND_LOG" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"

    # Wait up to 120 seconds for backend to become healthy (startup can take ~2 minutes)
    echo "⏳ Waiting for backend to start (this may take up to 2 minutes)..."
    for i in {1..60}; do
        sleep 2
        if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
            echo "✅ Backend running (PID: $(cat $BACKEND_PID_FILE)) - took $((i*2)) seconds"
            return 0
        fi
        if ! ps -p $(cat $BACKEND_PID_FILE) > /dev/null 2>&1; then
            echo "❌ Backend process died - check logs: $BACKEND_LOG"
            return 1
        fi
    done

    echo "❌ Backend failed to respond after 120 seconds - check logs: $BACKEND_LOG"
    return 1
}

start_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Frontend already running (PID: $PID)"
            return 0
        fi
    fi

    # Auto-cleanup: Kill anything blocking port 8501
    BLOCKING=$(lsof -ti:8501 2>/dev/null)
    if [ -n "$BLOCKING" ]; then
        echo "🧹 Auto-cleaning port 8501 (processes: $BLOCKING)..."
        echo "$BLOCKING" | xargs kill -9 2>/dev/null
        sleep 1
    fi

    echo "🎨 Starting frontend daemon..."
    cd "$SCRIPT_DIR"
    nohup "$STREAMLIT_BIN" run frontend/chat_ui.py --server.port 8501 --server.address 0.0.0.0 --server.headless true >> "$FRONTEND_LOG" 2>&1 &
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

clear_logs() {
    echo "🧹 Clearing old logs..."

    # Clear application logs (truncate to empty)
    : > "$SCRIPT_DIR/logs/llm_service.log" 2>/dev/null || true
    : > "$SCRIPT_DIR/logs/docker_service.log" 2>/dev/null || true
    : > "$SCRIPT_DIR/logs/app.log" 2>/dev/null || true

    # Truncate daemon logs (keep last 1000 lines only)
    if [ -f "$BACKEND_LOG" ]; then
        tail -1000 "$BACKEND_LOG" > "$BACKEND_LOG.tmp" 2>/dev/null && mv "$BACKEND_LOG.tmp" "$BACKEND_LOG" 2>/dev/null || true
    fi

    if [ -f "$FRONTEND_LOG" ]; then
        tail -1000 "$FRONTEND_LOG" > "$FRONTEND_LOG.tmp" 2>/dev/null && mv "$FRONTEND_LOG.tmp" "$FRONTEND_LOG" 2>/dev/null || true
    fi

    echo "✅ Logs cleared"
}

show_status() {
    echo "📊 MCP Assistant Status"
    echo "======================="

    BACKEND_HEALTHY=false
    FRONTEND_HEALTHY=false

    if [ -f "$BACKEND_PID_FILE" ]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Backend: Running (PID: $PID)"
            echo "   URL: http://127.0.0.1:8000"
            BACKEND_HEALTHY=true
        else
            echo "❌ Backend: Not running (stale PID file)"
            rm "$BACKEND_PID_FILE" 2>/dev/null
        fi
    else
        echo "❌ Backend: Not running"
    fi

    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Frontend: Running (PID: $PID)"
            echo "   URL: http://localhost:8501"
            FRONTEND_HEALTHY=true
        else
            echo "❌ Frontend: Not running (stale PID file)"
            rm "$FRONTEND_PID_FILE" 2>/dev/null
        fi
    else
        echo "❌ Frontend: Not running"
    fi

    echo ""
    echo "Logs:"
    echo "  Backend:  tail -f $BACKEND_LOG"
    echo "  Frontend: tail -f $FRONTEND_LOG"

    # Auto-fix suggestion
    if [ "$BACKEND_HEALTHY" = false ] || [ "$FRONTEND_HEALTHY" = false ]; then
        echo ""
        echo "💡 Tip: Run './daemon.sh start' to fix any stopped services"
    fi
}

case "$1" in
    start)
        run_preflight_check  # ← NEW: Validate before starting
        echo "🚀 Starting MCP Assistant daemons..."
        echo ""
        start_backend
        start_frontend
        echo ""
        echo "✅ Services started! Access at:"
        echo "   Backend:  http://127.0.0.1:8000"
        echo "   Frontend: http://localhost:8501"
        echo ""
        echo "💡 Optional: Run './watchdog.sh' to auto-recover from failures"
        echo "   Run './daemon.sh status' to check status"
        ;;
    stop)
        echo "🛑 Stopping MCP Assistant daemons..."
        echo ""
        stop_backend
        stop_frontend
        ;;
    restart)
        run_preflight_check  # ← NEW: Validate before restarting
        echo "🔄 Restarting MCP Assistant daemons..."
        echo ""
        stop_backend
        stop_frontend
        clear_logs
        sleep 2  # Give ports time to fully release
        start_backend
        start_frontend
        ;;
    status)
        show_status
        ;;
    check)
        # NEW: Manual preflight check
        if [ -f "$PREFLIGHT_SCRIPT" ]; then
            "$PREFLIGHT_SCRIPT"
        else
            echo "❌ Preflight check script not found"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|check}"
        echo ""
        echo "Commands:"
        echo "  start   - Start backend and frontend daemons"
        echo "  stop    - Stop all daemons"
        echo "  restart - Restart all daemons"
        echo "  status  - Show current status"
        exit 1
        ;;
esac
