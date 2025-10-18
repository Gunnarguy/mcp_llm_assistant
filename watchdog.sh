#!/usr/bin/env zsh

# Watchdog - monitors services and auto-restarts on failure
# Usage: ./watchdog.sh (runs in foreground, Ctrl+C to stop)

SCRIPT_DIR="${0:A:h}"
BACKEND_PID_FILE="$SCRIPT_DIR/runtime/backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/runtime/frontend.pid"
WATCHDOG_LOG="$SCRIPT_DIR/logs/watchdog.log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$WATCHDOG_LOG"
}

check_backend() {
    # Check 1: Process alive
    if [ -f "$BACKEND_PID_FILE" ]; then
        PID=$(cat "$BACKEND_PID_FILE")
        if ! ps -p $PID > /dev/null 2>&1; then
            return 1
        fi
    else
        return 1
    fi

    # Check 2: Health endpoint responding
    if ! curl -s -f http://127.0.0.1:8000/health > /dev/null 2>&1; then
        return 1
    fi

    return 0
}

check_frontend() {
    if [ -f "$FRONTEND_PID_FILE" ]; then
        PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

restart_backend() {
    log "${RED}Backend failure detected - restarting...${NC}"
    "$SCRIPT_DIR/daemon.sh" stop backend 2>/dev/null || true
    sleep 2
    "$SCRIPT_DIR/daemon.sh" start backend

    if check_backend; then
        log "${GREEN}Backend recovered successfully${NC}"
        return 0
    else
        log "${RED}Backend restart failed${NC}"
        return 1
    fi
}

restart_frontend() {
    log "${YELLOW}Frontend failure detected - restarting...${NC}"
    "$SCRIPT_DIR/daemon.sh" stop frontend 2>/dev/null || true
    sleep 1
    "$SCRIPT_DIR/daemon.sh" start frontend

    if check_frontend; then
        log "${GREEN}Frontend recovered successfully${NC}"
        return 0
    else
        log "${RED}Frontend restart failed${NC}"
        return 1
    fi
}

# Trap Ctrl+C
trap 'echo "\n${BLUE}Watchdog stopped${NC}"; exit 0' INT

log "${BLUE}Watchdog started - monitoring services every 30 seconds${NC}"
log "${BLUE}Press Ctrl+C to stop${NC}"

BACKEND_FAILURES=0
FRONTEND_FAILURES=0
MAX_FAILURES=3

while true; do
    # Check backend
    if check_backend; then
        echo -n "${GREEN}.${NC}"
        BACKEND_FAILURES=0
    else
        echo -n "${RED}!${NC}"
        BACKEND_FAILURES=$((BACKEND_FAILURES + 1))

        if [ $BACKEND_FAILURES -ge $MAX_FAILURES ]; then
            log "${RED}Backend failed $BACKEND_FAILURES times - giving up${NC}"
            log "${RED}Manual intervention required${NC}"
            exit 1
        else
            restart_backend
        fi
    fi

    # Check frontend
    if check_frontend; then
        echo -n "${GREEN}.${NC}"
        FRONTEND_FAILURES=0
    else
        echo -n "${YELLOW}!${NC}"
        FRONTEND_FAILURES=$((FRONTEND_FAILURES + 1))

        if [ $FRONTEND_FAILURES -le $MAX_FAILURES ]; then
            restart_frontend
        fi
    fi

    sleep 30
done
