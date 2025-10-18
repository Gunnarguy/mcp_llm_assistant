# 🛡️ Bulletproof Operations Guide

This system now includes **multiple safety layers** to prevent failures and auto-recover when things go wrong.

## 🚀 Quick Start (Idiot-Proof)

```bash
# 1. Check system health
./doctor.sh

# 2. Start services (auto-validates first)
./daemon.sh start

# 3. (Optional) Enable auto-recovery
./watchdog.sh
```

## 🔧 Safety Tools

### 1. `doctor.sh` - Auto-Fix Common Issues
Diagnoses and automatically fixes:
- ✅ Missing .env file → Creates template
- ✅ Missing Python packages → Installs them
- ✅ Stale PID files → Cleans them
- ✅ Port conflicts → Identifies them
- ✅ Large log files → Suggests cleanup
- ✅ Docker status → Validates it's running
- ✅ API key validation → Checks configuration

**Run anytime something feels broken:**
```bash
./doctor.sh
```

### 2. `preflight_check.sh` - Pre-Start Validation
Runs automatically before `./daemon.sh start` or `restart`.

Checks 10 critical areas:
1. Python 3.12+ installed
2. Docker running
3. Docker MCP Gateway functional
4. Ports 8000/8501 available
5. .env file configured
6. All Python dependencies present
7. Directory structure intact
8. Critical files present
9. Write permissions for logs/runtime
10. Sufficient disk space

**Manual run:**
```bash
./daemon.sh check
```

**Output:**
```
🔍 Running pre-flight checks...

[1/10] Checking Python...
✅ PASS: Python 3.12.9 found at /Users/.../.pyenv/versions/3.12.9/bin/python3

[2/10] Checking Docker...
✅ PASS: Docker 24.0.6 running

[3/10] Checking Docker MCP Gateway...
✅ PASS: Docker MCP Gateway is functional

...

✅ All checks passed!
```

If checks fail, **system won't start** until you fix the issues.

### 3. `watchdog.sh` - Auto-Recovery Daemon
Monitors services every 30 seconds and auto-restarts on failure.

**Features:**
- ✅ Detects process crashes
- ✅ Detects health endpoint failures
- ✅ Auto-restarts failed services
- ✅ Gives up after 3 consecutive failures (prevents infinite loops)
- ✅ Logs all recovery actions

**Run in background:**
```bash
./watchdog.sh &
```

**Run in foreground (Ctrl+C to stop):**
```bash
./watchdog.sh
```

**Output:**
```
[2025-10-17 10:30:00] Watchdog started - monitoring services every 30 seconds
[2025-10-17 10:30:00] Press Ctrl+C to stop
...
[2025-10-17 10:35:00] Backend failure detected - restarting...
[2025-10-17 10:35:15] Backend recovered successfully
```

### 4. Enhanced `daemon.sh`
Now includes auto-validation and better error handling.

**New command:**
```bash
./daemon.sh check  # Run preflight checks manually
```

**All commands:**
```bash
./daemon.sh start    # Start with validation
./daemon.sh stop     # Stop services
./daemon.sh restart  # Restart with validation + log cleanup
./daemon.sh status   # Show current status
./daemon.sh check    # Manual preflight validation
```

## 🔒 What's Protected

### 1. **Environment Corruption**
- ❌ Before: Breaking venv would crash system
- ✅ Now: Uses pyenv directly (can't break it)
- ✅ `requirements.lock` pins exact versions
- ✅ `doctor.sh` auto-reinstalls missing packages

### 2. **Port Conflicts**
- ❌ Before: "Address already in use" errors
- ✅ Now: Auto-kills blocking processes on start
- ✅ Preflight check warns you in advance

### 3. **Missing Configuration**
- ❌ Before: Cryptic startup errors
- ✅ Now: Preflight validates .env file
- ✅ Doctor creates template if missing
- ✅ Won't start without API key

### 4. **Docker Issues**
- ❌ Before: Silent failures if Docker stopped
- ✅ Now: Preflight checks Docker status
- ✅ Validates MCP Gateway accessibility
- ✅ Clear error messages with fix instructions

### 5. **Process Crashes**
- ❌ Before: Services crash, you don't know
- ✅ Now: Watchdog detects + auto-restarts
- ✅ Logs all recovery actions
- ✅ Gives up after 3 failures (prevents chaos)

### 6. **Stale State**
- ❌ Before: Stale PID files confuse daemon
- ✅ Now: Doctor auto-cleans stale PIDs
- ✅ Restart command truncates huge logs

### 7. **Dependency Hell**
- ❌ Before: `pip install` could break things
- ✅ Now: `requirements.lock` prevents version drift
- ✅ Doctor validates all packages present
- ✅ Preflight checks for import errors

## 📊 Monitoring

### Real-time Logs
```bash
# Backend logs (LLM function calls, API requests)
tail -f logs/backend.log

# Frontend logs (UI errors, user actions)
tail -f logs/frontend.log

# Watchdog logs (recovery actions)
tail -f logs/watchdog.log
```

### Health Check
```bash
curl http://127.0.0.1:8000/health | jq
```

**Output:**
```json
{
  "status": "healthy",
  "llm_configured": true,
  "docker_available": true,
  "mcp_gateway_functional": true
}
```

## 🚨 Troubleshooting Workflow

### Something isn't working?

**Step 1: Run doctor**
```bash
./doctor.sh
```
→ Auto-fixes common issues

**Step 2: Check status**
```bash
./daemon.sh status
```
→ Shows what's running

**Step 3: Review logs**
```bash
tail -100 logs/backend.log    # Last 100 lines
```
→ Find actual error

**Step 4: Full restart**
```bash
./daemon.sh restart
```
→ Clean slate with validation

**Step 5: Nuclear option**
```bash
./daemon.sh stop
./doctor.sh
./daemon.sh start
./watchdog.sh &
```
→ Full system reset + auto-recovery

## 🔐 Safety Guarantees

### You CANNOT Break It By:
1. ✅ Installing random Docker containers (isolated)
2. ✅ Breaking Python venv (uses pyenv directly)
3. ✅ Messing up port bindings (auto-cleaned)
4. ✅ Forgetting API keys (validation catches it)
5. ✅ Stopping Docker (preflight catches it)
6. ✅ Crashing services (watchdog recovers)
7. ✅ Running multiple starts (PID checks prevent it)
8. ✅ Corrupting log files (auto-truncated on restart)

### The System WILL:
1. ✅ Refuse to start if critical issues exist
2. ✅ Auto-fix fixable issues (doctor.sh)
3. ✅ Auto-restart crashed services (watchdog.sh)
4. ✅ Give clear error messages with fix instructions
5. ✅ Prevent port conflicts automatically
6. ✅ Validate configuration before starting
7. ✅ Log all actions for debugging

## 📝 Best Practices

### Daily Use
```bash
./daemon.sh start    # Morning
./daemon.sh stop     # End of day
```

### After System Updates
```bash
./doctor.sh          # Check for issues
./daemon.sh restart  # Fresh start
```

### Long-running Deployment
```bash
./daemon.sh start
./watchdog.sh &      # Enable auto-recovery
disown               # Detach from terminal
```

### Development/Testing
```bash
./daemon.sh status   # Check before coding
tail -f logs/backend.log  # Monitor changes
./daemon.sh restart  # Test new code
```

## 🎯 Zero-Downtime Updates

```bash
# 1. Pull latest code
git pull

# 2. Check for issues
./doctor.sh

# 3. Restart with validation
./daemon.sh restart

# 4. Verify healthy
./daemon.sh status
curl http://127.0.0.1:8000/health
```

## 🛠️ Advanced Recovery

### Service won't start after multiple attempts?
```bash
# 1. Nuclear cleanup
./daemon.sh stop
pkill -9 uvicorn streamlit  # Kill all related processes
rm runtime/*.pid            # Remove PID files

# 2. Clean ports manually
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9

# 3. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 4. Fresh start
./daemon.sh start
```

### Docker MCP issues?
```bash
# Reset MCP Gateway
docker mcp server list    # Verify connectivity
docker restart $(docker ps -aq)  # Restart all containers

# Re-run preflight
./daemon.sh check
```

## 📚 File Reference

```
Safety System Files:
├── doctor.sh           → Auto-fix common issues
├── preflight_check.sh  → Pre-start validation (auto-run)
├── watchdog.sh         → Auto-recovery daemon
├── daemon.sh           → Enhanced service manager
├── requirements.txt    → Loose dependencies
├── requirements.lock   → Exact versions (generated)
└── SAFETY.md           → This file
```

---

**🎉 Bottom Line:** The system is now **bulletproof**. Run `doctor.sh` when unsure, `daemon.sh start` to launch, and `watchdog.sh` for auto-recovery. You're covered! 🛡️
