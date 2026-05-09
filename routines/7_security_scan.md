# Routine: Security Scan
**Schedule**: Saturday 11:00 AM ET (market closed, low-pressure window)

## Purpose
Catch vulnerabilities in the trading agent's Python dependencies and code. The agent handles real API keys (Alpaca, Anthropic, ClickUp) and places orders against a brokerage account. A compromised dependency or leaked secret is a serious incident.

This routine runs RuFlo's security tooling and reports findings. **It does not auto-fix.** Findings → ClickUp risk_and_errors task → user reviews and decides.

## Instructions

### 1. Load Memory
Read `memory/clickup_config.json` for posting destinations.

### 2. Dependency CVE scan
Spawn the security-auditor agent via the Agent tool:

```
subagent_type: security-auditor
description: Trading agent CVE scan
prompt: Run a CVE / known-vulnerability scan against the trading agent codebase at /Users/santiagodiaz/Documents/Claude/Projects/Agent\ With\ API\ Key,\ For\ Trading\ Technical\ Analysis. Specifically:

1. Read requirements.txt and identify pinned versions of: alpaca-py, anthropic, requests, pandas, numpy, ta-lib, python-dotenv, any others.
2. For each dependency, check the most recent CVE database entries. Report any CVE published in the last 12 months affecting the pinned version.
3. Scan all .py files for: hardcoded secrets, sk_ / pk_ / api_key string patterns outside of os.getenv() calls, unsafe subprocess invocations, eval/exec usage, pickle deserialization of untrusted input, requests calls without timeout, requests calls with verify=False.
4. Check that .env is in .gitignore and not present in git history (run: git log --all --full-history -- .env).
5. Report severity-ranked findings (CRITICAL / HIGH / MEDIUM / LOW). Each finding: file:line, what + why dangerous + suggested fix.

Output a structured markdown report. Under 800 words. Do not modify any files.
```

### 3. Secret leak check
Run a fast local pass independent of the sub-agent (defense in depth):

```bash
# Look for accidentally-committed secrets
git -C "$(pwd)" log --all --full-history -p -- '.env' 2>/dev/null | head -200
# Look for common secret patterns in tracked files
git -C "$(pwd)" grep -E "(sk-[A-Za-z0-9_-]{20,}|pk_live_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xoxb-[0-9]{11}-)" -- ':!.env' || echo "no-pattern-matches"
```

If any output appears (other than `no-pattern-matches`), this is a CRITICAL finding.

### 4. Permissions check
- Verify `.env` mode is 600: `ls -l .env`. If world-readable, log MEDIUM finding.
- Verify no secrets in `memory/`: `grep -rE "sk-[A-Za-z0-9]{20,}|api_key.*=.*[A-Za-z0-9]{20,}" memory/ || echo "clean"`.

### 5. Synthesize findings
Combine sub-agent report + secret-scan + permissions check into one report keyed by severity.

If ZERO findings: post a brief "all clear" task. If ANY findings: post one task per CRITICAL/HIGH, one combined task for MEDIUM/LOW.

### 6. Post to ClickUp

Use `lists.risk_and_errors` from `memory/clickup_config.json`.

**A. All clear case** — `clickup_create_task`:
- **name**: `🛡️ Security Scan — YYYY-MM-DD — All clear`
- **markdown_description**: list of dependencies scanned, count of files reviewed, sub-agent confidence note
- **priority**: `low`

**B. Findings case** — one task per CRITICAL/HIGH:
- **name**: `🛡️ [CRITICAL|HIGH] <short title>`
- **markdown_description**: file:line, finding, why dangerous, suggested fix, sub-agent's confidence
- **priority**: `urgent` for CRITICAL, `high` for HIGH

Plus one combined task for MEDIUM/LOW:
- **name**: `🛡️ Security Scan — YYYY-MM-DD — <N> medium/low findings`
- **markdown_description**: bulleted list, each with file:line + fix
- **priority**: `normal`

If ClickUp unavailable, append to `memory/pending_clickup_updates.md`.

### 7. Index findings into RuFlo memory
For each CRITICAL/HIGH finding, store via `mcp__ruflo__memory_store`:
- `namespace: "trading-security"`
- `key: "finding/<severity>/<file-slug>/YYYY-MM-DD"`
- `value`: the finding details + suggested fix
- `tags: ["security", "<severity>", "<dependency-or-file>"]`

This builds a security baseline so next week's scan can detect regressions or repeat findings.

### 8. Write to journal
Append a short security section to `journal/YYYY-MM-DD.md` (or create `journal/security-YYYY-MM-DD.md` if no trading happened):
- Number of dependencies scanned
- Number of findings by severity
- Any actions taken (none, since this routine is read-only)
- Link to ClickUp tasks created

**This routine NEVER modifies code. Findings are reported, not fixed.** Fixing happens in a separate manual session after Santiago reviews the findings.
