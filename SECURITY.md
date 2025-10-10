# Security Policy

## Overview

MCP LLM Assistant handles sensitive API credentials and integrates with external services. This document outlines security practices and vulnerability reporting procedures.

## Supported Versions

Currently supported versions for security updates:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Security Best Practices

### 1. API Key Management

**CRITICAL**: Never commit API keys or tokens to version control.

- **Environment Variables**: All secrets must be in `.env` file (gitignored)
- **Template File**: `.env.template` shows structure without real values
- **Key Storage**: Store keys in password managers (1Password, Bitwarden, etc.)
- **Key Rotation**: Rotate API keys every 90 days or immediately if exposed

### 2. Before First Commit

Run these checks to prevent credential leaks:

```bash
# Verify .env is gitignored
git check-ignore .env  # Should output: .env

# Check for secrets in staged files
git diff --cached | grep -iE "api_key|token|secret|password"

# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install
```

### 3. Google Gemini API Keys

- **Generate at**: https://aistudio.google.com/app/apikey
- **Free tier limit**: 15 requests/minute
- **Key format**: `AIzaSy...` (39 characters)
- **Revoke immediately if exposed**: Visit API key dashboard → Delete key → Generate new

### 4. Docker MCP Server Credentials

Required environment variables for MCP servers:

- `NOTION_TOKEN` - Notion integration token (starts with `secret_`)
- `GITHUB_TOKEN` - GitHub Personal Access Token (classic or fine-grained)
- `PERPLEXITY_API_KEY` - Perplexity API key (optional)

**Setup**: Configure these in Docker MCP Gateway settings, NOT in this repository's `.env`.

### 5. Pre-commit Security Hooks

The repository uses `detect-secrets` to prevent accidental credential commits:

```bash
# Initialize baseline (first time only)
detect-secrets scan > .secrets.baseline

# Audit existing secrets
detect-secrets audit .secrets.baseline

# Pre-commit will automatically scan on every commit
```

### 6. Code Review Checklist

Before pushing code, verify:

- [ ] No hardcoded API keys in code
- [ ] `.env` file not in git history
- [ ] `.env.template` has placeholder values only
- [ ] No sensitive data in logs or error messages
- [ ] Authentication failures don't leak credentials
- [ ] Secrets not in function call arguments (visible in logs)

## Vulnerability Reporting

### Reporting a Vulnerability

If you discover a security vulnerability, please email: **[your-email@example.com]**

**Do NOT** open a public GitHub issue for security vulnerabilities.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if available)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix timeline**: Varies by severity (critical: 7 days, high: 30 days, medium: 90 days)

## Security Features

### Current Implementation

1. **Graceful Degradation**: Missing API keys print warnings but don't expose secrets
2. **Timeout Protection**: 30s timeout on subprocess calls prevents hanging
3. **Singleton Pattern**: Service instances prevent accidental multi-initialization
4. **Error String Returns**: Services return error strings (not exceptions) to prevent stack trace leaks
5. **Environment Validation**: Config verification at startup checks for required keys without logging values

### Future Enhancements

- [ ] Secrets encryption at rest (using Keyring library)
- [ ] API key prefix validation before use
- [ ] Rate limit tracking to prevent abuse
- [ ] Audit logging for all MCP server calls
- [ ] HTTPS enforcement for production deployments

## Incident Response

If credentials are accidentally committed:

1. **Immediately revoke** the exposed key/token
2. **Generate new credentials** from provider
3. **Update `.env` locally** with new values
4. **Scan git history** for exposed secrets:
   ```bash
   git log -p | grep -iE "api_key|token|secret|password"
   ```
5. **Rewrite git history** if needed (use `git filter-repo` or BFG Repo-Cleaner)
6. **Force push** after history cleanup (coordinate with team)

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Google Cloud API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

## Contact

For security questions or concerns: **[your-email@example.com]**

Last updated: 2025-01-XX
