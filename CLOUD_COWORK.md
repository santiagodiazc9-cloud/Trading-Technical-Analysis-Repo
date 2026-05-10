# Cloud Cowork — Mac-off operation

## The agent owns git

The trading agent is responsible for its own git operations. It commits the
memory it writes, pushes to `origin/main` so cloud routines and the human
can see the same state, and pulls before the next routine starts so it has
the latest context.

The agent never commits code. Only files it produced as part of normal
trading work get staged. Code is changed by humans (or `/ultrareview`-style
reviews), then committed by humans.

### Single entrypoint
All agent-initiated git ops go through `scripts/git_sync.py`. Routines and
ad-hoc agent sessions invoke it like any other tool:

```bash
python3 scripts/git_sync.py status                  # check sync state
python3 scripts/git_sync.py pull                    # fast-forward only
python3 scripts/git_sync.py commit "<message>"      # stage + secret-scan + commit
python3 scripts/git_sync.py push                    # push current branch
python3 scripts/git_sync.py sync "<message>"        # pull → commit → push
python3 scripts/git_sync.py guard <path>            # ad-hoc secret scan
```

Every subcommand emits JSON on stdout so a routine can `json.load` the
result and branch on success/failure without parsing prose.

### What the agent commits

Only paths under these prefixes are eligible:

- `memory/` — JSON state + markdown logs (the source of truth for the agent)
- `journal/` — daily journal entries
- `docs/` — ADRs and write-ups
- `inbox/` — Obsidian inbox notes
- `templates/` — note templates
- Root-level docs: `CLOUD_COWORK.md`, `DISCORD.md`, `README.md`, `RUN_ROUTINES.md`,
  `SETUP.md`, `TRADING_GUIDE.md`, `VAULT.md`

`CLAUDE.md` is intentionally **not** in that list — the rulebook only
changes when a human approves it.

Anything outside these prefixes (including `scripts/`, `.github/`, plist
files, dotfiles, `requirements.txt`) is silently skipped. The JSON output
lists those under `skipped` so a routine can flag them in the daily brief.

### Safety rules (enforced in code, not vibes)

1. **No secrets, ever.** Every staged file is scanned for Anthropic, AWS,
   Slack, Discord, Alpaca, and PEM-style private keys before the commit
   lands. A hit aborts the commit and resets the index.
2. **Hard-coded blocklist** in `git_sync.py` rejects `.env`, `*.env.*`,
   `memory/discord_config.json`, and `memory/clickup_config.json` even if
   they accidentally slipped past `.gitignore`.
3. **Main branch only.** Commits and pulls refuse to run on any other
   branch unless `--allow-branch` is passed (intended for human-driven
   maintenance, not routines).
4. **No force, no amend, no `--no-verify`.** Not supported by the script.
   A routine cannot rewrite history; the worst it can do is land an
   unwanted commit that humans can revert.
5. **Pull is fast-forward only.** No merge commits from the agent. If
   `origin/main` has diverged, the script bails and the routine logs an
   alert to `#risk-alerts` for human resolution.
6. **Push refuses on detached HEAD.**

### When the agent commits

Cadence is intentionally low-frequency to keep history readable:

| Trigger | What lands |
|---------|-----------|
| End of each trading routine (pre-market, market-open, midday, EOD) | `memory/`, `journal/` updates from that routine — one commit per routine |
| Weekly review | All weekly summary edits, new ADR if rules changed |
| Discord dispatcher (15-min) | Only commits if `memory/learnings.md` or `memory/open_positions.md` materially changed during dispatch — most dispatches are no-ops |
| Security scan (Saturday) | Findings written to `docs/security/` if any |

If nothing material changed, the script reports `committed: false` and
exits 0. Routines treat that as a normal outcome — silence is fine.

### Commit message convention

`routine(<name>): <YYYY-MM-DD HH:MM TZ> — <one-line summary>`

Examples:

- `routine(pre_market): 2026-05-12 08:05 ET — 3 setups proposed`
- `routine(end_of_day): 2026-05-12 15:50 ET — closed AMD swing, journal updated`
- `routine(weekly_review): 2026-05-16 16:35 ET — ADR-007 tightened sector cap`

This makes `git log --oneline` a readable trading diary.

## Routine integration

Routines that touch persistent state end with these steps:

1. Run `python3 scripts/dashboard.py` to regenerate `Dashboard.md`
   (which is gitignored — it's just a local mirror).
2. Run `python3 scripts/notify.py dashboard` to post the dashboard to
   Discord `#daily-brief`.
3. Run `python3 scripts/git_sync.py sync "routine(<name>): <stamp> — <summary>"`.
4. Parse the JSON result. If `ok: false`, post the error to `#risk-alerts`
   so the human can intervene; do NOT retry blindly.

The legacy auto-commit hook in `scripts/run_claude_routine.sh` (gated on
`TRADING_GIT_AUTOCOMMIT=1`) is preserved as a belt-and-suspenders fallback
for when an agent forgets to call `git_sync.py` at the end of a routine.
Both paths converge on the same secret-scan logic.

## Local vs cloud — same git protocol

Whether the routine runs on the local Mac via launchd or in Anthropic
Cloud Routines / GitHub Actions, the git protocol is identical:

- Pull `origin/main` at the start (cloud routines start from a fresh clone
  every time, so this is implicit there)
- Run the routine
- Sync (`git_sync.py sync`) at the end

This is what makes the agent stateless across surfaces: state lives in git,
not on a particular machine.

## Secret management across surfaces

`.env` and `memory/discord_config.json` never go to git. The cloud
equivalents:

- **Claude Cloud Routines**: paste `.env` contents into the routine's
  environment configuration in the desktop app. Each routine gets its own
  scoped env.
- **GitHub Actions**: store as encrypted Actions secrets at the repo
  level, referenced via `${{ secrets.* }}` in the workflow YAML.

Verify with: `git ls-files | grep -i env` — should be empty.

## Activation checklist

Local mode is the **active** surface today. GitHub Actions is scaffolded
but **parked** — workflow files exist with cron schedules commented out
and a `TRADING_GHA_ENABLED` repo-variable kill-switch. Reactivate later:

```text
1. Uncomment the `schedule:` block in both workflow files:
     .github/workflows/trading-dispatch.yml
     .github/workflows/trading-security.yml

2. In GitHub, Settings → Secrets and variables → Actions:
     Secrets: ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_BASE_URL (optional),
              ANTHROPIC_API_KEY, DISCORD_CONFIG_JSON
     Variable: TRADING_GHA_ENABLED = true

3. Verify clean working tree:
     python3 scripts/git_sync.py status   # ahead: 0, behind: 0, dirty: []

4. Test fire: Actions tab → trading-dispatch → "Run workflow" with
   routine input `routines/6_discord_dispatcher.md`. Confirm a
   `routine(gha): …` commit lands on origin/main.

5. Let the scheduled cron fire naturally on next trading day.

6. (optional) Disable local launchd once GHA proves stable:
     launchctl unload -w ~/Library/LaunchAgents/com.claude.tradingagent.routines.plist
     launchctl unload -w ~/Library/LaunchAgents/com.claude.tradingagent.polling.plist
```

See `.github/SECRETS.md` for the full secret/variable reference and
cost notes.

## Rollback

If cloud cowork misbehaves:

1. Re-enable local launchd: `launchctl load -w ~/Library/LaunchAgents/com.claude.tradingagent.routines.plist`
2. Disable the cloud routines (Claude desktop app or GitHub Actions UI)
3. Local mode resumes immediately. Memory state in git is unchanged.

## Verifying end-to-end

After cutover, leave the Mac OFF for one full trading day. Verify:

- Discord `#daily-brief` received Pre-Market Brief at 8:00 AM ET
- Discord `#daily-brief` received Market Open Execution at 9:35 AM ET
- Discord `#daily-brief` received Midday Scan at 12:30 PM ET
- Discord `#daily-brief` received EOD Review at 3:45 PM ET
- Pinned dashboard message in `#daily-brief` shows updated timestamps
- `git log --oneline -10` shows one `routine(...)` commit per routine

If any are missing, investigate cloud schedule, secret config, and the
`git_sync.py` step.

## Decision (2026-05-09 → 2026-05-10): split agent-side and repo-side

The cloud cowork architecture splits responsibilities across two surfaces:

### Claude Cloud Routines (agent-side)

Owns work that requires Claude's reasoning loop — analysis, decisions,
approvals, write-ups.

- All 5 trading routines (pre-market, market open, midday, EOD, weekly review)
- Discord dispatcher routine (drains queue files, answers `/ask`)
- Anywhere a sub-agent swarm is spawned
- ADR authoring during weekly review
- **Git commits/pushes for memory + journal + docs (via `scripts/git_sync.py`)**

**Why here**: each of these calls back into the Claude API and uses
memory tools. They're agentic, not deterministic — and the git operation
is part of the agent's job, not a separate runner's.

### GitHub Actions (repo-side)

Owns deterministic automation that must run independently of any Claude
session. Survives if Anthropic is down. Provides an audit trail in plain YAML.

- **Secret-leak verification** on every push (independent of `git_sync.py`'s
  pre-commit scan — defense in depth)
- Daily cron job: snapshot `memory/` + `journal/` to a separate "history"
  branch (immutable timeline of memory state)
- Pre-merge gate on `main`: lint, validate JSON schemas, run the import
  smoke test (`python3 -c "import scripts.alpaca_client; import scripts.research"`)
- Saturday security scan: also runs as a GitHub Action so the codebase is
  checked even if local Mac and Anthropic cloud are both quiet
- Optional: dependabot or equivalent on `requirements.txt`

**Why here**: deterministic, reproducible, platform-independent. No Claude
reasoning needed — just reliable runners.

### Boundary rule

If a job needs Claude to make a judgment call → Cloud Routines.
If a job is "always do X when Y" → GitHub Actions.

Trading routines that include reasoning AND deterministic post-processing
split the same way: the agent half runs in Cloud Routines (and commits its
own memory via `git_sync.py`), the validation half runs as a GitHub Action
triggered by the resulting push.
