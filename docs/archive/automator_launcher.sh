#!/bin/bash

# Simple launcher for Automator - opens Terminal and runs the main launcher
cd "$(dirname "$0")"

# Open a new Terminal window and run the launcher
osascript -e 'tell application "Terminal"
    activate
    do script "cd '"$(pwd)"' && ./MCP_Assistant_Launcher.sh"
end tell'
