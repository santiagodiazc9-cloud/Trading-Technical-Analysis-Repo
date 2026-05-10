# GitHub Actions secrets & variables

The trading workflows are **disabled by default**. To enable cloud-side
operation:

1. Configure secrets and the activation variable below
2. Verify locally with `workflow_dispatch` runs
3. Optionally disable the local launchd jobs (Mac-side) to avoid duplicate
   runs

## Required secrets

Set under **Settings → Secrets and variables → Actions → Secrets** (Repository secrets).

| Name | Purpose |
|---|---|
| `ALPACA_API_KEY` | Alpaca paper-trading key id (starts with `PK…`). Recreate from your Alpaca dashboard if rotated. |
| `ALPACA_API_SECRET` | Alpaca paper-trading secret. Paired with the key above. |
| `ALPACA_BASE_URL` | Optional. Defaults to `https://paper-api.alpaca.markets`. Override only for staging. |
| `ANTHROPIC_API_KEY` | Anthropic API key the Claude Code CLI uses inside the workflow. **Note**: this is the API key, not a Claude Code subscription. Routines billed per token. |
| `DISCORD_CONFIG_JSON` | Full JSON content of `memory/discord_config.example.json` with your real webhook URLs and bot token filled in. The workflow writes this to `memory/discord_config.json` at runtime. |

To paste `DISCORD_CONFIG_JSON`, take the full contents of your local
`memory/discord_config.json` (the gitignored file) and paste verbatim into
the secret value field. Multiline JSON is fine.

## Required variable

Set under **Settings → Secrets and variables → Actions → Variables**.

| Name | Value |
|---|---|
| `TRADING_GHA_ENABLED` | `true` — flips the kill-switch. Without this, every workflow exits at the first guard step. |

## Activation checklist

```text
[ ] All 5 secrets above set
[ ] TRADING_GHA_ENABLED = true
[ ] Run `trading-dispatch` via "Run workflow" with routine override
    `routines/6_discord_dispatcher.md` — should succeed and produce a
    `routine(gha): …` commit.
[ ] Inspect git history: latest commit author = "trading-agent" with the
    GitHub Actions runner having pushed via GITHUB_TOKEN.
[ ] Wait for the next scheduled cron tick and verify run logs in the
    Actions tab.
[ ] Leave Mac off for one full trading day; verify Discord receives the
    pre-market / market-open / midday / EOD posts.
[ ] Once stable, decide whether to keep launchd running in parallel or
    disable it:
        launchctl unload -w ~/Library/LaunchAgents/com.claude.tradingagent.routines.plist
        launchctl unload -w ~/Library/LaunchAgents/com.claude.tradingagent.polling.plist
```

## Cost notes

- GitHub Actions free tier on private repos: 2000 min/mo. Trading dispatch
  cron fires every 15 min during a wide UTC window Mon-Fri. Most ticks
  exit fast (no routine matched, or dispatcher early-exits). Expected
  monthly usage: well under quota.
- Anthropic API: each `claude -p` call inside a routine consumes tokens.
  Set a usage cap in the Anthropic console if you want a hard ceiling.

## Defense in depth

`git_sync.py` runs a secret scan before every commit (Anthropic, AWS,
Slack, Discord, Alpaca, PEM patterns). Even if a secret leaks into a
`memory/` file by mistake, the commit aborts. The workflow logs the
JSON failure so you can investigate.

## Rotating secrets

If a key rotates, update the GitHub secret value — no code change
needed. The workflow rebuilds `.env` from secrets on every run.
