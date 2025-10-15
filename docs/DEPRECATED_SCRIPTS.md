# Deprecated Scripts - Consolidated 2025-10-15

The following scripts were deprecated and moved to `docs/archive/`:

## Removed Scripts

### `start.sh` - REPLACED BY `daemon.sh start`
Old foreground startup script. Use `./daemon.sh start` instead.

### `stop.sh` - REPLACED BY `daemon.sh stop`
Old stop script. Use `./daemon.sh stop` instead.

### `launch.sh` - DUPLICATE OF `start.sh`
Another startup script. Use `./daemon.sh start` instead.

### `start_backend.sh`, `start_frontend.sh` - INTERNAL ONLY
Called by daemon.sh - not meant for direct use.

### `help.sh` - REPLACED BY `daemon.sh --help`
Old help documentation. Use `./daemon.sh --help` or `./daemon.sh status` instead.

### `MCP_Assistant_Launcher.sh` - MAC-SPECIFIC LAUNCHER
Automator/Mac app launcher. Only needed if you created a Mac app.

### `automator_launcher.sh` - MAC-SPECIFIC LAUNCHER
Another Mac-specific wrapper. Only needed for Mac app integration.

## Current Script Usage

**All you need:**
```bash
./setup.sh           # First-time setup (install deps, create venv)
./daemon.sh start    # Start services
./daemon.sh status   # Check if running
./daemon.sh stop     # Stop services
./daemon.sh restart  # Restart services
./run_tests.sh       # Run pytest
```

**That's it!** Everything else is deprecated.
