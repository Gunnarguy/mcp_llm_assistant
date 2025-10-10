# 🚀 Quick Start: Push to GitHub Safely

## ⚡ Fast Track (20 minutes)

### 1️⃣ Revoke Old API Key (5 min)
```bash
# Open: https://aistudio.google.com/app/apikey
# Delete: ***REMOVED***
# Generate new key → Update .env → Test with ./start.sh
```

### 2️⃣ Install Security Tools (2 min)
```bash
cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant
pip install pre-commit detect-secrets
pre-commit install
detect-secrets scan > .secrets.baseline
```

### 3️⃣ Initialize Git (1 min)
```bash
git init
git add .
```

### 4️⃣ Verify Safety (1 min)
```bash
# .env should NOT appear
git status | grep ".env"

# Pre-commit hooks should pass
pre-commit run --all-files
```

### 5️⃣ First Commit (1 min)
```bash
git commit -m "Initial commit: MCP LLM Assistant with security hardening"
```

### 6️⃣ Create GitHub Repo (2 min)
```bash
# Web: https://github.com/new
# Name: mcp-llm-assistant
# Don't initialize with README
```

### 7️⃣ Push (1 min)
```bash
git remote add origin https://github.com/YOUR_USERNAME/mcp-llm-assistant.git
git branch -M main
git push -u origin main
```

### 8️⃣ Enable Security (3 min)
```bash
# Repo → Settings → Security → Code security and analysis
# Enable: Secret scanning, Push protection, Dependabot alerts
```

### 9️⃣ Verify (2 min)
```bash
cd /tmp
git clone https://github.com/YOUR_USERNAME/mcp-llm-assistant.git test
cd test && ls -la .env  # Should NOT exist ✅
```

---

## 📚 Full Documentation

- **GITHUB_SETUP.md** - Complete step-by-step guide
- **SECURITY_CHECKLIST.md** - Detailed verification steps
- **SECURITY.md** - Full security policy
- **SECURITY_SUMMARY.md** - What we changed and why

---

## 🆘 Emergency Contacts

**If you see this message after pushing:**

> ⚠️ **GitHub detected a secret in your push**

1. **Don't panic** - Push protection stopped it
2. **Revoke the key** at its source (Google AI Studio, etc.)
3. **Remove from commit**: `git reset HEAD~1`
4. **Update .env** with new key (locally only)
5. **Try again**: `git commit` → `git push`

---

## ✅ Quick Checks

Before pushing, verify:
- [ ] Old API key revoked
- [ ] New API key tested locally
- [ ] Pre-commit hooks installed
- [ ] `git status` shows NO `.env` file
- [ ] `pre-commit run --all-files` passes
- [ ] Test commit succeeds

---

**Ready to push?** Follow steps 1-9 above ⬆️

**Need details?** Read `GITHUB_SETUP.md` 📖

**Have questions?** Check `SECURITY.md` FAQ section ❓
