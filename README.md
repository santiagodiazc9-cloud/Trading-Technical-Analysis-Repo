# Trading Agent

An autonomous AI trading agent that researches the U.S. equity market, proposes trade setups, executes orders with explicit user approval, and journals every decision. Runs headlessly via `launchd` and GitHub Actions — controlled from a phone via Discord.

## Paper trading only

This agent is configured to use **Alpaca's paper-trading endpoint** (`paper-api.alpaca.markets`). `CLAUDE.md` explicitly forbids live trading. Do not point this at a live brokerage account without redesigning the risk-enforcement layer.

## What it does

- **Researches** the watchlist every morning — fetches bars, computes RSI / MACD / SMA / EMA / Bollinger / ATR / VWAP / StochRSI, scans for crossovers and squeezes, spawns parallel sub-agents for fundamentals, news, and sector momentum
- **Proposes** setups with full analysis (entry zone, stop, target, R:R, position size, confidence score 1–10, catalyst) pushed to Discord as cards with Approve / Deny buttons
- **Executes** orders only after explicit user approval — Discord button, slash command, or direct file edit
- **Manages** open positions throughout the day — tightens trailing stops as winners run, fires the hard `-7%` manual cut rule, closes day trades before EOD
- **Reflects** at EOD and weekly — journals decisions, surfaces patterns, asks reflective questions, writes ADRs when strategy rules change
- **Learns** from feedback — drop articles in `#knowledge-inbox`, post one-liners in `#feedback`; the dispatcher folds them into agent memory and the RuFlo vector store

## Architecture

```
              ┌──────────────────────────────┐
              │    YOU (Discord on phone)    │
              └──────────────────────────────┘
                         │ ▲
                         ▼ │
              ┌──────────────────────────────┐
              │   Discord Bot (always-on)    │  ← launchd KeepAlive
              └──────────────────────────────┘
                         │ writes / reads
                         ▼
              ┌──────────────────────────────┐
              │  memory/  +  Dashboard.md   │  ← source of truth (git)
              └──────────────────────────────┘
                │ ▲                    │ ▲
                ▼ │                    ▼ │
      ┌──────────────────┐  ┌──────────────────────┐
      │  Mac (primary)   │  │  GitHub Actions      │
      │  launchd cron    │  │  cloud failsafe      │
      │  4 jobs loaded   │  │  TRADING_GHA_ENABLED │
      └──────────────────┘  └──────────────────────┘
                │
                ▼
      ┌──────────────────────────────┐
      │   Alpaca Paper API          │
      └──────────────────────────────┘
```

**Key components:**

| Path | Purpose |
|------|---------|
| `scripts/` | Python tooling — Alpaca client, technical research, Discord bot, notifier, dashboard generator, git sync |
| `routines/` | Markdown prompts Claude Code executes on schedule. Each file = one self-contained set of agent instructions |
| `memory/` | File-based agent state — watchlist, strategy, learnings, open positions, trade log, queue files |
| `journal/` | Date-stamped daily decision logs |
| `docs/adr/` | Architecture Decision Records — every strategy rule change has one |
| `docs/guides/` | Operational guides (setup, Discord reference, trading operations, cloud cowork) |

**Scheduling (Mac — launchd):**

| Job | Schedule | What runs |
|-----|----------|-----------|
| `com.claude.tradingagent.routines` | 8:00, 9:35, 12:30, 15:45, Fri 16:30 ET | Pre-market → open → midday → EOD → weekly review |
| `com.claude.tradingagent.polling` | Every 15 min, Mon–Fri 08:00–16:30 ET | Discord dispatcher — drains `/run`, `/ask`, inbox, feedback queues |
| `com.claude.tradingagent.discordbot` | Always-on (KeepAlive) | Handles button clicks and slash commands |
| `com.claude.tradingagent.security` | Sat 11:00 AM | CVE scan, secret-leak check, permissions audit |

## Quick start

```bash
git clone <this-repo>
cd trading-agent
cp .env.example .env        # fill in ALPACA_API_KEY, ALPACA_SECRET_KEY, ANTHROPIC_API_KEY, DISCORD_BOT_TOKEN
pip3 install -r requirements.txt
python3 scripts/alpaca_client.py account    # smoke test Alpaca connection
```

For the full install (Discord bot, launchd plists, channel setup): see **[docs/guides/SETUP.md](docs/guides/SETUP.md)**.

To enable GitHub Actions cloud failsafe (Mac-off operation): see **[.github/SECRETS.md](.github/SECRETS.md)** and **[docs/guides/CLOUD_COWORK.md](docs/guides/CLOUD_COWORK.md)**.

## Documentation

| Doc | What it's for |
|-----|---------------|
| **[CLAUDE.md](CLAUDE.md)** | Agent persona, hard risk rules, strategy framework, decision checklist. Loaded as system context for every routine. |
| **[docs/guides/SETUP.md](docs/guides/SETUP.md)** | First-time install — Python, Alpaca, Discord bot, launchd, MCP servers |
| **[docs/guides/DISCORD.md](docs/guides/DISCORD.md)** | The 7 channels, 14 slash commands, approval flow, dispatcher loop |
| **[docs/guides/TRADING_GUIDE.md](docs/guides/TRADING_GUIDE.md)** | Day-to-day operations from the user's perspective — approve, deny, pause, train, query |
| **[docs/guides/RUN_ROUTINES.md](docs/guides/RUN_ROUTINES.md)** | Manual routine triggers via VS Code or Discord |
| **[docs/guides/VAULT.md](docs/guides/VAULT.md)** | Obsidian vault conventions (this repo doubles as a knowledge vault) |
| **[docs/guides/CLOUD_COWORK.md](docs/guides/CLOUD_COWORK.md)** | Mac-off operation via GitHub Actions — activation checklist and git protocol |
| **[docs/adr/README.md](docs/adr/README.md)** | Architecture Decision Records index |

## Hard risk rules

- **Paper only.** Never live.
- **Max 5 open positions** at any time
- **Max 20% of portfolio per position** (cap $20,000 absolute)
- **Max 3 new trades per week** (closes don't count)
- **-7% hard cut** — any position at or below -7% unrealized P&L gets closed immediately, no exceptions
- **Real GTC trailing stops** placed on Alpaca immediately after every fill (not a note in memory)
- **Stop tightens** to 7% trail at +15% gain, 5% trail at +20% gain
- **75–85% capital deployed** when active
- **Daily loss cap -2%** → stop trading for the day
- **Sector blocklist** after 2 consecutive losses in a sector (5-day cooldown)
- **PDT-aware** — sub-$25k accounts limited to 3 day trades per 5 rolling business days
- **No options, no crypto, no margin** — equities only
- **Approval required** before every entry — no exceptions

## Project status

| Phase | What | Status |
|-------|------|--------|
| 1 | Discord bot, slash commands, dashboard, channel webhooks, routines wiring | Done |
| 2 | Discord dispatcher replaces ClickUp polling; bot listeners for `#knowledge-inbox` and `#feedback` | Done |
| 3 | ClickUp writes stripped from all routines; ClickUp now read-only archive | Done |
| 4 | ClickUp emergency-fallback files deleted; stable on Discord for one full trading week | Done |
| 5 | GitHub Actions cloud failsafe scaffolded; hybrid Mac-primary / GHA-backup with lockfile guard | Done |
| 6 | Full Mac-off operation — enable `TRADING_GHA_ENABLED=true` in GitHub + cloud Discord bot deploy | In progress |

**Active surfaces:** Discord (primary UI), Alpaca Paper (broker), Mac launchd (primary scheduler), GitHub Actions (cloud failsafe), RuFlo MCP (`3.7.0-alpha.20`).

**Archived surfaces:** ClickUp (read-only; see git history pre-`a201388`).

## License

MIT. Fork freely. No warranties — this is a paper-trading research project, not financial advice.
