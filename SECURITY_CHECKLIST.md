# Security Checklist for GitHub Push

## 🚨 CRITICAL - Before First Push

### ✅ Step 1: Verify .env is Gitignored

```bash
# Run from mcp_llm_assistant/ directory
git check-ignore .env
# Expected output: .env

# Verify .env is NOT tracked
git ls-files .env
# Expected output: (empty - nothing printed)
```

### ✅ Step 2: Revoke Exposed API Key

**URGENT**: If this repository previously contained a real Google API key, revoke it immediately:

1. Visit: https://aistudio.google.com/app/apikey
2. Find key starting with `AIzaSy...`
3. Click **Delete** or **Revoke**
4. Generate new key
5. Update local `.env` file with new key
6. **Test application** with new key before proceeding

### ✅ Step 3: Check Git History for Secrets

```bash
# Scan entire history for leaked credentials
git log -p | grep -iE "AIzaSy|api_key.*=.*[A-Za-z0-9]{20,}|secret.*=.*[A-Za-z0-9]{20,}|token.*=.*[A-Za-z0-9]{20,}"

# Alternative: Use gitleaks (install first: brew install gitleaks)
gitleaks detect --source . --verbose

# Alternative: Use truffleHog (install first: pip install truffleHog)
trufflehog filesystem .
```

**If secrets found in history**:
```bash
# Option 1: Use git filter-repo (recommended)
pip install git-filter-repo
git filter-repo --path .env --invert-paths --force

# Option 2: Use BFG Repo-Cleaner
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

### ✅ Step 4: Verify .env.template is Safe

```bash
# Check template has NO real secrets
cat .env.template | grep -iE "AIzaSy|[A-Za-z0-9]{30,}"
# Expected output: (empty - only placeholders like "your_gemini_api_key_here")
```

### ✅ Step 5: Install Pre-commit Hooks

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks from .pre-commit-config.yaml
pre-commit install

# Initialize secrets baseline (marks known false positives)
pip install detect-secrets
detect-secrets scan > .secrets.baseline

# Test hooks on all files
pre-commit run --all-files
```

### ✅ Step 6: Review Staged Files

```bash
# See what will be committed
git status
git diff --cached

# Check for sensitive patterns in staged files
git diff --cached | grep -iE "api_key|token|secret|password|AIzaSy"
# Expected output: (empty or only documentation/placeholders)
```

## 📋 Repository Health Check

### Files That MUST Exist

- [x] `.gitignore` - Comprehensive patterns (logs, PIDs, .env, IDE files)
- [x] `.env.template` - Safe placeholder values
- [x] `SECURITY.md` - Vulnerability reporting and best practices
- [x] `.pre-commit-config.yaml` - Automated security hooks
- [x] `README.md` - Setup instructions (see Step 7 below)

### Files That MUST NOT Exist in Git

- [ ] `.env` - Contains real API keys
- [ ] `backend.log` - May contain sensitive data
- [ ] `backend.pid` - Runtime file
- [ ] `__pycache__/` - Python bytecode
- [ ] `.vscode/` - IDE settings (may contain paths)

**Verify**:
```bash
git ls-files | grep -E "\.env$|backend\.log|backend\.pid|__pycache__|\.vscode"
# Expected output: (empty)
```

## 🔒 Step 7: Update README Security Section

Add this section to `README.md` after installation steps:

```markdown
## Security

**IMPORTANT**: This application requires sensitive API credentials.

### First-Time Setup

1. Copy the template file:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # Get your key at: https://aistudio.google.com/app/apikey
   GOOGLE_API_KEY="your_actual_key_here"
   ```

3. **NEVER commit `.env` to version control**:
   ```bash
   # Verify it's gitignored
   git check-ignore .env  # Should output: .env
   ```

### API Key Management

- **Google Gemini API**: Free tier at https://aistudio.google.com/app/apikey
- **Rotate keys** every 90 days
- **Revoke immediately** if exposed in commits/logs
- Store keys in password manager, not in code

See `SECURITY.md` for vulnerability reporting and best practices.
```

## 🚀 Final Pre-Push Commands

```bash
# 1. Stage security files
git add .gitignore .env.template .pre-commit-config.yaml SECURITY.md SECURITY_CHECKLIST.md

# 2. Verify NO secrets in staged files
pre-commit run detect-secrets --all-files

# 3. Verify .env is NOT staged
git status | grep ".env"
# Should only show: .env.template (NOT .env)

# 4. Make first commit
git commit -m "chore: add comprehensive security configuration

- Expand .gitignore with logs, PIDs, secrets, IDE files
- Add pre-commit hooks with detect-secrets
- Add SECURITY.md with vulnerability reporting
- Add .env.template with safe placeholders
- Add security checklist for contributors"

# 5. Create GitHub repository (if not exists)
# Visit: https://github.com/new

# 6. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## 🎯 Post-Push Verification

### Enable GitHub Security Features

1. **Secret Scanning** (free for public repos):
   - Settings → Security → Code security and analysis
   - Enable "Secret scanning"

2. **Dependabot Alerts**:
   - Enable "Dependabot alerts"
   - Enable "Dependabot security updates"

3. **Branch Protection** (optional):
   - Settings → Branches → Add rule for `main`
   - Require status checks (pre-commit hooks via GitHub Actions)

### Test Clone on Fresh Machine

```bash
# Simulate new contributor
cd /tmp
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Verify .env does NOT exist
ls -la .env
# Expected: No such file or directory

# Verify .env.template exists with placeholders
cat .env.template
```

## 📞 Emergency Contact

If you accidentally push a secret:

1. **Immediately revoke** the credential at its source
2. **Contact repository admin**: [your-email@example.com]
3. **Force push** after history cleanup (if needed)
4. **Report in SECURITY.md** following vulnerability process

---

**Status**: ⚠️ **Run this checklist BEFORE first push to GitHub**

Last updated: 2025-01-XX
