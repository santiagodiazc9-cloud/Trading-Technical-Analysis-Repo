# Cloud Cowork — Mac-off operation

## Today's mode (local-only)

The trading agent currently runs on local launchd schedules. This means routines fire ONLY while your Mac is on and the network is reachable. If you close the Mac for the weekend, no routines fire (this is documented in `TRADING_GUIDE.md` Part 3.1).

**Memory persistence today**: Files in `memory/` and `journal/` are written to disk locally. They survive across Mac reboots, but are NOT pushed to git automatically — yet.

## Cloud cowork — what changes

In cloud cowork mode:
- Routines run on Anthropic's infrastructure (Claude Code Cloud Routines)
- Memory is committed to git after every routine and pushed to your remote
- The Mac can be off, asleep, in another country — routines still fire
- The next routine pulls latest memory from git, runs, commits, pushes

This is the design implied by your CLAUDE.md ("Stateless execution: every session must start by reading memory files and end by writing them"). Local mode tolerates a stateful Mac; cloud mode forces real statelessness.

## What's already wired (this session)

1. **Auto-commit hook** in `scripts/run_claude_routine.sh` — after each routine, if env var `TRADING_GIT_AUTOCOMMIT=1` is set, the wrapper:
   - `git add memory/ journal/ docs/adr/` (never code, never `.env`)
   - `git commit -m "routine(<name>): <timestamp>"` if anything changed
   - `git push origin HEAD` if a remote is configured
   - Failures are logged but never halt the routine
2. **Polling routine step 11** — same auto-commit pattern, gated on the same env var
3. **`.gitignore`** updated to exclude `.claude-flow/`, `.swarm/`, all `*.log` files
4. **Git remote** verified: `origin https://github.com/santiagodiazc9-cloud/Trading-Technical-Analysis-Repo`

## To activate cloud cowork — manual steps

### Step 1: Enable auto-commit locally first (smoke test)
```bash
# Add to your shell rc (~/.zshrc):
export TRADING_GIT_AUTOCOMMIT=1
```
Then trigger any routine manually. After it finishes, run `git log -1` to confirm a new commit landed. If the push succeeded, your remote should reflect it. **Do this for at least one full week of routines to verify stability before flipping to cloud.**

### Step 2: Move secrets to a secure store
The `.env` file holds your Alpaca, Anthropic, and ClickUp keys. Cloud routines can't read your local `.env`. Options:

- **Anthropic Cloud Routines secret store** (preferred when supported) — paste `.env` contents into the routine's environment configuration in the Claude desktop app.
- **GitHub repo encrypted Actions secrets** — if you migrate to GitHub Actions instead of Claude cloud routines, configure secrets at the repo level.

**Never commit `.env` to git.** The `.gitignore` already protects against this; verify with `git ls-files | grep -i env`.

### Step 3: Switch the schedule

**Option A — Claude Code Cloud Routines (matches TRADING_GUIDE.md Part 8 mention)**
1. Open the Claude desktop app → Routines sidebar
2. For each of the 7 routines (5 trading + polling + security scan), create a Cloud Routine that:
   - Pulls the repo: `git pull origin main`
   - Runs: `cat routines/N_<name>.md | claude -p` (or via the routine wrapper if Anthropic cloud allows shell)
3. Set the schedule (8:00 AM ET pre-market, etc.) in Anthropic's UI, not launchd
4. Disable the local launchd plist: `launchctl unload ~/Library/LaunchAgents/com.claude.tradingagent.routines.plist`

**Option B — GitHub Actions** (more transparent, more YAML)
1. Create `.github/workflows/trading-routines.yml` with cron triggers matching the existing schedule
2. Use `secrets.ALPACA_KEY`, `secrets.ANTHROPIC_KEY`, `secrets.CLICKUP_KEY` in env
3. Run the routine wrapper inside the Action
4. Disable local launchd

### Step 4: Verify end-to-end
After cutover, leave the Mac OFF for one full trading day. Verify:
- ClickUp received Pre-Market Brief at 8:00 AM ET
- ClickUp received Market Open Execution post at 9:35 AM ET
- ClickUp received Midday Scan at 12:30 PM ET
- ClickUp received EOD Review at 3:45 PM ET
- Git remote shows commits for each routine

If any are missing, investigate the cloud schedule, secret config, and `git pull` step.

## Rollback

If cloud cowork misbehaves:
1. Re-enable local launchd: `launchctl load -w ~/Library/LaunchAgents/com.claude.tradingagent.routines.plist`
2. Disable the cloud routines (Claude desktop app or GitHub Actions UI)
3. Local mode resumes immediately.

## Why we're NOT activating it today

- Need at least 1 week of stable auto-commit-locally first to catch git-side surprises before adding cloud unknowns
- Need user-side action: configuring secrets in the cloud
- Need user authorization for the first push (this session has not committed or pushed anything yet)

## Single-command checklist to flip the switch (after local validation)

```bash
# 1. Enable auto-commit
echo 'export TRADING_GIT_AUTOCOMMIT=1' >> ~/.zshrc && source ~/.zshrc

# 2. Verify clean working tree (commit anything pending FIRST)
git status

# 3. Configure secrets in chosen cloud surface (manual UI step)

# 4. Schedule cloud routines (manual UI step)

# 5. Disable local launchd
launchctl unload ~/Library/LaunchAgents/com.claude.tradingagent.routines.plist
launchctl unload ~/Library/LaunchAgents/com.claude.tradingagent.polling.plist

# 6. Verify with Mac off — Step 4 above
```

## Decision (2026-05-09): Use BOTH

After review, the cloud cowork architecture splits responsibilities across two surfaces:

### Claude Cloud Routines (agent-side)
Owns work that requires Claude's reasoning loop — analysis, decisions, approvals, write-ups.

- All 5 trading routines (pre-market, market open, midday, EOD, weekly review)
- Polling routine (interprets ClickUp comments, drafts replies, updates memory)
- Anywhere a sub-agent swarm is spawned (RuFlo Phase 0 item 2)
- ADR authoring during weekly review

**Why here**: each of these calls back into the Claude API and uses memory tools. They're not stateless functions — they're agentic.

### GitHub Actions (repo-side)
Owns deterministic automation that must run independently of any Claude session. Survives if Anthropic is down. Provides an audit trail in plain YAML.

- Memory commit verification: every push triggers a check that `memory/` was updated and that no secrets leaked
- Daily cron job: snapshot `memory/` + `journal/` to a separate "history" branch (immutable timeline of memory state)
- Pre-merge gate on `main`: lint, validate `memory/clickup_config.json` schema, validate routine markdown front-matter, run `python3 -c "import scripts.alpaca_client; import scripts.research"` (smoke import test)
- Saturday security scan: also runs as a GitHub Action so the codebase is checked even if local Mac and Anthropic cloud are both quiet
- Optional: dependabot or equivalent on `requirements.txt`

**Why here**: these jobs benefit from being deterministic, reproducible, and platform-independent. They don't need Claude to think — they need a reliable runner.

### Boundary rule
If a job needs Claude to make a judgment call → Cloud Routines.
If a job is "always do X when Y" → GitHub Actions.

Trading routines that include reasoning AND deterministic post-processing (e.g., "agent decides, then push to git, then validate") split: the agent half runs in Cloud Routines, the validation half runs as a GitHub Action triggered by the resulting push.
