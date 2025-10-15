# GitHub Setup Guide

## 🚨 READ THIS FIRST - Critical Security Steps

This guide helps you safely prepare the MCP LLM Assistant for GitHub without exposing sensitive credentials.

---

## ⚠️ Step 1: Revoke Your Exposed API Key (URGENT)

**Your current `.env` file contains a real Google API key that should NEVER be committed.**

### Revoke the old key:

1. Go to [Google AI Studio API Keys](https://aistudio.google.com/app/apikey)
2. Find your existing key (starts with `AIzaSy...`)
3. Click the **Delete** or **Revoke** button
4. Confirm deletion

### Generate a new key:

1. Click **"Create API Key"**
2. Select **"Create API key in new project"** (or use existing)
3. Copy the new key (starts with `AIzaSy...`)
4. Update your local `.env` file:
   ```bash
   cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant
   nano .env
   # Replace old key with new key
   ```

### Test the new key:

```bash
# Start the application
./start.sh

# Verify it works in the UI
# Ask: "what tools do you have?"
# You should get a response from Gemini
```

**Why this matters**: The old key may have been visible in shell history, terminal output, or other locations. Revoking it ensures no one can use it even if they found it somewhere.

---

## ✅ Step 2: Initialize Git Repository

```bash
cd ~/Documents/GitHub/MCP_Home/mcp_llm_assistant

# Initialize git
git init

# Add all files (except those in .gitignore)
git add .

# Verify .env is NOT staged
git status | grep ".env"
# Should show: .env.template (NOT .env)

# If .env appears, check your .gitignore:
cat .gitignore | grep "^\.env$"
```

---

## ✅ Step 3: Install Security Tools

```bash
# Install pre-commit framework
pip install pre-commit

# Install detect-secrets
pip install detect-secrets

# Install pre-commit hooks
pre-commit install

# Create secrets baseline (marks known false positives)
detect-secrets scan > .secrets.baseline

# Test on all files
pre-commit run --all-files
```

**What this does**:
- `detect-secrets`: Scans for accidentally committed credentials
- `pre-commit`: Runs security checks automatically on every commit
- Baseline file: Prevents false positives on documentation/templates

---

## ✅ Step 4: Verify No Secrets in Staged Files

```bash
# Check what's staged
git status

# Search for sensitive patterns
git diff --cached | grep -iE "AIzaSy|api_key.*=.*[A-Za-z0-9]{20,}|secret.*=.*[A-Za-z0-9]{20,}"  # pragma: allowlist secret

# Expected output: Empty (or only documentation placeholders)
```

**Red flags** (DO NOT COMMIT if you see):
- Real API keys starting with `AIzaSy...`
- Lines like `GOOGLE_API_KEY="AIzaSy...actual key..."`  # pragma: allowlist secret
- Any credentials in code comments

---

## ✅ Step 5: Create First Commit

```bash
# Make the initial commit
git commit -m "Initial commit: MCP LLM Assistant

- FastAPI backend with Gemini LLM integration
- Streamlit frontend for chat UI
- Docker MCP Gateway integration
- Support for Notion, GitHub, Playwright, Perplexity servers
- Comprehensive security configuration
- Pre-commit hooks with secret detection"

# Verify commit succeeded
git log --oneline
```

---

## ✅ Step 6: Create GitHub Repository

### Option A: Via GitHub Web Interface

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `mcp-llm-assistant` (or your choice)
3. Description: "AI assistant with Docker MCP server integration (Notion, GitHub, Playwright, Perplexity)"
4. **Public** or **Private**: Choose based on your needs
5. **DO NOT** initialize with README (you already have one)
6. Click **"Create repository"**

### Option B: Via GitHub CLI

```bash
# Install gh CLI: brew install gh
gh auth login
gh repo create mcp-llm-assistant --public --source=. --remote=origin --description="AI assistant with Docker MCP server integration"
```

---

## ✅ Step 7: Push to GitHub

```bash
# Add remote (use URL from GitHub)
git remote add origin https://github.com/YOUR_USERNAME/mcp-llm-assistant.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## ✅ Step 8: Enable GitHub Security Features

### 1. Enable Secret Scanning (Free for Public Repos)

1. Go to your repo on GitHub
2. **Settings** → **Security** → **Code security and analysis**
3. Enable **"Secret scanning"**
4. Enable **"Push protection"** (prevents pushes with secrets)

### 2. Enable Dependabot

1. Same page as above
2. Enable **"Dependabot alerts"**
3. Enable **"Dependabot security updates"**

### 3. Add Repository Topics (Optional)

1. Go to your repo homepage
2. Click **⚙️** next to "About"
3. Add topics: `ai`, `llm`, `mcp`, `docker`, `fastapi`, `streamlit`, `gemini`, `notion`, `github-api`

---

## ✅ Step 9: Verify Security on GitHub

### Test 1: Check .env is NOT in Repo

```bash
# Clone in a temp directory
cd /tmp
git clone https://github.com/YOUR_USERNAME/mcp-llm-assistant.git test-clone
cd test-clone

# Verify .env does NOT exist
ls -la .env
# Expected: No such file or directory

# Verify .env.template DOES exist
cat .env.template
# Expected: Placeholder values only
```

### Test 2: Check GitHub Secret Scanning

1. Go to repo **Security** tab
2. Check **"Secret scanning alerts"**
3. Should show: **No alerts** (if any appear, revoke those credentials immediately)

---

## 🎉 Success Checklist

Before considering this complete, verify:

- [x] Old API key revoked at Google AI Studio
- [x] New API key generated and tested locally
- [x] `.env` file gitignored (not in repo)
- [x] `.env.template` has safe placeholders
- [x] Pre-commit hooks installed and passing
- [x] First commit created with no secrets
- [x] Pushed to GitHub successfully
- [x] GitHub secret scanning enabled
- [x] Test clone shows `.env` is missing
- [x] Application works with new API key

---

## 📞 Ongoing Security Practices

### Weekly

- Check **Security** tab for Dependabot alerts
- Review any secret scanning alerts

### Monthly

- Rotate API keys (generate new, update `.env`, revoke old)
- Update dependencies: `pip install -U -r requirements.txt`

### Before Each Commit

```bash
# Pre-commit hooks run automatically, but you can manually check:
pre-commit run --all-files

# Look for secrets in changed files
git diff | grep -iE "api_key|token|secret|password"
```

---

## 🆘 Emergency: I Committed a Secret

If you accidentally push a credential to GitHub:

### 1. Revoke the Credential Immediately

- Google Gemini: [AI Studio](https://aistudio.google.com/app/apikey) → Delete key
- GitHub Token: [Settings → Developer settings → Tokens](https://github.com/settings/tokens) → Revoke
- Notion Token: Notion integrations page → Revoke

### 2. Remove from Git History

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove file from entire history
git filter-repo --path .env --invert-paths --force

# Force push (WARNING: rewrites history)
git push origin main --force
```

### 3. Verify Removal

```bash
# Search entire history for the leaked key
git log --all -p | grep "AIzaSy"

# Should return nothing
```

### 4. Update .env with New Key

```bash
# Generate new key
# Update .env locally
# Test application

# NEVER commit the new key
```

---

## 📚 Additional Resources

- [SECURITY.md](./SECURITY.md) - Full security policy
- [SECURITY_CHECKLIST.md](./SECURITY_CHECKLIST.md) - Detailed pre-push checklist
- [detect-secrets docs](https://github.com/Yelp/detect-secrets)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Google API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)

---

## ❓ FAQ

**Q: Can I use the free tier Google API key?**
A: Yes! Free tier gives 15 requests/minute which is sufficient for development.

**Q: What if I need to share my .env with a team member?**
A: Use a password manager (1Password, Bitwarden) to share secrets securely. NEVER commit or email credentials.

**Q: Should I commit backend.log?**
A: NO. It's already gitignored and may contain sensitive data from API responses.

**Q: What if pre-commit is too slow?**
A: You can skip hooks (NOT RECOMMENDED): `git commit --no-verify`. Better to fix the underlying issue.

**Q: How do I update my API key without restarting?**
A: Currently requires restart. Edit `.env` → run `./stop.sh` → run `./start.sh`

---

**Last Updated**: 2025-01-XX
**Maintainer**: [Your Name/Contact]
