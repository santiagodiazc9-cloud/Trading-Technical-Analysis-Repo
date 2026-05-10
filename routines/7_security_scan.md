# Routine: Security Scan
**Schedule**: Saturday 11:00 AM ET (market closed, low-pressure window)

## Purpose
Catch vulnerabilities in the trading agent's Python dependencies and code. The agent handles real API keys (Alpaca, Anthropic, Discord bot token) and places orders against a brokerage account. A compromised dependency or leaked secret is a serious incident.

This routine runs RuFlo's security tooling and reports findings. **It does not auto-fix.** Findings → Discord `#risk-alerts` (CRITICAL/HIGH) and `#daily-brief` (medium/low summary) → user reviews and decides.

## Instructions

### 0. Ruflo health check (fail loudly, not silently)
This routine writes CRITICAL/HIGH security findings to RuFlo's `trading-security` namespace so next week's scan can detect regressions. If RuFlo is silently broken, the security baseline doesn't accumulate.

1. Call `mcp__ruflo__system_health`. Expected: healthy/ok.
2. Call `mcp__ruflo__system_info`. Expected: version `3.7.0-alpha.20` (pinned in `.mcp.json`).
3. On failure or version drift:
   ```bash
   python3 scripts/notify.py alert high ruflo 'Ruflo MCP unhealthy or version drift during security scan — findings will not be indexed for regression tracking. Expected v3.7.0-alpha.20.'
   ```
   Continue the scan; findings still get posted to Discord. Re-run scan after RuFlo is restored if you want findings indexed.

### 1. Load Memory
Read `memory/discord_config.json` for channel webhook URLs (used by `notify.py`).

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

### 6. Publish findings to Discord

**A. All clear case** — silent post to `#daily-brief`:

```bash
python3 scripts/notify.py brief '🛡️ Security Scan — YYYY-MM-DD — All clear' '<deps scanned, files reviewed, sub-agent confidence>'
```

**B. Findings case** — one alert per CRITICAL/HIGH to `#risk-alerts` (high+ tags @here):

```bash
python3 scripts/notify.py alert critical security '<short title>: <file:line> — <why dangerous> — <suggested fix>'
python3 scripts/notify.py alert high     security '<short title>: <file:line> — <why dangerous> — <suggested fix>'
```

Plus one summary brief to `#daily-brief` with the full medium/low list:

```bash
python3 scripts/notify.py brief '🛡️ Security Scan — YYYY-MM-DD — <N> medium/low findings' '<bulleted list, each with file:line + fix>'
```

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
- Link to Discord posts (channel + message timestamps)

**This routine NEVER modifies code. Findings are reported, not fixed.** Fixing happens in a separate manual session after Santiago reviews the findings.
